"""Preserve the deployed site's Google login without enabling it on other forks."""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from core.google_identity import google_configuration, require_google_configuration
from routers.google_auth import router

DHV_CLIENT = "839148608863-iv1en34namc76757touqsf36u1950ou2.apps.googleusercontent.com"
CUSTOM_CLIENT = "123456789-customclient.apps.googleusercontent.com"


@pytest.fixture(autouse=True)
def isolated_environment(monkeypatch):
    monkeypatch.delenv("GOOGLE_CLIENT_ID", raising=False)
    monkeypatch.delenv("RENDER_EXTERNAL_HOSTNAME", raising=False)


def test_dhv_render_service_keeps_its_existing_google_client(monkeypatch):
    monkeypatch.setenv("RENDER_EXTERNAL_HOSTNAME", "eduface-system.onrender.com")
    assert google_configuration() == {"enabled": True, "client_id": DHV_CLIENT}
    assert require_google_configuration()["client_id"] == DHV_CLIENT


@pytest.mark.parametrize("hostname", ["", "another-service.onrender.com", "eduface-system.onrender.com.attacker.example"])
def test_unconfigured_installations_stay_disabled(monkeypatch, hostname):
    monkeypatch.setenv("RENDER_EXTERNAL_HOSTNAME", hostname)
    assert google_configuration() == {"enabled": False, "client_id": ""}


def test_operator_configuration_overrides_deployment_default(monkeypatch):
    monkeypatch.setenv("RENDER_EXTERNAL_HOSTNAME", "eduface-system.onrender.com")
    monkeypatch.setenv("GOOGLE_CLIENT_ID", CUSTOM_CLIENT)
    assert google_configuration()["client_id"] == CUSTOM_CLIENT


@pytest.mark.parametrize("value", ["", "short", "invalid client id"])
def test_explicit_disable_or_invalid_config_does_not_fall_back(monkeypatch, value):
    monkeypatch.setenv("RENDER_EXTERNAL_HOSTNAME", "eduface-system.onrender.com")
    monkeypatch.setenv("GOOGLE_CLIENT_ID", value)
    assert google_configuration() == {"enabled": False, "client_id": ""}


def test_http_headers_cannot_select_deployment_configuration():
    app = FastAPI()
    app.include_router(router, prefix="/api/auth")
    response = TestClient(app).get("/api/auth/google/config", headers={
        "Host": "eduface-system.onrender.com", "Origin": "https://www.dhv-edu.tech"})
    assert response.status_code == 200
    assert response.json() == {"enabled": False, "client_id": ""}


def test_public_endpoint_returns_the_same_client_used_for_token_validation(monkeypatch):
    monkeypatch.setenv("RENDER_EXTERNAL_HOSTNAME", "eduface-system.onrender.com")
    app = FastAPI()
    app.include_router(router, prefix="/api/auth")
    response = TestClient(app).get("/api/auth/google/config")
    assert response.status_code == 200
    assert response.json() == require_google_configuration()
