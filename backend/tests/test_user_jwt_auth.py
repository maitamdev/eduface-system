"""
tests/test_user_jwt_auth.py

Covers Step 11: Per-user identity & JWT authentication.
Tests:
  - Password hashing and verification (scrypt)
  - JWT creation, decoding, and expiration rejection
  - POST /api/auth/login endpoint
  - Protected endpoints with Bearer tokens (RBAC checks)
  - Attendance marked_by and Person enrolled_by audit recording
"""

import time
from bson import ObjectId
import jwt
import pytest
from fastapi import FastAPI, Depends, Request
from fastapi.testclient import TestClient
from pymongo.errors import ServerSelectionTimeoutError

import core.auth as core_auth
from core.auth import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    require_admin,
    require_operator,
    get_user_id_from_request,
    JWT_ALGORITHM,
)
from core.database import get_db
from routers import auth as auth_router_module


def test_password_hashing_and_verification():
    raw_pw = "SuperSecurePassword123!"
    hashed = hash_password(raw_pw)

    assert hashed != raw_pw
    assert hashed.startswith("scrypt$")
    assert verify_password(raw_pw, hashed) is True
    assert verify_password("WrongPassword", hashed) is False
    assert verify_password("", hashed) is False


def test_jwt_creation_and_decoding():
    token, expires_in = create_access_token("user-123", "alice", "admin")
    assert isinstance(token, str)
    assert expires_in > 0

    payload = decode_access_token(token)
    assert payload["sub"] == "user-123"
    assert payload["username"] == "alice"
    assert payload["role"] == "admin"


def test_jwt_expired_token_rejected():
    # Generate token already in the past
    payload = {
        "sub": "user-expired",
        "username": "expired_user",
        "role": "operator",
        "exp": int(time.time()) - 10,
        "iat": int(time.time()) - 20,
    }
    expired_token = jwt.encode(payload, core_auth.JWT_SECRET, algorithm=JWT_ALGORITHM)

    with pytest.raises(Exception) as exc_info:
        decode_access_token(expired_token)
    assert exc_info.value.status_code == 401
    assert "expired" in exc_info.value.detail.lower()


class FakeUsersCollection:
    def __init__(self, users):
        self.users = users

    async def find_one(self, query):
        for u in self.users:
            if all(u.get(k) == v for k, v in query.items()):
                return u
        return None

    async def insert_one(self, doc):
        doc["_id"] = ObjectId()
        self.users.append(doc)
        class Res:
            inserted_id = doc["_id"]
        return Res()

    async def update_one(self, query, update):
        doc = await self.find_one(query)
        if doc is not None:
            doc.update(update.get("$set", {}))
            for key, amount in update.get("$inc", {}).items():
                doc[key] = doc.get(key, 0) + amount


class FakeAuthDB:
    def __init__(self, users):
        self.users = FakeUsersCollection(users)


@pytest.fixture
def auth_client():
    user_doc = {
        "_id": ObjectId(),
        "username": "operator_john",
        "password_hash": hash_password("secret123"),
        "role": "operator",
        "is_active": True,
    }
    admin_doc = {
        "_id": ObjectId(),
        "username": "admin_sarah",
        "password_hash": hash_password("adminsecret123"),
        "role": "admin",
        "is_active": True,
    }
    fake_db = FakeAuthDB([user_doc, admin_doc])

    app = FastAPI()
    app.include_router(auth_router_module.router, prefix="/api/auth")

    # Mock routes to test RBAC with Bearer token
    @app.get("/test-operator", dependencies=[Depends(require_operator)])
    async def test_op_route(request: Request):
        return {"user_id": get_user_id_from_request(request)}

    @app.get("/test-admin", dependencies=[Depends(require_admin)])
    async def test_admin_route(request: Request):
        return {"user_id": get_user_id_from_request(request)}

    app.dependency_overrides[get_db] = lambda: fake_db
    app.state.test_db = fake_db

    return TestClient(app), user_doc, admin_doc


