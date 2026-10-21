from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock

import jwt
import pytest
from bson import ObjectId
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from core import microsoft_identity as identity
from core.database import get_db
from core.rate_limit import limiter
from routers import microsoft_auth

TENANT = "11111111-1111-4111-8111-111111111111"
CLIENT = "22222222-2222-4222-8222-222222222222"
OBJECT = "33333333-3333-4333-8333-333333333333"
CHALLENGE = "test-challenge-identifier-long-enough"
NONCE = "server-issued-random-nonce"


@pytest.fixture
def keys():
    private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return private, private.public_key()


def _token(private, **overrides):
    now = datetime.now(timezone.utc)
    payload = {"iss": f"https://login.microsoftonline.com/{TENANT}/v2.0", "aud": CLIENT,
               "sub": "pairwise-subject", "tid": TENANT, "oid": OBJECT, "nonce": NONCE,
               "iat": now, "exp": now + timedelta(minutes=5)}
    payload.update(overrides)
    return jwt.encode(payload, private, algorithm="RS256", headers={"kid": "test-key"})


@pytest.fixture
def config(monkeypatch, keys):
    monkeypatch.setenv("MICROSOFT_CLIENT_ID", CLIENT)
    monkeypatch.setenv("MICROSOFT_TENANT_ID", TENANT)
    monkeypatch.setattr(identity, "_key_client", lambda tenant: SimpleNamespace(get_signing_key_from_jwt=lambda token: SimpleNamespace(key=keys[1])))
    return identity.require_microsoft_configuration()


@pytest.mark.parametrize("overrides", [
    {"aud": "untrusted-client"}, {"iss": "https://untrusted.example/v2.0"},
    {"tid": "44444444-4444-4444-8444-444444444444"},
    {"exp": datetime.now(timezone.utc) - timedelta(minutes=2)},
    {"nonce": None}, {"oid": "not-a-guid"},
])
def test_identity_rejects_invalid_claims(config, keys, overrides):
    with pytest.raises(HTTPException) as error:
        identity.verify_microsoft_identity(_token(keys[0], **overrides), config)
    assert error.value.status_code == 401


def test_identity_rejects_untrusted_signature(config, keys):
    attacker = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    with pytest.raises(HTTPException) as error:
        identity.verify_microsoft_identity(_token(attacker), config)
    assert error.value.status_code == 401


@pytest.fixture
def client(config):
    challenge = {"_id": CHALLENGE, "nonce_hash": identity.nonce_digest(NONCE), "expires_at": datetime.now(timezone.utc) + timedelta(minutes=5)}
    user = {"_id": ObjectId(), "username": "student_demo", "role": "student", "is_active": True}
    async def consume(query):
        if challenge and query["_id"] == challenge["_id"] and query["nonce_hash"] == challenge["nonce_hash"] and challenge["expires_at"] > query["expires_at"]["$gt"]:
            result = dict(challenge)
            challenge.clear()
            return result
        return None
    db = SimpleNamespace(
        users=SimpleNamespace(find_one=AsyncMock(return_value=user), update_one=AsyncMock()),
        auth_challenges=SimpleNamespace(insert_one=AsyncMock(), find_one_and_delete=AsyncMock(side_effect=consume)),
    )
    app = FastAPI()
    app.state.limiter = limiter
    limiter.reset()
    app.include_router(microsoft_auth.router, prefix="/api/auth")
    app.dependency_overrides[get_db] = lambda: db
    return TestClient(app), db, challenge, user


def test_config_disabled_until_valid_tenant_and_client(monkeypatch):
    monkeypatch.delenv("MICROSOFT_CLIENT_ID", raising=False)
    monkeypatch.setenv("MICROSOFT_TENANT_ID", "common")
    assert identity.microsoft_configuration()["enabled"] is False
    with pytest.raises(HTTPException) as error:
        identity.require_microsoft_configuration()
    assert error.value.status_code == 503


def test_challenge_is_expiring_and_nonce_is_not_stored_plaintext(client):
    http, db, _, _ = client
    response = http.post("/api/auth/microsoft/challenge")
    assert response.status_code == 200
    body = response.json()
    stored = db.auth_challenges.insert_one.call_args.args[0]
    assert stored["nonce_hash"] == identity.nonce_digest(body["nonce"])
    assert "nonce" not in stored
    assert stored["expires_at"] > datetime.now(timezone.utc)


def test_linked_identity_preserves_student_role_and_cannot_replay(client, keys):
    http, db, _, _ = client
    body = {"challenge_id": CHALLENGE, "id_token": _token(keys[0])}
    response = http.post("/api/auth/microsoft", json=body)
    assert response.status_code == 200
    assert response.json()["role"] == "student"
    assert response.json()["access_token"]
    db.users.find_one.assert_awaited_once_with({"microsoft_oid": OBJECT, "microsoft_tenant_id": TENANT, "is_active": True})
    assert http.post("/api/auth/microsoft", json=body).status_code == 401


def test_unlinked_user_is_not_created_or_matched_by_email(client, keys):
    http, db, _, _ = client
    db.users.find_one.return_value = None
    response = http.post("/api/auth/microsoft", json={"challenge_id": CHALLENGE, "id_token": _token(keys[0], preferred_username="admin@example.edu")})
    assert response.status_code == 403
    assert "email" not in db.users.find_one.call_args.args[0]


@pytest.mark.parametrize("expired", [True, False])
def test_expired_or_mismatched_nonce_does_not_reach_accounts(client, keys, expired):
    http, db, challenge, _ = client
    if expired:
        challenge["expires_at"] = datetime.now(timezone.utc) - timedelta(minutes=1)
    else:
        challenge["nonce_hash"] = identity.nonce_digest("different-nonce")
    response = http.post("/api/auth/microsoft", json={"challenge_id": CHALLENGE, "id_token": _token(keys[0])})
    assert response.status_code == 401
    db.users.find_one.assert_not_awaited()


def test_link_endpoint_requires_admin(client):
    http, db, _, user = client
    response = http.put(f"/api/auth/users/{user['_id']}/microsoft", json={"object_id": OBJECT})
    assert response.status_code in (401, 503)
    db.users.update_one.assert_not_awaited()
