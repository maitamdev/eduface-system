"""Run with MONGODB_INTEGRATION_URI pointing to an isolated localhost replica set.

Each test creates and drops only its own randomly named eduface_integration_* DB.
AI image recognition remains mocked; indexes, HTTP routes, transactions and storage are real.
"""
import os
import uuid
from datetime import datetime, timezone
from urllib.parse import urlsplit
from unittest.mock import AsyncMock
import httpx
import pytest
import pytest_asyncio
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from pymongo.errors import OperationFailure, DuplicateKeyError

URI = os.getenv("MONGODB_INTEGRATION_URI", "")
pytestmark = pytest.mark.skipif(not URI, reason="Set MONGODB_INTEGRATION_URI for the local replica-set integration suite")


@pytest_asyncio.fixture
async def live(monkeypatch):
    assert urlsplit(URI).hostname in {"127.0.0.1", "localhost"}, "Integration tests only target localhost"
    from core import database, auth, azure_face
    from core.rate_limit import limiter
    from main import app
    client = AsyncIOMotorClient(URI, tz_aware=True, serverSelectionTimeoutMS=3000)
    name = "eduface_integration_" + uuid.uuid4().hex
    monkeypatch.setattr(database, "_client", client)
    monkeypatch.setattr(database, "DB_NAME", name)
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("DEFAULT_ADMIN_PASSWORD", "integration-password-only")
    monkeypatch.setenv("SEED_DEMO_ACCOUNTS", "false")
    monkeypatch.setattr(auth, "ADMIN_API_KEYS", {"integration-admin-key"})
    limiter.reset()
    await database.init_db()
    app.state.database_initialized = True
    db = client[name]
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app, raise_app_exceptions=False), base_url="http://test", headers={"X-API-Key": "integration-admin-key"}) as http:
        yield db, http
    assert name.startswith("eduface_integration_")
    await client.drop_database(name)
    azure_face.invalidate_cache()
    client.close()


@pytest.mark.asyncio
async def test_import_transaction_rolls_back_profile_when_account_write_fails(live, monkeypatch):
    db, http = live
    original = AsyncIOMotorCollection.insert_one
    async def failing(self, doc, *args, **kwargs):
        if self.name == "users" and doc.get("role") == "student":
            raise OperationFailure("Injected storage failure", code=123)
        return await original(self, doc, *args, **kwargs)
    monkeypatch.setattr(AsyncIOMotorCollection, "insert_one", failing)
    result = await http.post("/api/academic/import-students", json={"students": [{"student_id": "SV001", "name": "Student", "department": "CS"}]})
    assert result.status_code == 503, result.text
    assert await db.persons.count_documents({}) == 0
    assert await db.users.count_documents({"role": "student"}) == 0


@pytest.mark.asyncio
async def test_close_transaction_rolls_back_and_retry_is_idempotent(live, monkeypatch):
    db, http = live
    await db.persons.insert_one({"_id": "p", "name": "Student", "is_active": True, "department": "CS"})
    opened = await http.post("/api/sessions", json={"label": "Class session", "department": "CS"})
    assert opened.status_code == 201, opened.text
    sid = opened.json()["id"]
    original = AsyncIOMotorCollection.insert_one
    async def failing(self, doc, *args, **kwargs):
        if self.name == "attendance": raise OperationFailure("Injected storage failure", code=123)
        return await original(self, doc, *args, **kwargs)
    with monkeypatch.context() as context:
        context.setattr(AsyncIOMotorCollection, "insert_one", failing)
        result = await http.patch(f"/api/sessions/{sid}/end")
        assert result.status_code == 503, result.text
        assert (await db.sessions.find_one({"_id": ObjectId(sid)}))["is_active"] is True
    assert (await http.patch(f"/api/sessions/{sid}/end")).status_code == 200
    assert (await http.patch(f"/api/sessions/{sid}/end")).status_code == 200
    assert await db.attendance.count_documents({"session_id": ObjectId(sid)}) == 1


@pytest.mark.asyncio
async def test_real_unique_identity_index_blocks_case_variant_but_allows_same_name(live):
    db, _ = live
    await db.persons.insert_one({"_id": "one", "name": "Same", "student_id": "SV001", "is_active": True})
    with pytest.raises(DuplicateKeyError):
        await db.persons.insert_one({"_id": "two", "name": "Other", "student_id": "sv001", "is_active": True})
    await db.persons.insert_one({"_id": "three", "name": "Same", "student_id": "SV002", "is_active": True})
    assert await db.persons.count_documents({"name": "Same"}) == 2


@pytest.mark.asyncio
async def test_live_course_grade_report_transfer_and_dashboard(live):
    db, http = live
    await db.persons.insert_one({"_id": "p", "name": "Student", "is_active": True, "department": "CS", "enrolled_at": datetime(2025, 1, 1, tzinfo=timezone.utc)})
    course = await http.post("/api/academic/courses", json={"code": "CS01", "name": "Computer Science", "department": "CS"})
    assert course.status_code == 201, course.text
    cid = course.json()["id"]
    for _ in range(2):
        opened = await http.post("/api/sessions", json={"label": "CS lecture", "course_id": cid})
        sid = opened.json()["id"]
        mark = await http.put("/api/attendance/manual", json={"person_id": "p", "session_id": sid, "status": "late"})
        assert mark.status_code == 200, mark.text
        assert (await http.patch(f"/api/sessions/{sid}/end")).status_code == 200
    grade = await http.put("/api/academic/grades", json={"person_id": "p", "course_id": cid, "midterm_score": 8, "final_score": 9})
    assert grade.status_code == 200, grade.text
    assert grade.json()["total_10"] == 8.8
    metrics = (await http.get("/api/dashboard/metrics")).json()
    assert metrics["present_today"] == 1 and metrics["attendance_rate"] == 100
    await db.persons.update_one({"_id": "p"}, {"$set": {"department": "ART"}})
    historical = (await http.get(f"/api/academic/grades?course_id={cid}")).json()
    assert historical[0]["total_sessions"] == 2
    report = (await http.get("/api/reports/persons?department=CS")).json()
    assert report[0]["present_count"] == 2
    assert await db.audit_logs.count_documents({}) >= 5


