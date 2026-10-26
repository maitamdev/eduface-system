"""
routers/auth.py
Authentication router for per-user identity (Step 11).

Endpoints:
  POST /api/auth/login     - Authenticate credentials and receive a signed JWT
  POST /api/auth/register  - Create user accounts (Admin only)
  GET  /api/auth/me        - Get current authenticated user profile
"""

import re
import asyncio
from datetime import datetime, timezone
from typing import Optional
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from core.auth import (
    AuthenticatedUser,
    create_access_token,
    hash_password,
    require_admin,
    require_authenticated,
    require_operator,
    verify_password,
)
from core.rate_limit import limiter
from core.database import get_db
from core.attendance_policy import session_applies_to_person, is_session_assessed
from core.schemas import (
    PersonOut,
    PasswordChange,
    StudentPortalSummary,
    StudentSessionItem,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserOut,
    UserUpdate,
)

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
async def login(
    request: Request,
    credentials: UserLogin,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Authenticate username and password; returns a signed JWT."""
    username = credentials.username.strip()
    user_doc = await db.users.find_one({"username": username, "is_active": True})

    if not user_doc or not await asyncio.to_thread(verify_password, credentials.password, user_doc.get("password_hash", "")):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Invalid username or password.",
        )

    token, expires_in = create_access_token(
        user_id=str(user_doc["_id"]),
        username=user_doc["username"],
        role=user_doc["role"],
        auth_version=user_doc.get("auth_version", 0),
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=expires_in,
        role=user_doc["role"],
        username=user_doc["username"],
    )


@router.post("/register", response_model=UserOut, dependencies=[Depends(require_admin)])
async def register_user(
    body: UserCreate,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Create a new operator or admin user (Admin only)."""
    username = body.username.strip()
    existing = await db.users.find_one({"username": username})
    if existing:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            f"User '{username}' already exists.",
        )

    now = datetime.now(timezone.utc)
    user_doc = {
        "username": username,
        "password_hash": await asyncio.to_thread(hash_password, body.password),
        "role": body.role,
        "is_active": True,
        "created_at": now,
        "person_id": body.person_id,
    }
    if body.person_id and not await db.persons.find_one({"_id": body.person_id, "is_active": True}):
        raise HTTPException(422, "Hồ sơ liên kết không tồn tại hoặc đã ngừng hoạt động.")
    result = await db.users.insert_one(user_doc)

    return UserOut(
        id=str(result.inserted_id),
        username=username,
        role=body.role,
        is_active=True,
        created_at=now,
        person_id=body.person_id,
    )


