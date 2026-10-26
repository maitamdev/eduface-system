"""CORS must survive errors, without allowing unrelated origins or leaking details."""
import re
from contextlib import asynccontextmanager

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from pymongo.errors import DuplicateKeyError, OperationFailure

TRUSTED = "https://www.dhv-edu.tech"
APEX = "https://dhv-edu.tech"


@pytest.fixture
def cors_client(monkeypatch):
    from main import app
    monkeypatch.setattr(app, "cors_origins", [TRUSTED, APEX])
    monkeypatch.setattr(app, "middleware_stack", None)
    monkeypatch.setattr(app.router, "routes", list(app.router.routes))
    monkeypatch.setattr(app.state, "startup_attempted", False, raising=False)

    @app.get("/_cors-test/{kind}")
    async def response_probe(kind: str):
        if kind == "crash":
            raise RuntimeError("private-db-detail-never-return-this")
        if kind == "duplicate":
            raise DuplicateKeyError("private duplicate key")
        if kind == "database":
            raise OperationFailure("private database operation", code=123)
        if kind == "auth":
            raise HTTPException(401, "Sign in required")
        return {"ok": True}

    client = TestClient(app, raise_server_exceptions=False)
    yield client
    client.close()


def test_unhandled_error_keeps_cors_and_returns_safe_traceable_json(cors_client):
    response = cors_client.get("/_cors-test/crash", headers={"Origin": TRUSTED, "X-Request-ID": "enroll-debug-123"})
    assert response.status_code == 500
    assert response.headers.get("Access-Control-Allow-Origin") == TRUSTED
    assert response.headers["Access-Control-Allow-Credentials"] == "true"
    assert "X-Request-ID" in response.headers["Access-Control-Expose-Headers"]
    assert response.headers["X-Request-ID"] == "enroll-debug-123"
    assert response.json()["request_id"] == "enroll-debug-123"
    assert response.headers["Cache-Control"] == "no-store"
    assert "private-db-detail" not in response.text


@pytest.mark.parametrize("kind,status", [("ok",200),("auth",401),("duplicate",409),("database",503)])
def test_regular_and_handled_error_responses_keep_cors(cors_client, kind, status):
    response = cors_client.get(f"/_cors-test/{kind}", headers={"Origin": TRUSTED})
    assert response.status_code == status
    assert response.headers["Access-Control-Allow-Origin"] == TRUSTED
    assert response.headers["X-Request-ID"]
    assert "Origin" in response.headers["Vary"]


@pytest.mark.parametrize("origin", [TRUSTED, APEX])
def test_self_enroll_preflight_succeeds_even_while_database_is_starting(cors_client, monkeypatch, origin):
    from main import app
    monkeypatch.setattr(app.state, "startup_attempted", True)
    monkeypatch.setattr(app.state, "database_initialized", False, raising=False)
    preflight = cors_client.options("/api/persons/self-enroll", headers={"Origin": origin,
        "Access-Control-Request-Method":"POST", "Access-Control-Request-Headers":"authorization,content-type,x-request-id"})
    assert preflight.status_code == 200
    assert preflight.headers["Access-Control-Allow-Origin"] == origin
    blocked = cors_client.post("/api/persons/self-enroll", headers={"Origin": origin})
    assert blocked.status_code == 503
    assert blocked.headers["Access-Control-Allow-Origin"] == origin
    assert blocked.headers["X-Request-ID"]
    assert blocked.headers["Cache-Control"] == "no-store"


def test_untrusted_origin_is_not_granted_cors_even_on_500(cors_client):
    origin = "https://untrusted.example"
    response = cors_client.get("/_cors-test/crash", headers={"Origin": origin})
    assert response.status_code == 500
    assert "Access-Control-Allow-Origin" not in response.headers
    preflight = cors_client.options("/api/persons/self-enroll", headers={"Origin":origin,"Access-Control-Request-Method":"POST"})
    assert preflight.status_code == 400
    assert "Access-Control-Allow-Origin" not in preflight.headers


def test_invalid_incoming_request_id_is_replaced(cors_client):
    response = cors_client.get("/_cors-test/crash", headers={"Origin":TRUSTED, "X-Request-ID":"x"*1000})
    assert response.status_code == 500
    assert re.fullmatch(r"[a-f0-9]{12}", response.headers["X-Request-ID"])
    assert response.json()["request_id"] == response.headers["X-Request-ID"]


def test_same_origin_request_without_origin_header_remains_traceable(cors_client):
    response = cors_client.get("/_cors-test/crash")
    assert response.status_code == 500
    assert "Access-Control-Allow-Origin" not in response.headers
    assert response.json()["request_id"] == response.headers["X-Request-ID"]


def test_outer_middleware_preserves_lifespan_and_websockets():
    from core.http_app import CorsFastAPI
    from starlette.websockets import WebSocket
    events = []

    @asynccontextmanager
    async def lifecycle(app):
        events.append("startup")
        yield
        events.append("shutdown")

    test_app = CorsFastAPI(cors_origins=[TRUSTED], lifespan=lifecycle)

    @test_app.websocket("/echo")
    async def echo(socket: WebSocket):
        await socket.accept()
        await socket.send_text(await socket.receive_text())
        await socket.close()

    with TestClient(test_app) as client:
        assert events == ["startup"]
        with client.websocket_connect("/echo") as socket:
            socket.send_text("ping")
            assert socket.receive_text() == "ping"
    assert events == ["startup", "shutdown"]
