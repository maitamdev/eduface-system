"""Regression checks for the October audit findings; synthetic data only."""
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock
import numpy as np
import pytest
from bson import ObjectId
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from mongomock_motor import AsyncMongoMockClient
from core import auth, azure_face
from core.database import get_db, get_write_db, count_present_today
from core.attendance_policy import session_applies_to_person
from core.origins import allowed_origins
from core.rate_limit import limiter
from routers import persons, academic, sessions, attendance


@pytest.fixture
def memory_db():
    return AsyncMongoMockClient(tz_aware=True).db


def client_for(db, role="student", account=None):
    app = FastAPI()
    app.state.limiter = limiter
    limiter.reset()
    for module, prefix in [(persons, "persons"), (academic, "academic"), (sessions, "sessions"), (attendance, "attendance")]:
        app.include_router(module.router, prefix=f"/api/{prefix}")
    async def identity(request: Request):
        request.state.user = auth.AuthenticatedUser(str(account or ObjectId()), "test-user", role, "jwt")
        return request.state.user
    for dependency in (auth.require_authenticated, auth.require_operator, auth.require_admin):
        app.dependency_overrides[dependency] = identity
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_write_db] = lambda: db
    persons.AuthenticatedUser = auth.AuthenticatedUser
    academic.AuthenticatedUser = auth.AuthenticatedUser
    return TestClient(app)


@pytest.fixture
def face_service(monkeypatch):
    monkeypatch.setattr(persons, "read_and_validate_image", AsyncMock(return_value=b"photo"))
    monkeypatch.setattr(azure_face, "ensure_person_group", AsyncMock())
    monkeypatch.setattr(azure_face, "check_duplicate_face", AsyncMock(return_value=None))
    monkeypatch.setattr(azure_face, "upload_photo_to_blob", AsyncMock(return_value=""))
    async def enroll(name, images, existing_person_id=None):
        return existing_person_id or "new-person"
    monkeypatch.setattr(azure_face, "enroll_person", enroll)


@pytest.mark.asyncio
async def test_self_enroll_uses_account_link_and_preserves_academic_identity(memory_db, face_service):
    uid = ObjectId(); original = datetime(2025, 1, 1, tzinfo=timezone.utc)
    await memory_db.users.insert_one({"_id": uid, "person_id": "mine", "is_active": True})
    await memory_db.persons.insert_one({"_id": "mine", "name": "Original", "student_id": "SV01", "department": "A", "email": "own@example.test", "is_active": True, "enrolled_at": original})
    http = client_for(memory_db, account=uid)
    response = http.post("/api/persons/self-enroll", data={"consent": "true", "name": "Changed", "student_id": "SV999", "department": "B", "email": "other@example.test"}, files={"photos": ("p.jpg", b"x", "image/jpeg")})
    assert response.status_code == 201, response.text
    saved = await memory_db.persons.find_one({"_id": "mine"})
    assert saved["enrolled_at"] == original
    assert saved["name"] == "Original" and saved["student_id"] == "SV01" and saved["department"] == "A"
    assert saved["face_updated_at"] > original


@pytest.mark.asyncio
async def test_self_enroll_cannot_claim_existing_profile_by_email(memory_db, face_service):
    uid = ObjectId()
    await memory_db.users.insert_one({"_id": uid, "is_active": True})
    await memory_db.persons.insert_one({"_id": "victim", "name": "Victim", "student_id": "SV01", "department": "A", "email": "victim@example.test", "is_active": True, "enrolled_at": datetime.now(timezone.utc)})
    response = client_for(memory_db, account=uid).post("/api/persons/self-enroll", data={"consent": "true", "name": "Attacker", "student_id": "SV01", "department": "A", "email": "victim@example.test"}, files={"photos": ("p.jpg", b"x", "image/jpeg")})
    assert response.status_code == 409
    assert (await memory_db.users.find_one({"_id": uid})).get("person_id") is None


@pytest.mark.asyncio
async def test_admin_refresh_keeps_enrollment_day_and_same_name_is_not_identity(memory_db, face_service):
    original = datetime(2025, 1, 1, tzinfo=timezone.utc)
    await memory_db.persons.insert_one({"_id": "mine", "name": "Same Name", "student_id": "SV01", "department": "A", "is_active": True, "enrolled_at": original})
    http = client_for(memory_db, "admin")
    response = http.post("/api/persons/enroll", data={"consent": "true", "name": "Same Name", "student_id": "SV01"}, files={"photos": ("p.jpg", b"x", "image/jpeg")})
    assert response.status_code == 201, response.text
    assert (await memory_db.persons.find_one({"_id": "mine"}))["enrolled_at"] == original
    response = http.post("/api/persons/enroll", data={"consent": "true", "name": "Same Name", "student_id": "SV02"}, files={"photos": ("p.jpg", b"x", "image/jpeg")})
    assert response.status_code == 201
    assert await memory_db.persons.count_documents({"name": "Same Name"}) == 2


