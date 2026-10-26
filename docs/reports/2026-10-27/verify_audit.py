"""Read-only audit reproductions. Uses synthetic data, no real DB/model/network."""
import os
import sys
import json
import asyncio
import inspect
from pathlib import Path
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

ROOT = Path(__file__).resolve().parents[3]
os.environ.update(MONGODB_URL="mongodb://127.0.0.1:27017/attendance_audit_test",
                  MONGODB_DB_NAME="attendance_audit_test", APP_ENV="test",
                  API_KEY="audit-synthetic-key", JWT_SECRET="audit-local-synthetic-secret-not-a-real-credential")
sys.path.insert(0, str(ROOT / "backend"))
import numpy as np
from fastapi import FastAPI, Request
from httpx import AsyncClient, ASGITransport
from core.auth import AuthenticatedUser, require_authenticated, require_operator
from core.database import get_db
from core import azure_face
from core.attendance_policy import session_applies_to_person
from routers import persons, dashboard, attendance

results = {}

async def run():
    user = AuthenticatedUser("000000000000000000000001", "synthetic-student", "student")
    req = Request({"type": "http", "method": "POST", "path": "/", "headers": [],
                   "client": ("127.0.0.1", 1234), "state": {"user": user}})
    with patch.object(persons, "read_and_validate_image", AsyncMock(return_value=b"synthetic")), \
         patch.object(azure_face, "ensure_person_group", AsyncMock()):
        try:
            await inspect.unwrap(persons.self_enroll_student)(
                request=req, name="Synthetic Student", student_id="TEST001", department="A",
                email="synthetic@example.invalid", photos=[object()], db=SimpleNamespace())
            results["self_enroll"] = {"unexpected_success": True}
        except Exception as exc:
            results["self_enroll"] = {"error_type": type(exc).__name__, "message": str(exc)}

    existing = {"_id": "synthetic-person", "name": "Synthetic Student", "department": "A",
                "student_id": "TEST001", "is_active": True,
                "enrolled_at": datetime(2026, 9, 1, tzinfo=timezone.utc)}
    session = {"started_at": datetime(2026, 10, 1, tzinfo=timezone.utc), "department": "A"}
    collection = SimpleNamespace(find_one=AsyncMock(return_value=dict(existing)), update_one=AsyncMock())
    with patch.object(persons, "read_and_validate_image", AsyncMock(return_value=b"synthetic")), \
         patch.object(azure_face, "ensure_person_group", AsyncMock()), \
         patch.object(azure_face, "check_duplicate_face", AsyncMock(return_value=None)), \
         patch.object(azure_face, "enroll_person", AsyncMock(return_value=existing["_id"])), \
         patch.object(azure_face, "upload_photo_to_blob", AsyncMock(return_value="")):
        await inspect.unwrap(persons.enroll_person)(
            request=req, name=existing["name"], student_id=None, email=None, department=None,
            student_username=None, student_password=None,
            photos=[SimpleNamespace(filename="synthetic.jpg")], db=SimpleNamespace(persons=collection))
        updates = collection.update_one.await_args.args[1]["$set"]
        results["reenrollment_history"] = {
            "before": session_applies_to_person(session, existing),
            "after": session_applies_to_person(session, {**existing, **updates}),
            "enrolled_at_overwritten": updates["enrolled_at"] != existing["enrolled_at"],
        }

    with patch.object(dashboard, "count_persons", AsyncMock(return_value=10)), \
         patch.object(dashboard, "count_sessions_today", AsyncMock(return_value=2)), \
         patch.object(dashboard, "count_present_today", AsyncMock(return_value=20)):
        results["dashboard_two_sessions"] = (await dashboard.get_metrics(db=object())).model_dump()

    results["confidence_mapping"] = [{"raw": score, "displayed": round(azure_face._calibrate_confidence(score), 4)}
                                      for score in (0.38, 0.40, 0.45, 0.55, 0.8)]
    face = SimpleNamespace(bbox=np.array([10, 10, 90, 90]), det_score=.9)
    results["liveness_uniform_image"] = azure_face._check_liveness(np.zeros((100, 100, 3), dtype=np.uint8), face)
    results["liveness_exception"] = azure_face._check_liveness(np.zeros((100, 100, 3), dtype=np.uint8), object())
    results["liveness_without_probe"] = azure_face._check_multiframe_motion(np.zeros((100, 100, 3), dtype=np.uint8), face, None)

    # Exercise SDK's actual advertised paths without contacting any backend.
    app = FastAPI()
    app.include_router(attendance.router, prefix="/api/attendance")
    async def allow_operator():
        return True
    app.dependency_overrides[require_operator] = allow_operator
    app.dependency_overrides[get_db] = lambda: object()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://audit.invalid") as client:
        wrong_field = await client.post("/api/attendance/identify", files={"photo": ("a.jpg", b"synthetic", "image/jpeg")})
        wrong_path = await client.post("/api/attendance/mark", files={"photo": ("a.jpg", b"synthetic", "image/jpeg")})
        results["sdk_contract"] = {"identify_photo_field_status": wrong_field.status_code,
                                   "mark_missing_session_path_status": wrong_path.status_code}

    # Real application registration and CORS handling, without running lifespan/DB.
    import main
    async with AsyncClient(transport=ASGITransport(app=main.app), base_url="http://audit.invalid") as client:
        cors = await client.options("/api/auth/me", headers={
            "Origin": "https://unrelated-audit-example.vercel.app",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "authorization"})
        health = await client.get("/health")
    results["cors_unrelated_vercel_origin"] = {
        "status": cors.status_code, "allow_origin": cors.headers.get("access-control-allow-origin"),
        "allow_credentials": cors.headers.get("access-control-allow-credentials")}
    results["health_without_lifespan"] = {"status": health.status_code, "body": health.json()}
    schema = main.app.openapi()
    routes = []
    for path, methods in schema["paths"].items():
        for method, spec in methods.items():
            if method.lower() in {"get", "post", "put", "patch", "delete", "options", "head"}:
                routes.append({"method": method.upper(), "path": path, "summary": spec.get("summary", "")})
    results["openapi"] = {"path_count": len(schema["paths"]), "operation_count": len(routes), "routes": routes}
    output = Path(__file__).with_name("verification.json")
    output.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in results.items() if k != "openapi"}, ensure_ascii=False, indent=2))
    print(f"OpenAPI: {len(schema['paths'])} paths, {len(routes)} operations; saved {output.name}")

if __name__ == "__main__":
    asyncio.run(run())
