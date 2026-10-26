"""Academic authorization and business rules using an in-memory Mongo stand-in."""

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import re
from types import SimpleNamespace

from bson import ObjectId
from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from core import auth
from core.database import get_db
from routers import academic


NOW = datetime(2026, 10, 23, 2, tzinfo=timezone.utc)
OWN = "own-person"
OTHER = "other-person"


def matches(doc, query):
    for key, value in query.items():
        if key == "$or":
            if not any(matches(doc, clause) for clause in value):
                return False
        elif isinstance(value, dict):
            actual = doc.get(key)
            if "$in" in value and actual not in value["$in"]:
                return False
            if "$regex" in value and not re.search(value["$regex"], actual or "", re.I if value.get("$options") == "i" else 0):
                return False
        elif doc.get(key) != value:
            return False
    return True


class Cursor:
    def __init__(self, docs):
        self.docs = deepcopy(docs)

    def sort(self, *_):
        return self

    def limit(self, count):
        self.docs = self.docs[:count]
        return self

    async def to_list(self, length=None):
        return self.docs[:length] if length else self.docs

    def __aiter__(self):
        async def items():
            for doc in self.docs:
                yield doc
        return items()


class Collection:
    def __init__(self, docs=()):
        self.docs = deepcopy(list(docs))
        self.writes = []

    async def find_one(self, query):
        return deepcopy(next((doc for doc in self.docs if matches(doc, query)), None))

    def find(self, query=None):
        return Cursor([doc for doc in self.docs if matches(doc, query or {})])

    async def insert_one(self, doc):
        saved = deepcopy(doc)
        saved.setdefault("_id", ObjectId())
        self.docs.append(saved)
        self.writes.append(("insert", saved))
        return SimpleNamespace(inserted_id=saved["_id"])

    async def update_one(self, query, update, upsert=False):
        doc = next((doc for doc in self.docs if matches(doc, query)), None)
        self.writes.append(("update", deepcopy(query), deepcopy(update)))
        if doc is None and upsert:
            doc = deepcopy(query)
            doc.setdefault("_id", ObjectId())
            doc.update(deepcopy(update.get("$setOnInsert", {})))
            self.docs.append(doc)
        if doc is not None:
            doc.update(deepcopy(update.get("$set", {})))
        return SimpleNamespace(matched_count=int(doc is not None))

    async def find_one_and_update(self, query, update, **_):
        doc = next((doc for doc in self.docs if matches(doc, query)), None)
        if doc is None:
            return None
        doc.update(deepcopy(update.get("$set", {})))
        self.writes.append(("atomic_update", deepcopy(query), deepcopy(update)))
        return deepcopy(doc)


def person(pid=OWN, **overrides):
    return {"_id": pid, "name": "Mai Tâm" if pid == OWN else "Lan Anh", "student_id": "SV001" if pid == OWN else "SV002",
            "department": "CT01", "is_active": True, "enrolled_at": NOW - timedelta(days=5), **overrides}


def session(**overrides):
    return {"_id": ObjectId(), "label": "Buổi sáng", "department": "CT01", "started_at": NOW,
            "is_active": False, **overrides}


@pytest.fixture(autouse=True)
def refresh_identity_class(monkeypatch):
    # Other test modules reload core.auth; keep isinstance on the current class.
    monkeypatch.setattr(academic, "AuthenticatedUser", auth.AuthenticatedUser)


def make_client(role="student", linked=True, **collections):
    uid = ObjectId()
    user = {"_id": uid, "username": "SV001", "role": role, "is_active": True}
    if linked:
        user["person_id"] = OWN
    defaults = {"users": [user], "persons": [person(), person(OTHER)], "sessions": [], "attendance": [],
                "grades": [], "courses": [], "announcements": [], "leave_requests": []}
    defaults.update(collections)
    db = SimpleNamespace(**{name: Collection(docs) for name, docs in defaults.items()})
    app = FastAPI()
    app.include_router(academic.router, prefix="/api/academic")
    app.dependency_overrides[get_db] = lambda: db
    token, _ = auth.create_access_token(str(uid), "SV001", role)
    return TestClient(app), {"Authorization": f"Bearer {token}"}, db