def test_snapshot_roster_survives_transfer_and_rejects_new_classmate():
    session = {"roster_ids": ["existing"], "department": "A"}
    assert session_applies_to_person(session, {"_id": "existing", "department": "B"})
    assert not session_applies_to_person(session, {"_id": "new", "department": "A"})


@pytest.mark.asyncio
async def test_dashboard_counts_unique_active_people_with_late_and_excused(memory_db):
    await memory_db.persons.insert_many([{"_id": "a", "is_active": True}, {"_id": "b", "is_active": True}, {"_id": "deleted", "is_active": False}])
    for pid, state in [("a", "present"), ("a", "late"), ("b", "excused"), ("deleted", "present")]:
        await memory_db.attendance.insert_one({"person_id": pid, "status": state, "marked_at": datetime.now(timezone.utc)})
    assert await count_present_today(memory_db) == 2


@pytest.mark.asyncio
async def test_course_grades_are_isolated_and_legacy_writes_are_rejected(memory_db):
    await memory_db.persons.insert_one({"_id": "p", "name": "Student", "is_active": True, "department": "A"})
    c1, c2 = ObjectId(), ObjectId()
    for cid in [c1, c2]:
        await memory_db.courses.insert_one({"_id": cid, "department": "A", "name": str(cid), "credits": 3, "semester": "HK1"})
    http = client_for(memory_db, "operator")
    for cid, score in [(c1, 9), (c2, 4)]:
        response = http.put("/api/academic/grades", json={"person_id": "p", "course_id": str(cid), "midterm_score": score, "final_score": score})
        assert response.status_code == 200, response.text
        assert response.json()["midterm_score"] == score
    assert await memory_db.grades.count_documents({"person_id": "p"}) == 2
    assert http.put("/api/academic/grades", json={"person_id": "p"}).status_code == 422
    assert http.get(f"/api/academic/grades?course_id={c1}").json()[0]["midterm_score"] == 9


@pytest.mark.asyncio
async def test_import_issues_unique_passwords_and_allows_same_names(memory_db):
    response = client_for(memory_db, "operator").post("/api/academic/import-students", json={"students": [{"student_id": "SV001", "name": "Same Name", "department": "A"}, {"student_id": "SV002", "name": "Same Name", "department": "A"}]})
    assert response.status_code == 200, response.text
    passwords = [x["password"] for x in response.json()["credentials"]]
    assert len(set(passwords)) == 2 and min(map(len, passwords)) >= 20
    for credential in response.json()["credentials"]:
        user = await memory_db.users.find_one({"username": credential["username"]})
        assert auth.verify_password(credential["password"], user["password_hash"])


def test_untrusted_vercel_origin_not_allowed(monkeypatch):
    monkeypatch.setenv("ALLOWED_ORIGINS", "https://school.example")
    assert allowed_origins() == ["https://school.example"]
    for value in ["*", "https://*.vercel.app", "https://school.example/path"]:
        monkeypatch.setenv("ALLOWED_ORIGINS", value)
        with pytest.raises(RuntimeError): allowed_origins()


def test_liveness_rejects_uniform_images_invalid_crops_and_exceptions():
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    face = SimpleNamespace(bbox=np.array([10, 10, 90, 90]))
    assert azure_face._check_liveness(frame, face)["is_live"] is False
    assert azure_face._check_liveness(frame, object())["is_live"] is False
    assert azure_face._check_liveness(frame, SimpleNamespace(bbox=np.array([120, 120, 150, 150])))["is_live"] is False
    assert azure_face._check_multiframe_motion(frame, face, None)[0] is False
    assert azure_face._check_multiframe_motion(frame, face, frame)[0] is False


@pytest.mark.asyncio
async def test_server_threshold_cannot_be_lowered_by_client(monkeypatch):
    from tests.conftest import FakeFace, FakeInsightApp
    monkeypatch.setenv("MIN_CONFIDENCE", "0.7")
    monkeypatch.setattr(azure_face, "_load_all", AsyncMock(return_value={"p": {"name": "Person", "embeddings": [np.array([1., 0.])]}}))
    monkeypatch.setattr(azure_face, "_get_insight_app", lambda: FakeInsightApp(default_faces=[FakeFace([0.6, 0.8], [10, 10, 90, 90])]))
    monkeypatch.setattr(azure_face, "_bytes_to_bgr", lambda _: np.zeros((100, 100, 3), dtype=np.uint8))
    assert await azure_face.identify_faces(b"image", 0.1) == []
    assert azure_face._calibrate_confidence(0.4) == 0.4


