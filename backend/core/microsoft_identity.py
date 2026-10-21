"""Single-tenant Microsoft identity validation. No email-based account linking."""
import hashlib
import os
import uuid
from functools import lru_cache

import jwt
from fastapi import HTTPException


def microsoft_configuration() -> dict:
    client_id = os.environ.get("MICROSOFT_CLIENT_ID", "").strip()
    tenant_id = os.environ.get("MICROSOFT_TENANT_ID", "").strip()
    try:
        client_id = str(uuid.UUID(client_id))
        tenant_id = str(uuid.UUID(tenant_id))
    except (ValueError, AttributeError):
        return {"enabled": False, "client_id": "", "tenant_id": ""}
    return {"enabled": True, "client_id": client_id, "tenant_id": tenant_id}


def require_microsoft_configuration() -> dict:
    config = microsoft_configuration()
    if not config["enabled"]:
        raise HTTPException(503, "Microsoft sign-in is not configured. Contact your administrator.")
    return config


def nonce_digest(nonce: str) -> str:
    return hashlib.sha256(nonce.encode("utf-8")).hexdigest()


@lru_cache(maxsize=4)
def _key_client(tenant_id: str) -> jwt.PyJWKClient:
    return jwt.PyJWKClient(
        f"https://login.microsoftonline.com/{tenant_id}/discovery/v2.0/keys",
        cache_keys=True, cache_jwk_set=True, lifespan=3600, timeout=8,
    )


def verify_microsoft_identity(id_token: str, config: dict) -> dict:
    """Validate provider signature, tenant, issuer, audience and token lifetime."""
    tenant = config["tenant_id"]
    try:
        key = _key_client(tenant).get_signing_key_from_jwt(id_token)
        claims = jwt.decode(
            id_token, key.key, algorithms=["RS256"], audience=config["client_id"],
            issuer=f"https://login.microsoftonline.com/{tenant}/v2.0",
            options={"require": ["exp", "iat", "iss", "aud", "sub", "tid", "oid", "nonce"]},
            leeway=30,
        )
        if str(uuid.UUID(claims["tid"])) != tenant:
            raise ValueError("Wrong tenant")
        claims["oid"] = str(uuid.UUID(claims["oid"]))
        if not isinstance(claims["nonce"], str) or not claims["nonce"]:
            raise ValueError("Missing nonce")
        return claims
    except jwt.PyJWKClientConnectionError:
        raise HTTPException(503, "Microsoft sign-in is temporarily unavailable. Please try again.") from None
    except (jwt.PyJWTError, ValueError, TypeError, KeyError, AttributeError):
        raise HTTPException(401, "Microsoft identity token is invalid or expired.") from None
