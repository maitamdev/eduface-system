from types import SimpleNamespace

import pytest

from core.auth import verify_password
from core.database import _seed_accounts


class Users:
    def __init__(self):
        self.created = []

    async def find_one(self, query):
        return None

    async def insert_one(self, doc):
        self.created.append(doc)


@pytest.mark.asyncio
@pytest.mark.parametrize("password", ["", "admin123", "short"])
async def test_production_does_not_create_known_or_missing_passwords(monkeypatch, password):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("DEFAULT_ADMIN_PASSWORD", password)
    db = SimpleNamespace(users=Users())
    await _seed_accounts(db)
    assert db.users.created == []


@pytest.mark.asyncio
async def test_production_only_creates_explicit_admin_not_demo_users(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("DEFAULT_ADMIN_USERNAME", "school-admin")
    monkeypatch.setenv("DEFAULT_ADMIN_PASSWORD", "test-only-unique-password-42")
    db = SimpleNamespace(users=Users())
    await _seed_accounts(db)
    assert len(db.users.created) == 1
    user = db.users.created[0]
    assert user["username"] == "school-admin"
    assert user["role"] == "admin"
    assert verify_password("test-only-unique-password-42", user["password_hash"])
