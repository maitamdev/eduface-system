"""Google Identity Services (OAuth2 / OIDC) token verification for EduFace."""
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from functools import lru_cache

import jwt
from fastapi import HTTPException


def google_configuration() -> dict:
    client_id = os.environ.get("GOOGLE_CLIENT_ID", "").strip()
    if len(client_id) < 15 or " " in client_id:
        return {"enabled": False, "client_id": ""}
    return {"enabled": True, "client_id": client_id}


def require_google_configuration() -> dict:
    config = google_configuration()
    if not config["enabled"]:
        raise HTTPException(
            503,
            "Đăng nhập Google chưa được cấu hình (thiếu GOOGLE_CLIENT_ID). / Google sign-in is not configured.",
        )
    return config


@lru_cache(maxsize=2)
def _google_jwk_client() -> jwt.PyJWKClient:
    return jwt.PyJWKClient(
        "https://www.googleapis.com/oauth2/v3/certs",
        cache_keys=True,
        cache_jwk_set=True,
        lifespan=3600,
        timeout=8,
    )


def verify_google_id_token(id_token: str, config: dict) -> dict:
    """Validate a Google OIDC id_token using Google's JWKS keys."""
    try:
        key = _google_jwk_client().get_signing_key_from_jwt(id_token)
        claims = jwt.decode(
            id_token,
            key.key,
            algorithms=["RS256"],
            audience=config["client_id"],
            issuer=["https://accounts.google.com", "accounts.google.com"],
            options={"require": ["exp", "iat", "iss", "aud", "sub", "email"]},
            leeway=30,
        )
        if not claims.get("email_verified"):
            raise ValueError("Email not verified")
        email = str(claims.get("email", "")).strip().lower()
        if not email or "@" not in email:
            raise ValueError("Invalid email")
        return {
            "sub": str(claims["sub"]),
            "email": email,
            "name": str(claims.get("name", email)),
        }
    except jwt.PyJWKClientConnectionError:
        raise HTTPException(503, "Google sign-in is temporarily unavailable. Please try again.") from None
    except (jwt.PyJWTError, ValueError, TypeError, KeyError, AttributeError):
        raise HTTPException(401, "Google identity token is invalid or expired.") from None


def verify_google_access_token(access_token: str, config: dict) -> dict:
    """Validate a Google OAuth2 access_token via Google tokeninfo + userinfo endpoints."""
    try:
        tokeninfo_url = "https://oauth2.googleapis.com/tokeninfo?" + urllib.parse.urlencode(
            {"access_token": access_token}
        )
        with urllib.request.urlopen(tokeninfo_url, timeout=8) as resp:
            info = json.loads(resp.read().decode("utf-8"))

        aud = info.get("aud") or info.get("azp") or ""
        if aud != config["client_id"]:
            raise ValueError("Audience mismatch")

        email_verified = str(info.get("email_verified", "")).lower() == "true"
        email = str(info.get("email", "")).strip().lower()
        sub = str(info.get("sub", "")).strip()

        if not email or not email_verified or "@" not in email:
            req = urllib.request.Request(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            with urllib.request.urlopen(req, timeout=8) as uresp:
                uinfo = json.loads(uresp.read().decode("utf-8"))
            email = str(uinfo.get("email", "")).strip().lower()
            email_verified = bool(uinfo.get("email_verified"))
            sub = str(uinfo.get("sub", sub)).strip()

        if not email or not email_verified or "@" not in email:
            raise ValueError("Unverified Google email")

        return {"sub": sub, "email": email, "name": email}
    except urllib.error.HTTPError as exc:
        if exc.code >= 500:
            raise HTTPException(503, "Google sign-in is temporarily unavailable.") from None
        raise HTTPException(401, "Google access token is invalid or expired.") from None
    except urllib.error.URLError:
        raise HTTPException(503, "Google sign-in is temporarily unavailable.") from None
    except (ValueError, TypeError, KeyError, json.JSONDecodeError):
        raise HTTPException(401, "Google access token is invalid or expired.") from None
