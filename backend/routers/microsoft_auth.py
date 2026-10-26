import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, Field
from pymongo.errors import DuplicateKeyError
from starlette.concurrency import run_in_threadpool

from core.auth import create_access_token, require_admin
from core.database import get_db
from core.microsoft_identity import microsoft_configuration, require_microsoft_configuration, nonce_digest, verify_microsoft_identity
from core.rate_limit import limiter
from core.schemas import TokenResponse

router = APIRouter()


class MicrosoftExchange(BaseModel):
    challenge_id: str = Field(min_length=20, max_length=128)
    id_token: str = Field(min_length=20, max_length=24000)


class MicrosoftLink(BaseModel):
    object_id: Optional[UUID] = None


@router.get("/microsoft/config")
async def get_configuration():
    return microsoft_configuration()


@router.post("/microsoft/challenge")
@limiter.limit("10/minute")
async def create_challenge(request: Request, db: AsyncIOMotorDatabase = Depends(get_db)):
    require_microsoft_configuration()
    nonce = secrets.token_urlsafe(32)
    challenge_id = secrets.token_urlsafe(32)
    await db.auth_challenges.insert_one({
        "_id": challenge_id, "nonce_hash": nonce_digest(nonce),
        "expires_at": datetime.now(timezone.utc) + timedelta(minutes=10),
    })
    return {"challenge_id": challenge_id, "nonce": nonce}


@router.post("/microsoft", response_model=TokenResponse)
@limiter.limit("10/minute")
async def exchange_identity(request: Request, body: MicrosoftExchange, db: AsyncIOMotorDatabase = Depends(get_db)):
    config = require_microsoft_configuration()
    claims = await run_in_threadpool(verify_microsoft_identity, body.id_token, config)
    # Atomically consume the nonce: an ID token cannot be replayed, even by
    # simultaneous requests or across multiple backend workers.
    challenge = await db.auth_challenges.find_one_and_delete({
        "_id": body.challenge_id,
        "nonce_hash": nonce_digest(claims["nonce"]),
        "expires_at": {"$gt": datetime.now(timezone.utc)},
    })
    if not challenge:
        raise HTTPException(401, "Microsoft sign-in request expired or was already used. Please sign in again.")
    user = await db.users.find_one({
        "microsoft_oid": claims["oid"], "microsoft_tenant_id": config["tenant_id"],
        "is_active": True,
    })
    if not user or user.get("role") not in {"admin", "operator", "student"}:
        raise HTTPException(403, "This Microsoft account is not linked to an active EduFace account. Contact your administrator.")
    token, expires = create_access_token(str(user["_id"]), user["username"], user["role"], user.get("auth_version", 0))
    return TokenResponse(access_token=token, expires_in=expires, role=user["role"], username=user["username"])


@router.put("/users/{user_id}/microsoft", dependencies=[Depends(require_admin)])
async def link_identity(user_id: str, body: MicrosoftLink, db: AsyncIOMotorDatabase = Depends(get_db)):
    config = require_microsoft_configuration()
    if not ObjectId.is_valid(user_id):
        raise HTTPException(400, "Invalid user identifier.")
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(404, "User not found.")
    if body.object_id:
        identity = {"microsoft_oid": str(body.object_id), "microsoft_tenant_id": config["tenant_id"]}
        existing = await db.users.find_one(identity)
        if existing and existing["_id"] != user["_id"]:
            raise HTTPException(409, "This Microsoft account is already linked to another user.")
        update = {"$set": identity}
    else:
        update = {"$unset": {"microsoft_oid": "", "microsoft_tenant_id": ""}}
    try:
        await db.users.update_one({"_id": user["_id"]}, update)
    except DuplicateKeyError:
        raise HTTPException(409, "This Microsoft account is already linked to another user.") from None
    return {"linked": body.object_id is not None, "object_id": str(body.object_id) if body.object_id else None}