def test_student_cannot_read_another_grade_using_query_parameter():
    http, headers, _ = make_client(grades=[{"person_id": OWN, "midterm_score": 8}, {"person_id": OTHER, "midterm_score": 1}])
    response = http.get(f"/api/academic/my-grade?person_id={OTHER}", headers=headers)
    assert response.status_code == 200
    assert response.json()["person_id"] == OWN
    assert response.json()["midterm_score"] == 8


def test_unlinked_student_cannot_claim_grade_by_id_or_username():
    http, headers, _ = make_client(linked=False)
    assert http.get(f"/api/academic/my-grade?person_id={OTHER}", headers=headers).json() is None


@pytest.mark.parametrize(("method", "path", "payload"), [
    ("get", "/grades", None),
    ("put", "/grades", {"person_id": OTHER, "midterm_score": 10}),
    ("post", "/courses", {"code": "CS101", "name": "Tin học", "department": "CT01"}),
    ("post", "/announcements", {"title": "Thông báo", "content": "Nội dung"}),
    ("patch", f"/leaves/{ObjectId()}", {"status": "approved"}),
    ("post", "/import-students", {"students": []}),
])
def test_students_cannot_use_operator_endpoints(method, path, payload):
    http, headers, db = make_client()
    kwargs = {"headers": headers}
    if payload is not None:
        kwargs["json"] = payload
    assert getattr(http, method)(f"/api/academic{path}", **kwargs).status_code in (401, 403)
    assert not any(collection.writes for collection in vars(db).values())


def test_courses_and_announcements_follow_students_actual_class():
    courses = [{"_id": ObjectId(), "code": dept, "name": dept, "department": dept, "credits": 3, "created_at": NOW} for dept in ("CT01", "CT02")]
    announcements = [{"_id": ObjectId(), "title": dept or "Chung", "content": "Nội dung", "department": dept,
                      "priority": "normal", "author": "GV", "created_at": NOW} for dept in (None, "CT01", "CT02")]
    http, headers, _ = make_client(courses=courses, announcements=announcements)
    assert [row["department"] for row in http.get("/api/academic/courses?department=CT02", headers=headers).json()] == ["CT01"]
    assert [row["department"] for row in http.get("/api/academic/announcements?department=CT02", headers=headers).json()] == [None, "CT01"]


def test_student_leave_creation_and_list_are_pinned_to_own_profile():
    http, headers, db = make_client()
    response = http.post(f"/api/academic/leaves?person_id={OTHER}", headers=headers,
                         json={"leave_date": "2026-10-23", "reason": "Khám bệnh"})
    assert response.status_code == 201
    assert response.json()["person_id"] == OWN
    db.leave_requests.docs.append({**db.leave_requests.docs[0], "_id": ObjectId(), "person_id": OTHER})
    assert [row["person_id"] for row in http.get("/api/academic/leaves", headers=headers).json()] == [OWN]


@pytest.mark.parametrize("leave_date", ["2026-02-30", "tomorrow", "20261023", "2026-10-23T09:00:00Z"])
def test_invalid_leave_dates_do_not_write(leave_date):
    http, headers, db = make_client()
    result = http.post("/api/academic/leaves", headers=headers, json={"leave_date": leave_date, "reason": "Khám bệnh"})
    assert result.status_code == 422
    assert db.leave_requests.writes == []


@pytest.mark.parametrize("changes", [{"department": "CT02"}, {"started_at": NOW - timedelta(days=1)}])
def test_leave_session_must_belong_to_student_class_and_leave_day(changes):
    sess = session(**changes)
    http, headers, db = make_client(sessions=[sess])
    result = http.post("/api/academic/leaves", headers=headers,
                       json={"session_id": str(sess["_id"]), "leave_date": "2026-10-23", "reason": "Khám bệnh"})
    assert result.status_code == 422
    assert db.leave_requests.writes == []


