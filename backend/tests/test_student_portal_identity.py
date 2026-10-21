"""Portal identity isolation and attendance calculation without a live database."""
from datetime import datetime, timezone
from types import SimpleNamespace

from bson import ObjectId
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from core.auth import create_access_token
from core.database import get_db
from routers.auth import router


@pytest.fixture(autouse=True)
def current_auth_type(monkeypatch):
    # Role-configuration tests reload core.auth. Refresh this imported class
    # reference so the router and dependency use the same identity type.
    from core import auth
    from routers import auth as auth_router
    monkeypatch.setattr(auth_router, "AuthenticatedUser", auth.AuthenticatedUser)


class Cursor:
    def __init__(self, docs):
        self.docs = docs

    def sort(self, *_):
        return self

    def limit(self, count):
        self.docs = self.docs[:count]
        return self

    def __aiter__(self):
        async def items():
            for doc in self.docs:
                yield doc
        return items()


class Collection:
    def __init__(self, docs):
        self.docs = docs
        self.queries = []

    async def find_one(self, query):
        self.queries.append(query)
        return next((doc for doc in self.docs if all(doc.get(k) == v for k, v in query.items())), None)

    def find(self, query):
        return Cursor([doc for doc in self.docs if all(doc.get(k) == v for k, v in query.items())])


def portal_client(linked=True, sessions=None, attendance=None):
    uid = ObjectId()
    user = {"_id": uid, "username": "Same Name", "role": "student", "is_active": True}
    if linked:
        user["person_id"] = "own-profile"
    people = Collection([{
        "_id": "own-profile", "name": "Same Name", "is_active": True,
        "enrolled_at": datetime.now(timezone.utc),
    }])
    db = SimpleNamespace(users=Collection([user]), persons=people,
                         sessions=Collection(sessions or []), attendance=Collection(attendance or []))
    app = FastAPI()
    app.include_router(router, prefix="/api/auth")
    app.dependency_overrides[get_db] = lambda: db
    token, _ = create_access_token(str(uid), user["username"], "student")
    return TestClient(app), {"Authorization": f"Bearer {token}"}, people


def test_unlinked_student_cannot_claim_profile_by_name_or_query_parameter():
    client, headers, people = portal_client(linked=False)
    result = client.get("/api/auth/student-portal?person_id=own-profile", headers=headers)
    assert result.status_code == 200
    assert result.json()["person"] is None
    assert people.queries == []


def test_linked_student_ignores_other_person_parameter():
    client, headers, people = portal_client()
    result = client.get("/api/auth/student-portal?person_id=another-profile", headers=headers)
    assert result.status_code == 200
    assert result.json()["person"]["id"] == "own-profile"
    assert people.queries == [{"_id": "own-profile", "is_active": True}]


def test_open_unmarked_sessions_do_not_reduce_attendance_rate():
    now = datetime.now(timezone.utc)
    sessions = [{"_id": sid, "label": sid, "started_at": now, "is_active": active}
                for sid, active in [("present", False), ("open", True)]]
    client, headers, _ = portal_client(sessions=sessions, attendance=[{
        "person_id": "own-profile", "session_id": "present", "marked_at": now,
    }])
    result = client.get("/api/auth/student-portal", headers=headers).json()
    assert result["total_sessions"] == 2
    assert result["present_count"] == 1
    assert result["attendance_rate"] == 100
    assert result["is_defaulter"] is False


def test_closed_unmarked_session_counts_as_absent():
    now = datetime.now(timezone.utc)
    client, headers, _ = portal_client(sessions=[{
        "_id": "closed", "label": "Closed", "started_at": now, "is_active": False,
    }])
    result = client.get("/api/auth/student-portal", headers=headers).json()
    assert result["absent_count"] == 1
    assert result["attendance_rate"] == 0
    assert result["is_defaulter"] is True
