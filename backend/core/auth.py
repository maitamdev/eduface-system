"""
core/auth.py
Role-separated authentication with Per-User JWT Identity (Step 11)
and backward-compatible shared-secret API key fallback.

Features:
  - Per-user identity via JWT tokens (bearer authorization header).
  - Minimal user collection support with salted scrypt / bcrypt password hashing.
  - Role-based access control: operator vs. admin.
  - Backward compatibility: existing X-API-Key shared secrets remain valid
    as fallbacks during rollout (Step 11 / Finding 9).
"""

import hashlib
import logging
import math
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple

import jwt
from bson import ObjectId
from fastapi import Depends, Header, HTTPException, Request, status
from fastapi.params import Depends as DependsParameter
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import PyMongoError

from core.database import get_db, get_database

logger = logging.getLogger(__name__)

# ── Password Hashing ──────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    """Hash password using hashlib.scrypt with a secure random salt."""
    salt = secrets.token_hex(16)
    key = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt.encode("utf-8"),
        n=16384,
        r=8,
        p=1,
        maxmem=0x2000000,
    )
    return f"scrypt$16384$8$1${salt}${key.hex()}"


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against scrypt or bcrypt hash."""
    if not hashed or not password:
        return False
    try:
        parts = hashed.split("$")
        if len(parts) == 6 and parts[0] == "scrypt":
            _, n, r, p, salt, key_hex = parts
            derived = hashlib.scrypt(
                password.encode("utf-8"),
                salt=salt.encode("utf-8"),
                n=int(n),
                r=int(r),
                p=int(p),
                maxmem=0x2000000,
            )
            return secrets.compare_digest(derived.hex(), key_hex)
        elif hashed.startswith("$2"):
            import bcrypt
            return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except Exception as e:
        logger.warning("Password verification error: %s", e)
        return False
    return False


# ── JWT Utilities ─────────────────────────────────────────────────────────────

_configured_jwt_secret = os.environ.get("JWT_SECRET", "").strip()
_production = os.environ.get("APP_ENV", os.environ.get("ENVIRONMENT", "development")).lower() in {"production", "prod"}
if _production and (len(_configured_jwt_secret) < 32 or _configured_jwt_secret == "smart-attend-jwt-secret-change-in-production"):
    raise RuntimeError("Production requires JWT_SECRET with at least 32 characters.")
# Keep one unpredictable development secret for the process, including module reloads.
_DEV_JWT_SECRET = globals().get("_DEV_JWT_SECRET") or secrets.token_urlsafe(48)
JWT_SECRET = _configured_jwt_secret if _configured_jwt_secret and _configured_jwt_secret != "smart-attend-jwt-secret-change-in-production" else _DEV_JWT_SECRET
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = int(os.environ.get("JWT_EXPIRY_HOURS", "12"))


def create_access_token(user_id: str, username: str, role: str, auth_version: int = 0) -> Tuple[str, int]:
    """Issue a signed JWT containing user ID and role claim."""
    expires_in = JWT_EXPIRY_HOURS * 3600
    expire = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
    payload = {
        "sub": user_id,
        "username": username,
        "role": role,
        "auth_version": auth_version,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token, expires_in


def decode_access_token(token: str) -> dict:
    """Decode and validate a JWT access token."""
    try:
        payload = jwt.decode(
            token, JWT_SECRET, algorithms=[JWT_ALGORITHM],
            options={"require": ["sub", "username", "role", "exp", "iat"]},
        )
        if (
            any(not isinstance(payload.get(key), str) or not payload[key].strip() for key in ("sub", "username"))
            or payload.get("role") not in ("admin", "operator", "student")
            or any(type(payload[key]) not in (int, float) or not math.isfinite(payload[key]) for key in ("exp", "iat"))
            or type(payload.get("auth_version", 0)) is not int
            or payload.get("auth_version", 0) < 0
        ):
            raise jwt.InvalidTokenError("Invalid identity claims")
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Authentication token has expired. Please log in again.",
        )
    except (jwt.InvalidTokenError, ValueError, TypeError, OverflowError):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Invalid authentication token.",
        )


# ── Authenticated User Context ────────────────────────────────────────────────

class AuthenticatedUser:
    def __init__(self, id: str, username: str, role: str, auth_type: str = "jwt", auth_version: int = 0):
        self.id = id
        self.username = username
        self.role = role
        self.auth_type = auth_type
        self.auth_version = auth_version

    def __bool__(self):
        return True


def get_user_id_from_request(request: Optional[Request]) -> Optional[str]:
    """Safely extract user_id from request.state if authenticated."""
    if request and hasattr(request, "state"):
        user = getattr(request.state, "user", None)
        if isinstance(user, AuthenticatedUser):
            return user.id
    return None


# ── Shared-Secret Legacy Keys ─────────────────────────────────────────────────

def _load_keys(*env_names: str) -> set:
    """Collect non-empty, comma-separated key values from the given env vars."""
    keys = set()
    for name in env_names:
        raw = os.environ.get(name, "")
        for part in raw.split(","):
            part = part.strip()
            if part:
                keys.add(part)
    return keys


# Admin API keys (includes legacy single API_KEY)
ADMIN_API_KEYS = _load_keys("API_KEY_ADMIN", "API_KEY")

# Operator API keys
OPERATOR_API_KEYS = _load_keys("API_KEY_OPERATOR")


def _matches_any(candidate: str, valid_keys: set) -> bool:
    if not candidate or not valid_keys:
        return False
    return any(secrets.compare_digest(candidate, k) for k in valid_keys)


def _authenticate(
    request: Optional[Request],
    x_api_key: str,
    authorization: Optional[str],
) -> Tuple[Optional[AuthenticatedUser], bool]:
    """
    Checks Authorization header (Bearer JWT) first, then falls back to X-API-Key.
    Returns (user, no_keys_configured).
    """
    # 1. Check Bearer token
    bearer_token = None
    if isinstance(authorization, str) and authorization.lower().startswith("bearer "):
        bearer_token = authorization[7:].strip()
    elif request is not None and hasattr(request, "headers") and "authorization" in request.headers:
        auth_hdr = request.headers.get("authorization", "")
        if isinstance(auth_hdr, str) and auth_hdr.lower().startswith("bearer "):
            bearer_token = auth_hdr[7:].strip()

    if bearer_token is not None:
        payload = decode_access_token(bearer_token)
        user = AuthenticatedUser(
            id=payload["sub"],
            username=payload["username"],
            role=payload["role"],
            auth_type="jwt",
            auth_version=payload.get("auth_version", 0),
        )
        if request is not None and hasattr(request, "state"):
            request.state.user = user
        return user, False

    # 2. Legacy X-API-Key fallback
    candidate_key = x_api_key if isinstance(x_api_key, str) else ""
    if not candidate_key and request is not None and hasattr(request, "headers"):
        candidate_key = request.headers.get("X-API-Key", "")

    no_keys_configured = not ADMIN_API_KEYS and not OPERATOR_API_KEYS

    if _matches_any(candidate_key, ADMIN_API_KEYS):
        user = AuthenticatedUser(
            id="admin_key",
            username="admin",
            role="admin",
            auth_type="api_key",
        )
        if request is not None:
            request.state.user = user
        return user, False

    if _matches_any(candidate_key, OPERATOR_API_KEYS):
        user = AuthenticatedUser(
            id="operator_key",
            username="operator",
            role="operator",
            auth_type="api_key",
        )
        if request is not None:
            request.state.user = user
        return user, False

    return None, no_keys_configured


async def authenticate_live_user(
    request: Optional[Request],
    x_api_key: str,
    authorization: Optional[str],
    db: Optional[AsyncIOMotorDatabase] = None,
) -> Tuple[Optional[AuthenticatedUser], bool]:
    """Resolve JWT identity against current account state, retaining legacy keys.

    Token roles are historical claims. Every request/frame uses the role and
    active state in MongoDB, so disabling/removing/demoting an account takes
    effect without waiting for the token to expire.
    """
    user, no_keys = _authenticate(request, x_api_key, authorization)
    if user and user.auth_type == "jwt":
        if not ObjectId.is_valid(user.id):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid authentication token.")
        if db is None or isinstance(db, DependsParameter):
            db = get_database()
        try:
            doc = await db.users.find_one({"_id": ObjectId(user.id)})
        except PyMongoError:
            logger.warning("Account verification database unavailable")
            raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Account verification is temporarily unavailable.") from None
        if (
            not doc or doc.get("is_active") is not True
            or doc.get("role") not in ("admin", "operator", "student")
            or not isinstance(doc.get("username"), str) or not doc["username"].strip()
            or type(doc.get("auth_version", 0)) is not int
            or user.auth_version != doc.get("auth_version", 0)
        ):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Account is unavailable or the session has been revoked. Please log in again.")
        user = AuthenticatedUser(str(doc["_id"]), doc["username"], doc["role"], auth_version=doc.get("auth_version", 0))
        if request is not None:
            request.state.user = user
    return user, no_keys


# ── RBAC Route Dependencies ───────────────────────────────────────────────────

async def require_admin(
    request: Request = None,
    x_api_key: str = Header(default="", alias="X-API-Key"),
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> bool:
    """FastAPI dependency: admin-only endpoints."""
    user, no_keys = await authenticate_live_user(request, x_api_key, authorization, db)

    if not ADMIN_API_KEYS and (not user or user.auth_type == "api_key"):
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "Server misconfiguration: no admin API key is configured. "
            "Set API_KEY_ADMIN (or the legacy API_KEY) in the backend environment.",
        )

    if user and user.role == "admin":
        return True

    raise HTTPException(
        status.HTTP_401_UNAUTHORIZED,
        "Missing or invalid admin API key or Bearer token.",
    )


async def require_operator(
    request: Request = None,
    x_api_key: str = Header(default="", alias="X-API-Key"),
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> bool:
    """FastAPI dependency: operator endpoints (create/end sessions, mark attendance).
    An admin key or admin token is also accepted here."""
    user, no_keys = await authenticate_live_user(request, x_api_key, authorization, db)

    if no_keys and (not user or user.auth_type == "api_key"):
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "Server misconfiguration: no API key is configured. "
            "Set API_KEY_OPERATOR (and/or API_KEY_ADMIN) in the backend environment.",
        )

    if user and user.role in ("operator", "admin"):
        return True

    raise HTTPException(
        status.HTTP_401_UNAUTHORIZED,
        "Missing or invalid API key or Bearer token.",
    )


async def require_authenticated(
    request: Request = None,
    x_api_key: str = Header(default="", alias="X-API-Key"),
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> bool:
    """FastAPI dependency: any authenticated user (student, operator, or admin)."""
    user, no_keys = await authenticate_live_user(request, x_api_key, authorization, db)

    if no_keys and (not user or user.auth_type == "api_key"):
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "Server misconfiguration: no API key is configured.",
        )

    if user and user.role in ("student", "operator", "admin"):
        return True

    raise HTTPException(
        status.HTTP_401_UNAUTHORIZED,
        "Missing or invalid authentication token.",
    )


# Backward-compat alias
require_api_key = require_admin
