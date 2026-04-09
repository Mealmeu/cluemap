from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.core.config import Settings
from tests.conftest import auth_headers, browser_headers, register_user


def test_register_success_and_duplicate_fail(client):
    first = client.post(
        "/api/auth/register",
        headers=browser_headers(client, include_csrf=False),
        json={"email": "dup@example.com", "password": "password123", "role": "student"},
    )
    assert first.status_code == 201

    duplicate = client.post(
        "/api/auth/register",
        headers=browser_headers(client, include_csrf=False),
        json={"email": "dup@example.com", "password": "password123", "role": "student"},
    )
    assert duplicate.status_code == 409


def test_login_success_and_fail_and_cookie_flags(client):
    register_user(client, "login@example.com", "password123", "student")

    success = client.post(
        "/api/auth/login",
        headers=browser_headers(client, include_csrf=False),
        json={"email": "login@example.com", "password": "password123"},
    )
    assert success.status_code == 200
    assert success.json()["access_token"]
    set_cookie = success.headers.get("set-cookie", "")
    assert "HttpOnly" in set_cookie
    assert "SameSite=lax" in set_cookie or "SameSite=Lax" in set_cookie

    failure = client.post(
        "/api/auth/login",
        headers=browser_headers(client, include_csrf=False),
        json={"email": "login@example.com", "password": "wrongpass99"},
    )
    assert failure.status_code == 401


def test_refresh_success_revoked_reuse_and_fail_after_logout(client):
    payload = register_user(client, "refresh@example.com", "password123", "student")
    me = client.get("/api/auth/me", headers=auth_headers(payload["access_token"]))
    assert me.status_code == 200

    original_refresh = client.cookies.get("cluemap_refresh_token")
    refreshed = client.post("/api/auth/refresh", headers=browser_headers(client))
    assert refreshed.status_code == 200
    assert refreshed.json()["access_token"]

    replay = client.post(
        "/api/auth/refresh",
        headers=browser_headers(client),
        cookies={
            "cluemap_refresh_token": original_refresh,
            "cluemap_csrf_token": client.cookies.get("cluemap_csrf_token"),
        },
    )
    assert replay.status_code == 401

    logout = client.post("/api/auth/logout", headers=browser_headers(client))
    assert logout.status_code == 200

    failed_refresh = client.post("/api/auth/refresh", headers=browser_headers(client))
    assert failed_refresh.status_code == 403


def test_refresh_requires_csrf_and_origin(client):
    register_user(client, "csrf@example.com", "password123", "student")

    missing_csrf = client.post(
        "/api/auth/refresh",
        headers=browser_headers(client, include_csrf=False),
    )
    assert missing_csrf.status_code == 403

    wrong_origin = client.post(
        "/api/auth/refresh",
        headers={"Origin": "http://evil.example", "X-CSRF-Token": client.cookies.get("cluemap_csrf_token")},
    )
    assert wrong_origin.status_code == 403


def test_refresh_rejects_user_agent_mismatch(client):
    register_user(client, "ua@example.com", "password123", "student")

    mismatched = client.post(
        "/api/auth/refresh",
        headers={
            "Origin": "http://testserver",
            "X-CSRF-Token": client.cookies.get("cluemap_csrf_token"),
            "User-Agent": "suspicious-bot/1.0",
        },
    )
    assert mismatched.status_code == 401

    failed_again = client.post("/api/auth/refresh", headers=browser_headers(client))
    assert failed_again.status_code == 401


def test_production_unsafe_settings_fail():
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            environment="production",
            frontend_origin="http://localhost",
            cors_origins_raw="http://localhost",
            trusted_hosts_raw="localhost",
            csrf_trusted_origins_raw="http://localhost",
            access_token_secret="change-me-access-secret",
            refresh_token_secret="change-me-refresh-secret",
            sandbox_runner_shared_secret="change-me-runner-secret",
            cookie_secure=False,
            allow_refresh_token_in_body=False,
        )
