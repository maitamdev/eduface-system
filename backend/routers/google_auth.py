import re
import secrets
from datetime import datetime, timezone
from typing import Optional

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, Field
from pymongo.errors import DuplicateKeyError
from starlette.concurrency import run_in_threadpool

from core.auth import create_access_token, hash_password, require_admin
from core.database import get_db
from core.google_identity import (
    google_configuration,
    require_google_configuration,
    verify_google_access_token,
    verify_google_id_token,
)
from core.rate_limit import limiter
from core.schemas import TokenResponse

router = APIRouter()


class GoogleExchange(BaseModel):
    access_token: Optional[str] = Field(default=None, max_length=8192)
    id_token: Optional[str] = Field(default=None, max_length=24000)


class GoogleLink(BaseModel):
    email: Optional[str] = Field(default=None, max_length=254)


@router.get("/google/config")
async def get_google_config():
    return google_configuration()


@router.post("/google", response_model=TokenResponse)
@limiter.limit("15/minute")
async def exchange_google_identity(
    request: Request,
    body: GoogleExchange,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    config = require_google_configuration()
    if body.id_token:
        claims = await run_in_threadpool(verify_google_id_token, body.id_token, config)
    elif body.access_token:
        claims = await run_in_threadpool(verify_google_access_token, body.access_token, config)
    else:
        raise HTTPException(400, "Missing Google token.")

    email = claims["email"].strip().lower()
    display_name = (claims.get("name") or email.split("@")[0]).strip()
    escaped_email = re.escape(email)

    # Only a deliberately linked, verified identity grants access to an existing account.
    user = await db.users.find_one({"google_email": {"$regex": f"^{escaped_email}$", "$options": "i"}})
    if user and not user.get("is_active", False):
        raise HTTPException(403, "Tài khoản đã bị khóa.")
    if not user and await db.users.find_one({"username": {"$regex": f"^{escaped_email}$", "$options": "i"}}):
        raise HTTPException(409, "Tài khoản đã tồn tại. Quản trị viên cần liên kết Google trước khi đăng nhập.")

    # 3. Nếu là tài khoản Google mới hoàn toàn -> Tự động tạo tài khoản Sinh viên (role='student')
    # để sinh viên vào Cổng sinh viên (/student) tự khai báo Họ tên, MSSV, Lớp và chụp ảnh khuôn mặt lần đầu!
    if not user:
        new_user_doc = {
            "username": email,
            "display_name": display_name,
            "password_hash": await run_in_threadpool(hash_password, secrets.token_urlsafe(24)),
            "role": "student",
            "google_email": email,
            "person_id": None,
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
        }
        try:
            res = await db.users.insert_one(new_user_doc)
        except DuplicateKeyError:
            raise HTTPException(409, "Tài khoản vừa được tạo hoặc liên kết. Vui lòng đăng nhập lại.") from None
        new_user_doc["_id"] = res.inserted_id
        user = new_user_doc
    elif display_name and not user.get("display_name"):
        await db.users.update_one(
            {"_id": user["_id"]},
            {"$set": {"display_name": display_name}},
        )

    token, expires = create_access_token(str(user["_id"]), user["username"], user["role"], user.get("auth_version", 0))
    return TokenResponse(
        access_token=token,
        expires_in=expires,
        role=user["role"],
        username=user["username"],
    )


@router.put("/users/{user_id}/google", dependencies=[Depends(require_admin)])
async def link_google_account(
    user_id: str,
    body: GoogleLink,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    if not ObjectId.is_valid(user_id):
        raise HTTPException(400, "Invalid user identifier.")
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(404, "User not found.")

    clean_email = (body.email or "").strip().lower()
    if clean_email:
        if "@" not in clean_email or "." not in clean_email.split("@")[-1]:
            raise HTTPException(400, "Địa chỉ email Google không hợp lệ. / Invalid Google email address.")
        existing = await db.users.find_one({"google_email": clean_email})
        if existing and existing["_id"] != user["_id"]:
            raise HTTPException(409, "Email Google này đã được liên kết với tài khoản khác.")
        update = {"$set": {"google_email": clean_email}}
    else:
        update = {"$unset": {"google_email": ""}}

    try:
        await db.users.update_one({"_id": user["_id"]}, update)
    except DuplicateKeyError:
        raise HTTPException(409, "Email Google này đã được liên kết với tài khoản khác.") from None

    return {"linked": bool(clean_email), "google_email": clean_email or None}