def pending_leave(sess):
    return {"_id": ObjectId(), "person_id": OWN, "person_name": "Mai Tâm", "student_id": "SV001", "department": "CT01",
            "session_id": str(sess["_id"]), "session_label": sess["label"], "leave_date": "2026-10-23",
            "reason": "Khám bệnh", "status": "pending", "created_at": NOW, "reviewed_at": None}


@pytest.mark.parametrize("status", ["present", "late", "excused", None])
def test_leave_approval_preserves_real_attendance_and_legacy_records(status):
    sess = session()
    leave = pending_leave(sess)
    record = {"_id": ObjectId(), "person_id": OWN, "session_id": sess["_id"], "confidence": .98, "marked_at": NOW}
    if status is not None:
        record["status"] = status
    http, headers, db = make_client("operator", sessions=[sess], leave_requests=[leave], attendance=[record])
    response = http.patch(f"/api/academic/leaves/{leave['_id']}", headers=headers, json={"status": "approved"})
    assert response.status_code == 200
    assert db.attendance.docs == [record]
    assert db.attendance.writes == []
    assert http.patch(f"/api/academic/leaves/{leave['_id']}", headers=headers, json={"status": "rejected"}).status_code == 409
    assert db.leave_requests.docs[0]["status"] == "approved"


@pytest.mark.parametrize("existing", [True, False])
def test_leave_approval_excuses_absence_without_duplicate_legacy_session(existing):
    sess = session()
    leave = pending_leave(sess)
    records = [{"_id": ObjectId(), "person_id": OWN, "session_id": str(sess["_id"]), "status": "absent"}] if existing else []
    http, headers, db = make_client("operator", sessions=[sess], leave_requests=[leave], attendance=records)
    result = http.patch(f"/api/academic/leaves/{leave['_id']}", headers=headers, json={"status": "approved"})
    assert result.status_code == 200
    assert len(db.attendance.docs) == 1
    assert db.attendance.docs[0]["status"] == "excused"
    assert db.attendance.docs[0]["leave_request_id"] == str(leave["_id"])


def test_lost_review_race_does_not_touch_attendance(monkeypatch):
    sess = session()
    leave = pending_leave(sess)
    http, headers, db = make_client("operator", sessions=[sess], leave_requests=[leave])
    async def lost_race(*_, **__):
        return None
    monkeypatch.setattr(db.leave_requests, "find_one_and_update", lost_race)
    assert http.patch(f"/api/academic/leaves/{leave['_id']}", headers=headers, json={"status": "approved"}).status_code == 409
    assert db.attendance.writes == []


def test_failed_attendance_write_returns_leave_to_pending(monkeypatch):
    sess = session()
    leave = pending_leave(sess)
    http, headers, db = make_client("operator", sessions=[sess], leave_requests=[leave])
    async def unavailable(*_, **__):
        raise RuntimeError("simulated database failure")
    monkeypatch.setattr(db.attendance, "update_one", unavailable)
    with pytest.raises(RuntimeError, match="simulated database failure"):
        http.patch(f"/api/academic/leaves/{leave['_id']}", headers=headers, json={"status": "approved"})
    assert db.leave_requests.docs[0]["status"] == "pending"
    assert db.leave_requests.docs[0]["reviewed_at"] is None


def test_rejecting_a_leave_never_changes_attendance():
    sess = session()
    leave = pending_leave(sess)
    http, headers, db = make_client("operator", sessions=[sess], leave_requests=[leave])
    response = http.patch(f"/api/academic/leaves/{leave['_id']}", headers=headers, json={"status": "rejected"})
    assert response.status_code == 200
    assert db.attendance.writes == []