@router.get("/me", response_model=UserOut, dependencies=[Depends(require_authenticated)])
async def get_current_profile(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Return the profile of the currently authenticated user."""
    user = getattr(request.state, "user", None)
    if not isinstance(user, AuthenticatedUser):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated.")

    if user.auth_type == "jwt" and ObjectId.is_valid(user.id):
        doc = await db.users.find_one({"_id": ObjectId(user.id)})
        if doc and doc.get("is_active") is True and doc.get("auth_version", 0) == user.auth_version:
            return UserOut(
                id=str(doc["_id"]),
                username=doc["username"],
                display_name=doc.get("display_name"),
                role=doc["role"],
                is_active=doc.get("is_active", True),
                created_at=doc.get("created_at", datetime.now(timezone.utc)),
                person_id=doc.get("person_id"),
                google_email=doc.get("google_email"),
                microsoft_oid=doc.get("microsoft_oid"),
            )

    if user.auth_type == "jwt":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Account is unavailable. Please log in again.")

    return UserOut(
        id=user.id,
        username=user.username,
        role=user.role,
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )


@router.get("/users", response_model=list[UserOut], dependencies=[Depends(require_admin)])
async def list_users(
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """List all registered users (Admin only)."""
    users = []
    async for doc in db.users.find().sort("created_at", -1):
        users.append(
            UserOut(
                id=str(doc["_id"]),
                username=doc["username"],
                display_name=doc.get("display_name"),
                role=doc.get("role", "operator"),
                is_active=doc.get("is_active", True),
                created_at=doc.get("created_at", datetime.now(timezone.utc)),
                person_id=doc.get("person_id"),
                google_email=doc.get("google_email"),
                microsoft_oid=doc.get("microsoft_oid"),
            )
        )
    return users


@router.patch("/users/{user_id}", response_model=UserOut, dependencies=[Depends(require_admin)])
async def update_user(
    request: Request,
    user_id: str,
    body: UserUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Cập nhật vai trò (role), trạng thái (is_active), mật khẩu hoặc hồ sơ liên kết (Admin only)."""
    if not ObjectId.is_valid(user_id):
        raise HTTPException(400, "Invalid user_id.")
    oid = ObjectId(user_id)
    doc = await db.users.find_one({"_id": oid})
    if not doc:
        raise HTTPException(404, "User not found.")

    current_user = getattr(request.state, "user", None)
    is_self = isinstance(current_user, AuthenticatedUser) and current_user.id == user_id
    if is_self:
        if body.is_active is False:
            raise HTTPException(400, "Không thể tự khóa tài khoản đang đăng nhập của chính bạn.")
        if body.role is not None and body.role != "admin":
            raise HTTPException(400, "Không thể tự hạ quyền Admin của tài khoản đang đăng nhập.")

    updates: dict = {}
    if body.role is not None:
        updates["role"] = body.role
    if body.is_active is not None:
        updates["is_active"] = body.is_active
    if body.password is not None and body.password.strip():
        updates["password_hash"] = await asyncio.to_thread(hash_password, body.password.strip())
    if body.person_id is not None:
        updates["person_id"] = body.person_id.strip() or None
        if updates["person_id"] and not await db.persons.find_one({"_id": updates["person_id"], "is_active": True}):
            raise HTTPException(422, "Hồ sơ liên kết không tồn tại hoặc đã ngừng hoạt động.")

    if updates:
        update_operation = {"$set": updates}
        if "password_hash" in updates or updates.get("is_active") is False:
            # Resetting a password or disabling an account invalidates existing
            # sessions, including after the account is enabled again.
            update_operation["$inc"] = {"auth_version": 1}
        await db.users.update_one({"_id": oid}, update_operation)
        doc.update(updates)

    return UserOut(
        id=str(doc["_id"]),
        username=doc["username"],
        display_name=doc.get("display_name"),
        role=doc.get("role", "operator"),
        is_active=doc.get("is_active", True),
        created_at=doc.get("created_at", datetime.now(timezone.utc)),
        person_id=doc.get("person_id"),
        google_email=doc.get("google_email"),
        microsoft_oid=doc.get("microsoft_oid"),
    )


@router.get("/student-portal", response_model=StudentPortalSummary, dependencies=[Depends(require_authenticated)])
async def get_student_portal(
    request: Request,
    person_id: Optional[str] = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Return course sessions and attendance history for the authenticated student."""
    user = getattr(request.state, "user", None)
    if not isinstance(user, AuthenticatedUser):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated.")

    target_person_id = person_id if user.role in ("admin", "operator") and person_id else None
    if not target_person_id and user.auth_type == "jwt" and ObjectId.is_valid(user.id):
        user_doc = await db.users.find_one({"_id": ObjectId(user.id)})
        if user_doc and user_doc.get("person_id"):
            target_person_id = user_doc["person_id"]

    person_doc = None
    if target_person_id:
        person_doc = await db.persons.find_one({"_id": target_person_id, "is_active": True})

    # Identity must be linked explicitly by an administrator. Names and email
    # strings are not proof that the account owns a biometric/attendance profile.
    if not person_doc:
        return StudentPortalSummary(
            person=None,
            total_sessions=0,
            present_count=0,
            absent_count=0,
            attendance_rate=0.0,
            is_defaulter=False,
            sessions=[],
        )

    pid = str(person_doc["_id"])
    person_out = PersonOut(
        id=pid,
        name=person_doc["name"],
        student_id=person_doc.get("student_id"),
        email=person_doc.get("email"),
        department=person_doc.get("department"),
        photo_url=person_doc.get("photo_url"),
        enrolled_at=person_doc["enrolled_at"],
        is_active=person_doc.get("is_active", True),
        enrolled_by=person_doc.get("enrolled_by"),
    )

    session_query = {}

    session_docs = []
    async for sdoc in db.sessions.find(session_query).sort("started_at", -1):
        if session_applies_to_person(sdoc, person_doc):
            session_docs.append(sdoc)

    attendance_by_session = {}
    async for adoc in db.attendance.find({"person_id": pid}):
        sid = str(adoc.get("session_id", ""))
        attendance_by_session[sid] = adoc

    items = []
    for sdoc in session_docs:
        sid = str(sdoc["_id"])
        att = attendance_by_session.get(sid)
        is_active = bool(sdoc.get("is_active", False))
        if att and is_session_assessed(sdoc, att):
            raw_status = att.get("status", "present")
            if raw_status in ("present", "late", "excused"):
                item_status = raw_status if raw_status in ("present", "late", "excused") else "present"
                attended = True
            else:
                item_status = "absent"
                attended = False
            marked_at = att.get("marked_at")
            confidence = att.get("confidence")
        elif is_active:
            item_status = "open"
            attended = False
            marked_at = None
            confidence = None
        else:
            item_status = "absent"
            attended = False
            marked_at = None
            confidence = None

        items.append(
            StudentSessionItem(
                session_id=sid,
                label=sdoc["label"],
                department=sdoc.get("department"),
                started_at=sdoc["started_at"],
                ended_at=sdoc.get("ended_at"),
                is_active=is_active,
                attended=attended,
                marked_at=marked_at,
                confidence=confidence,
                status=item_status,
            )
        )

    total_sessions = len(items)
    present_count = sum(1 for item in items if item.attended)
    absent_count = sum(1 for item in items if item.status == "absent")
    assessed_sessions = present_count + absent_count
    rate = round((present_count / assessed_sessions) * 100, 1) if assessed_sessions else 100.0

    return StudentPortalSummary(
        person=person_out,
        total_sessions=total_sessions,
        present_count=present_count,
        absent_count=absent_count,
        attendance_rate=rate,
        is_defaulter=assessed_sessions > 0 and rate < 75.0,
        sessions=items,
    )


@router.post("/password", response_model=TokenResponse, dependencies=[Depends(require_authenticated)])
@limiter.limit("5/minute")
async def change_password(request: Request, body: PasswordChange,
                          db: AsyncIOMotorDatabase = Depends(get_db)):
    user = request.state.user
    if user.auth_type != "jwt" or not ObjectId.is_valid(user.id):
        raise HTTPException(403, "Cần đăng nhập bằng tài khoản cá nhân.")
    doc = await db.users.find_one({"_id": ObjectId(user.id), "is_active": True})
    if not doc or not await asyncio.to_thread(verify_password, body.current_password, doc.get("password_hash", "")):
        raise HTTPException(400, "Mật khẩu hiện tại không đúng.")
    if body.current_password == body.new_password:
        raise HTTPException(422, "Mật khẩu mới phải khác mật khẩu hiện tại.")
    encoded = await asyncio.to_thread(hash_password, body.new_password)
    changed = await db.users.update_one({"_id": doc["_id"], "password_hash": doc["password_hash"]},
        {"$set": {"password_hash": encoded}, "$inc": {"auth_version": 1}})
    if not changed.matched_count:
        raise HTTPException(409, "Mật khẩu vừa được thay đổi. Vui lòng đăng nhập lại.")
    token, expires = create_access_token(str(doc["_id"]), doc["username"], doc["role"], doc.get("auth_version", 0) + 1)
    return TokenResponse(access_token=token, expires_in=expires, role=doc["role"], username=doc["username"])
