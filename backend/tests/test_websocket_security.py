import io
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from bson import ObjectId
from fastapi import FastAPI
from fastapi.testclient import TestClient
from PIL import Image
from starlette.websockets import WebSocketDisconnect

from core.auth import create_access_token
from routers import attendance


@pytest.fixture
def socket_client(monkeypatch):
    session_id = str(ObjectId())
    find = AsyncMock(return_value={"_id": ObjectId(session_id), "is_active": True})
    db = SimpleNamespace(sessions=SimpleNamespace(find_one=find))
    monkeypatch.setattr(attendance, "get_database", lambda: db)
    monkeypatch.setattr(attendance, "_ws_limiter", SimpleNamespace(hit=lambda *args: True))
    identify = AsyncMock(return_value=[])
    monkeypatch.setattr(attendance.azure_face, "identify_faces", identify)
    app = FastAPI()
    app.include_router(attendance.router, prefix="/api/attendance")
    return TestClient(app), session_id, find, identify


def _authenticate(socket):
    token, _ = create_access_token("preview-user", "operator", "operator")
    socket.send_json({"type": "auth", "authorization": f"Bearer {token}", "confidence": 0.6})
    assert socket.receive_json()["status"] == 200


def test_unauthenticated_socket_never_touches_database(socket_client):
    client, session_id, find, identify = socket_client
    with client.websocket_connect(f"/api/attendance/ws/{session_id}") as socket:
        socket.send_json({"type": "auth", "authorization": "Bearer invalid"})
        with pytest.raises(WebSocketDisconnect) as error:
            socket.receive_json()
        assert error.value.code == 1008
    find.assert_not_awaited()
    identify.assert_not_awaited()


def test_foreign_origin_is_rejected(socket_client):
    client, session_id, find, _ = socket_client
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect(f"/api/attendance/ws/{session_id}", headers={"origin": "https://untrusted.example"}):
            pass
    find.assert_not_awaited()


def test_authenticated_frame_is_validated_and_uses_threshold(socket_client):
    client, session_id, _, identify = socket_client
    image = io.BytesIO()
    Image.new("RGB", (100, 100)).save(image, format="JPEG")
    with client.websocket_connect(f"/api/attendance/ws/{session_id}") as socket:
        _authenticate(socket)
        socket.send_bytes(image.getvalue())
        assert socket.receive_json()["matches"] == []
    identify.assert_awaited_once_with(image.getvalue(), 0.6)


def test_invalid_frame_does_not_reach_recognition(socket_client):
    client, session_id, _, identify = socket_client
    with client.websocket_connect(f"/api/attendance/ws/{session_id}") as socket:
        _authenticate(socket)
        socket.send_bytes(b"not an image")
        assert socket.receive_json()["status"] == 400
    identify.assert_not_awaited()


def test_rate_limit_blocks_recognition(socket_client, monkeypatch):
    client, session_id, _, identify = socket_client
    monkeypatch.setattr(attendance, "_ws_limiter", SimpleNamespace(hit=lambda *args: False))
    with client.websocket_connect(f"/api/attendance/ws/{session_id}") as socket:
        _authenticate(socket)
        socket.send_bytes(b"frame")
        assert socket.receive_json()["status"] == 429
    identify.assert_not_awaited()


@pytest.mark.parametrize("value", ["=1+1", "+SUM(A1)", "-SUM(A1)", "@SUM(A1)", "  =1+1"])
def test_csv_cells_cannot_be_formulas(value):
    assert attendance._safe_csv_cell(value).startswith("'")


def test_csv_preserves_legitimate_values():
    assert attendance._safe_csv_cell("Nguyễn Minh Anh") == "Nguyễn Minh Anh"
    assert attendance._safe_csv_cell(0) == 0