def test_grade_rate_excludes_other_classes_pre_enrollment_and_open_sessions():
    closed = session()
    excused = session()
    other_class = session(department="CT02")
    before_enrollment = session(started_at=NOW - timedelta(days=10))
    open_session = session(is_active=True)
    attendance = [{"person_id": OWN, "session_id": closed["_id"]}, {"person_id": OWN, "session_id": excused["_id"], "status": "excused"}]
    http, headers, _ = make_client(sessions=[closed, excused, other_class, before_enrollment, open_session], attendance=attendance,
                                 grades=[{"person_id": OWN, "midterm_score": 8, "final_score": 8}])
    row = http.get("/api/academic/my-grade", headers=headers).json()
    assert (row["total_sessions"], row["present_count"], row["attendance_rate"]) == (2, 2, 100)
    assert row["total_10"] == 8.2
    assert row["exam_eligible"] is True


def test_bulk_import_never_merges_a_different_student_by_same_name():
    http, headers, db = make_client("operator")
    original = deepcopy(db.persons.docs)
    response = http.post("/api/academic/import-students", headers=headers,
                         json={"students": [{"student_id": "SV999", "name": "Mai Tâm", "department": "CT02"}], "create_login_accounts": False})
    assert response.status_code == 200
    assert db.persons.docs[:len(original)] == original
    assert db.persons.docs[-1]["student_id"] == "SV999"
    assert db.persons.docs[-1]["_id"] not in [p["_id"] for p in original]


@pytest.mark.parametrize("bad_row", [
    {"student_id": "sv003", "name": "Trùng mã", "department": "CT01"},
    {"student_id": "SV004", "name": "  ", "department": "CT01"},
    {"student_id": "SV004", "name": "Lan Anh", "department": "  "},
])
def test_bulk_import_checks_later_rows_before_any_write(bad_row):
    http, headers, db = make_client("operator")
    rows = [{"student_id": "SV003", "name": "Sinh viên mới", "department": "CT01"}, bad_row]
    response = http.post("/api/academic/import-students", headers=headers, json={"students": rows, "create_login_accounts": False})
    assert response.status_code in (409, 422)
    assert db.persons.writes == []
    assert db.users.writes == []


def test_bulk_import_updates_by_id_and_preserves_existing_face():
    own = person(photo_url="/uploads/own.jpg")
    http, headers, db = make_client("operator", persons=[own])
    result = http.post("/api/academic/import-students", headers=headers,
                       json={"students": [{"student_id": "sv001", "name": "Tên đã sửa", "department": "CT02"}], "create_login_accounts": False})
    assert result.status_code == 200
    assert result.json() == {"created": 0, "updated": 1, "accounts_created": 0, "total_processed": 1, "credentials": []}
    assert db.persons.docs[0]["_id"] == OWN
    assert db.persons.docs[0]["name"] == "Tên đã sửa"
    assert db.persons.docs[0]["photo_url"] == "/uploads/own.jpg"


def test_bulk_import_does_not_relink_an_existing_account():
    http, headers, db = make_client("operator")
    # The current operator username collides with the incoming student's MSSV.
    db.users.docs[0]["person_id"] = OTHER
    result = http.post("/api/academic/import-students", headers=headers,
                       json={"students": [{"student_id": "SV001", "name": "Mai Tâm", "department": "CT01"}]})
    assert result.status_code == 409
    assert db.users.writes == []
    assert db.persons.writes == []


def test_bulk_import_duplicate_google_emails_fail_before_profiles_are_written():
    http, headers, db = make_client("operator")
    rows = [{"student_id": "SV003", "name": "Minh Châu", "department": "CT01", "email": "same@school.edu.vn"},
            {"student_id": "SV004", "name": "Thành An", "department": "CT01", "email": "Same@school.edu.vn"}]
    result = http.post("/api/academic/import-students", headers=headers, json={"students": rows})
    assert result.status_code == 409
    assert db.persons.writes == []
    assert db.users.writes == []


def test_operator_can_create_announcement_without_optional_display_name_attribute():
    http, headers, _ = make_client("operator")
    result = http.post("/api/academic/announcements", headers=headers, json={"title": "Lịch thi", "content": "Lịch thi mới"})
    assert result.status_code == 201
    assert result.json()["author"] == "SV001"
