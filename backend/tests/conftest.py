from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import pytest
from fastapi.testclient import TestClient

TEST_DB_PATH = Path(__file__).resolve().parent / "test.db"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH.as_posix()}"
os.environ["SANDBOX_MODE"] = "local"
os.environ["ACCESS_TOKEN_SECRET"] = "test-access-secret-1234567890-test"
os.environ["REFRESH_TOKEN_SECRET"] = "test-refresh-secret-1234567890-test"
os.environ["COOKIE_SECURE"] = "false"
os.environ["TRUSTED_HOSTS_RAW"] = "testserver,localhost,127.0.0.1"
os.environ["CSRF_TRUSTED_ORIGINS_RAW"] = "http://testserver,http://localhost"
os.environ["ALLOW_REFRESH_TOKEN_IN_BODY"] = "false"
os.environ["RUN_SEED_ON_START"] = "false"

from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.main import app


@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    SessionLocal.remove() if hasattr(SessionLocal, "remove") else None


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def browser_headers(client: TestClient, access_token: Optional[str] = None, include_csrf: bool = True) -> dict[str, str]:
    headers = {"Origin": "http://testserver"}
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"
    if include_csrf:
        csrf_token = client.cookies.get("cluemap_csrf_token")
        if csrf_token:
            headers["X-CSRF-Token"] = csrf_token
    return headers


def register_user(client: TestClient, email: str, password: str, role: str) -> dict:
    response = client.post(
        "/api/auth/register",
        headers=browser_headers(client, include_csrf=False),
        json={"email": email, "password": password, "role": role},
    )
    assert response.status_code == 201
    return response.json()


def login_user(client: TestClient, email: str, password: str) -> dict:
    response = client.post(
        "/api/auth/login",
        headers=browser_headers(client, include_csrf=False),
        json={"email": email, "password": password},
    )
    assert response.status_code == 200
    return response.json()


def auth_headers(access_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def student_auth(client: TestClient):
    payload = register_user(client, "student@example.com", "password123", "student")
    return payload["access_token"], payload["user"]


@pytest.fixture
def teacher_auth(client: TestClient):
    payload = register_user(client, "teacher@example.com", "password123", "teacher")
    return payload["access_token"], payload["user"]


@pytest.fixture
def seeded_problem(client: TestClient, teacher_auth):
    access_token, _ = teacher_auth
    response = client.post(
        "/api/problems",
        headers={**browser_headers(client), **auth_headers(access_token)},
        json={
            "title": "테스트 문제",
            "description": "짝수의 합을 구하는 함수를 작성하세요.",
            "starter_code": "def sum_even_numbers(numbers):\n    total = 0\n    return total\n",
            "reference_solution_summary": "짝수만 골라 더합니다.",
            "concept_tags": ["loop", "condition", "accumulator"],
            "misconception_taxonomy": ["wrong_condition_logic", "accumulator_missing"],
            "test_cases": [
                {"input_data": {"args": [[1, 2, 3, 4]]}, "expected_output": 6, "is_hidden": False, "order_index": 0},
                {"input_data": {"args": [[2, 6, 8]]}, "expected_output": 16, "is_hidden": True, "order_index": 1},
            ],
        },
    )
    assert response.status_code == 201
    return response.json()