@pytest.mark.asyncio
async def test_csv_exports_more_than_ten_thousand_rows_and_filters_first(live):
    db, http = live
    sid = ObjectId(); now = datetime.now(timezone.utc)
    await db.sessions.insert_one({"_id": sid, "label": "Large session", "started_at": now})
    await db.persons.insert_many([{"_id": str(i), "name": "=FORMULA", "department": "CS"} for i in range(10005)])
    await db.attendance.insert_many([{"person_id": str(i), "session_id": sid, "marked_at": now, "status": "present"} for i in range(10005)])
    result = await http.get("/api/attendance/export/csv?department=CS")
    assert result.status_code == 200, result.text[:500]
    import csv, io
    rows = list(csv.reader(io.StringIO(result.text.lstrip("\ufeff"))))
    assert len(rows) == 10006
    assert rows[1][2].startswith("'")


@pytest.mark.asyncio
async def test_password_change_revokes_old_token_and_login_is_throttled(live):
    db, http = live
    from core.auth import hash_password
    await db.users.insert_one({"username": "student", "password_hash": hash_password("old-password-123"), "role": "student", "is_active": True, "created_at": datetime.now(timezone.utc)})
    login = await http.post("/api/auth/login", json={"username": "student", "password": "old-password-123"})
    assert login.status_code == 200, login.text
    old = login.json()["access_token"]
    changed = await http.post("/api/auth/password", headers={"Authorization": f"Bearer {old}"}, json={"current_password": "old-password-123", "new_password": "new-password-456"})
    assert changed.status_code == 200, changed.text
    assert (await http.get("/api/auth/me", headers={"Authorization": f"Bearer {old}"})).status_code == 401
    assert (await http.get("/api/auth/me", headers={"Authorization": f"Bearer {changed.json()['access_token']}"})).status_code == 200
    for _ in range(6):
        result = await http.post("/api/auth/login", json={"username": "student", "password": "wrong-password"})
    assert result.status_code == 429


@pytest.mark.asyncio
async def test_migration_preserves_history_and_blocks_ambiguous_duplicates(live):
    from scripts.migrate_integrity import migrate, plan
    db, http = live
    sid = ObjectId()
    await db.persons.insert_one({"_id": "p", "name": "Same Name", "student_id": " old01 ", "is_active": True})
    await db.attendance.insert_one({"person_id": "p", "session_id": str(sid), "status": "present"})
    await db.grades.insert_one({"person_id": "p", "final_exam": 9})
    result = await migrate(db)
    assert not any(result["collisions"].values()) and result["unassigned_grades"] == 1
    assert (await db.persons.find_one({"_id": "p"}))["student_id"] == "OLD01"
    assert (await db.attendance.find_one({"person_id": "p"}))["session_id"] == sid
    # The old string and ObjectId representations may both exist under the old index.
    await db.attendance.insert_one({"person_id": "p", "session_id": str(sid), "status": "absent"})
    with pytest.raises(ValueError): await migrate(db)
    assert await db.attendance.count_documents({}) == 2


@pytest.mark.asyncio
async def test_legacy_attendance_visible_in_list_and_manual_update(live):
    db, http = live
    now = datetime.now(timezone.utc); sid = ObjectId()
    await db.persons.insert_one({"_id": "p", "name": "Student", "department": "CS", "is_active": True})
    await db.sessions.insert_one({"_id": sid, "label": "Legacy", "department": "CS", "started_at": now, "is_active": False})
    await db.attendance.insert_one({"person_id": "p", "session_id": str(sid), "marked_at": now, "status": "present", "confidence": .8})
    response = await http.get("/api/attendance", params={"session_id": str(sid)})
    assert response.status_code == 200 and response.json()[0]["session_label"] == "Legacy"
    response = await http.put("/api/attendance/manual", json={"person_id": "p", "session_id": str(sid), "status": "late"})
    assert response.status_code == 200, response.text
    assert await db.attendance.count_documents({}) == 1


@pytest.mark.asyncio
async def test_concurrent_marks_preserve_one_record_and_can_retry(live, monkeypatch):
    import asyncio
    from core import azure_face
    from routers import attendance
    db, http = live
    await db.persons.insert_one({"_id": "concurrent-person", "name": "Test", "department": "CS", "is_active": True})
    opened = await http.post("/api/sessions", json={"label": "Concurrent", "department": "CS"})
    sid = opened.json()["id"]
    monkeypatch.setattr(attendance, "read_and_validate_image", AsyncMock(return_value=b"validated"))
    monkeypatch.setattr(azure_face, "identify_faces", AsyncMock(return_value=[{
        "azure_person_id": "concurrent-person", "name": "Test", "confidence": .9, "is_live": True,
        "face_box": {"left": 0, "top": 0, "width": 10, "height": 10}}]))
    async def mark():
        return await http.post(f"/api/attendance/mark/{sid}", files={"frame": ("f.jpg", b"image", "image/jpeg"), "probe_frame": ("p.jpg", b"probe", "image/jpeg")})
    responses = await asyncio.gather(*(mark() for _ in range(4)))
    assert all(r.status_code in {200, 503} for r in responses), [r.text for r in responses]
    for result in responses:
        if result.status_code == 503: assert (await mark()).status_code == 200
    assert await db.attendance.count_documents({"person_id": "concurrent-person"}) == 1