@pytest.mark.asyncio
async def test_cache_is_used_and_invalidated(memory_db, monkeypatch):
    monkeypatch.setattr(azure_face, "get_database", lambda: memory_db)
    azure_face.invalidate_cache()
    await memory_db.face_encodings.insert_one({"_id": "p", "name": "Person", "embeddings": [[1., 0.]]})
    first = await azure_face._load_all()
    assert await azure_face._load_all() is first
    await azure_face._upsert_person("new", "New", [np.array([0., 1.])])
    assert len(await azure_face._load_all()) == 2
    azure_face.invalidate_cache()


@pytest.mark.asyncio
async def test_manual_correction_preserves_original_scan_timestamp(memory_db):
    sid, aid = ObjectId(), ObjectId(); before = datetime(2025, 1, 1, tzinfo=timezone.utc)
    await memory_db.persons.insert_one({"_id": "p", "name": "Person", "is_active": True})
    await memory_db.sessions.insert_one({"_id": sid, "label": "Session", "roster_ids": ["p"]})
    await memory_db.attendance.insert_one({"_id": aid, "person_id": "p", "session_id": sid, "marked_at": before, "status": "present"})
    response = client_for(memory_db, "operator").put("/api/attendance/manual", json={"person_id": "p", "session_id": str(sid), "status": "excused"})
    assert response.status_code == 200, response.text
    stored = await memory_db.attendance.find_one({"_id": aid})
    assert stored["marked_at"] == before and stored["updated_at"] > before


@pytest.mark.asyncio
async def test_google_does_not_link_by_mutable_contact_email(memory_db, monkeypatch):
    from routers import google_auth
    monkeypatch.setattr(google_auth, "require_google_configuration", lambda: {"enabled": True})
    monkeypatch.setattr(google_auth, "verify_google_id_token", lambda *_: {"email": "attacker@example.test", "name": "New"})
    await memory_db.persons.insert_one({"_id": "victim", "email": "attacker@example.test", "is_active": True})
    await memory_db.users.insert_one({"username": "victim", "role": "admin", "person_id": "victim", "is_active": True})
    app = FastAPI(); app.state.limiter = limiter; limiter.reset()
    app.include_router(google_auth.router, prefix="/api/auth")
    app.dependency_overrides[get_db] = lambda: memory_db
    response = TestClient(app).post("/api/auth/google", json={"id_token": "synthetic-token"})
    assert response.status_code == 200, response.text
    assert response.json()["role"] == "student"
    account = await memory_db.users.find_one({"google_email": "attacker@example.test"})
    assert account["person_id"] is None


@pytest.mark.asyncio
async def test_biometric_delete_keeps_academic_history_and_queues_photo_cleanup(memory_db):
    await memory_db.persons.insert_one({"_id": "p", "name": "Person", "is_active": True, "photo_url": "https://example.test/photo.jpg"})
    await memory_db.face_encodings.insert_one({"_id": "p", "embeddings": [[1., 0.]]})
    await memory_db.attendance.insert_one({"person_id": "p", "session_id": ObjectId(), "status": "present"})
    from unittest.mock import patch
    with patch.object(azure_face, "get_database", lambda: memory_db):
        response = client_for(memory_db, "admin").delete("/api/persons/p")
    assert response.status_code == 204, response.text
    assert await memory_db.face_encodings.count_documents({}) == 0
    assert await memory_db.attendance.count_documents({}) == 1
    job = await memory_db.biometric_cleanup.find_one({"_id": "p"})
    assert job["status"] == "pending" and job["has_photo"]


def test_similarity_evaluation_reports_errors_without_claiming_accuracy():
    from scripts.evaluate_similarity import evaluate
    result = evaluate([{ "genuine": "1", "similarity": .8 }, { "genuine": "1", "similarity": .2 },
                       { "genuine": "0", "similarity": .6 }, { "genuine": "0", "similarity": .1 }], .4)
    assert result["false_acceptance_rate"] == .5 and result["false_rejection_rate"] == .5
    with pytest.raises(ValueError): evaluate([{ "genuine": "1", "similarity": .8 }], .4)


def test_local_mongodb_does_not_force_tls(monkeypatch):
    from core import database
    monkeypatch.setattr(database, "_client", None)
    monkeypatch.setattr(database, "MONGO_URL", "mongodb://127.0.0.1:27028")
    client = database.get_client()
    assert client.delegate.options.pool_options._ssl_context is None
    client.close()