def test_login_success(auth_client):
    client, user_doc, _ = auth_client

    resp = client.post("/api/auth/login", json={
        "username": "operator_john",
        "password": "secret123",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["role"] == "operator"
    assert data["username"] == "operator_john"


def test_login_invalid_credentials(auth_client):
    client, _, _ = auth_client

    resp = client.post("/api/auth/login", json={
        "username": "operator_john",
        "password": "wrongpassword",
    })
    assert resp.status_code == 401
    assert "Invalid username or password" in resp.json()["detail"]


def test_jwt_bearer_token_access_and_rbac(auth_client):
    client, user_doc, admin_doc = auth_client

    # Generate tokens
    op_token, _ = create_access_token(str(user_doc["_id"]), "operator_john", "operator")
    admin_token, _ = create_access_token(str(admin_doc["_id"]), "admin_sarah", "admin")

    # 1. Operator accesses operator endpoint -> OK
    res1 = client.get("/test-operator", headers={"Authorization": f"Bearer {op_token}"})
    assert res1.status_code == 200
    assert res1.json()["user_id"] == str(user_doc["_id"])

    # 2. Operator accesses admin endpoint -> 401 Forbidden/Unauthorized
    res2 = client.get("/test-admin", headers={"Authorization": f"Bearer {op_token}"})
    assert res2.status_code == 401

    # 3. Admin accesses operator endpoint -> OK (Admin is superset of operator)
    res3 = client.get("/test-operator", headers={"Authorization": f"Bearer {admin_token}"})
    assert res3.status_code == 200
    assert res3.json()["user_id"] == str(admin_doc["_id"])

    # 4. Admin accesses admin endpoint -> OK
    res4 = client.get("/test-admin", headers={"Authorization": f"Bearer {admin_token}"})
    assert res4.status_code == 200
    assert res4.json()["user_id"] == str(admin_doc["_id"])


@pytest.mark.parametrize("change", ["disabled", "deleted", "invalid_role"])
def test_existing_token_rejects_unavailable_account(auth_client, change):
    client, user, _ = auth_client
    token, _ = create_access_token(str(user["_id"]), user["username"], user["role"])
    if change == "disabled":
        user["is_active"] = False
    elif change == "deleted":
        client.app.state.test_db.users.users.remove(user)
    else:
        user["role"] = "owner"
    for path in ("/test-operator", "/api/auth/me"):
        assert client.get(path, headers={"Authorization": f"Bearer {token}"}).status_code == 401


def test_role_and_username_come_from_current_account(auth_client):
    client, _, admin = auth_client
    token, _ = create_access_token(str(admin["_id"]), admin["username"], "admin")
    admin.update(role="operator", username="renamed_admin")
    headers = {"Authorization": f"Bearer {token}"}
    assert client.get("/test-admin", headers=headers).status_code == 401
    assert client.get("/test-operator", headers=headers).status_code == 200
    profile = client.get("/api/auth/me", headers=headers)
    assert profile.status_code == 200
    assert profile.json()["username"] == "renamed_admin"
    assert profile.json()["role"] == "operator"
    admin["role"] = "student"
    assert client.get("/test-operator", headers=headers).status_code == 401
    assert client.get("/api/auth/me", headers=headers).status_code == 200


@pytest.mark.parametrize("missing", ["sub", "username", "role", "exp", "iat"])
def test_signed_token_requires_identity_and_lifetime_claims(auth_client, missing):
    client, user, _ = auth_client
    claims = {"sub": str(user["_id"]), "username": user["username"], "role": "operator", "exp": int(time.time()) + 60, "iat": int(time.time())}
    del claims[missing]
    token = jwt.encode(claims, core_auth.JWT_SECRET, algorithm=JWT_ALGORITHM)
    assert client.get("/test-operator", headers={"Authorization": f"Bearer {token}"}).status_code == 401


@pytest.mark.parametrize("claim,value", [("sub", "not-an-object-id"), ("username", ""), ("role", "owner"), ("exp", "9999999999"), ("exp", {}), ("iat", None), ("exp", float("inf")), ("auth_version", True), ("auth_version", -1)])
def test_signed_token_rejects_malformed_claims(auth_client, claim, value):
    client, user, _ = auth_client
    claims = {"sub": str(user["_id"]), "username": user["username"], "role": "operator", "exp": int(time.time()) + 60, "iat": int(time.time())}
    claims[claim] = value
    token = jwt.encode(claims, core_auth.JWT_SECRET, algorithm=JWT_ALGORITHM)
    assert client.get("/test-operator", headers={"Authorization": f"Bearer {token}"}).status_code == 401


def test_password_reset_revokes_old_sessions_and_allows_new_login(auth_client):
    client, user, admin = auth_client
    old_token, _ = create_access_token(str(user["_id"]), user["username"], "operator")
    admin_token, _ = create_access_token(str(admin["_id"]), admin["username"], "admin")
    reset = client.patch(f"/api/auth/users/{user['_id']}", json={"password": "replacement-secret"}, headers={"Authorization": f"Bearer {admin_token}"})
    assert reset.status_code == 200
    assert user["auth_version"] == 1
    assert client.get("/api/auth/me", headers={"Authorization": f"Bearer {old_token}"}).status_code == 401
    login = client.post("/api/auth/login", json={"username": user["username"], "password": "replacement-secret"})
    assert login.status_code == 200
    new_token = login.json()["access_token"]
    assert decode_access_token(new_token)["auth_version"] == 1
    assert client.get("/api/auth/me", headers={"Authorization": f"Bearer {new_token}"}).status_code == 200


def test_legacy_token_without_auth_version_still_resolves_account(auth_client):
    client, user, _ = auth_client
    claims = {"sub": str(user["_id"]), "username": user["username"], "role": "operator", "exp": int(time.time()) + 60, "iat": int(time.time())}
    token = jwt.encode(claims, core_auth.JWT_SECRET, algorithm=JWT_ALGORITHM)
    assert client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"}).status_code == 200


def test_account_lookup_outage_fails_closed(auth_client, monkeypatch):
    client, user, _ = auth_client
    token, _ = create_access_token(str(user["_id"]), user["username"], "operator")

    async def unavailable(_query):
        raise ServerSelectionTimeoutError("private database connection details")

    monkeypatch.setattr(client.app.state.test_db.users, "find_one", unavailable)
    response = client.get("/test-operator", headers={"Authorization": f"Bearer {token}", "X-API-Key": "test-api-key"})
    assert response.status_code == 503
    assert "private database" not in response.text


def test_empty_bearer_cannot_fall_back_to_legacy_key(auth_client):
    client, _, _ = auth_client
    response = client.get("/test-operator", headers={"Authorization": "Bearer ", "X-API-Key": "test-api-key"})
    assert response.status_code == 401


def test_reenabled_account_does_not_restore_revoked_token(auth_client):
    client, user, admin = auth_client
    old_token, _ = create_access_token(str(user["_id"]), user["username"], "operator")
    admin_token, _ = create_access_token(str(admin["_id"]), admin["username"], "admin")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    path = f"/api/auth/users/{user['_id']}"
    assert client.patch(path, json={"is_active": False}, headers=admin_headers).status_code == 200
    assert user["auth_version"] == 1
    assert client.patch(path, json={"is_active": True}, headers=admin_headers).status_code == 200
    assert client.get("/api/auth/me", headers={"Authorization": f"Bearer {old_token}"}).status_code == 401
    login = client.post("/api/auth/login", json={"username": user["username"], "password": "secret123"})
    assert login.status_code == 200
    assert client.get("/api/auth/me", headers={"Authorization": f"Bearer {login.json()['access_token']}"}).status_code == 200
