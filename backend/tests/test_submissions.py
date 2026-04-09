from __future__ import annotations

from tests.conftest import auth_headers


def test_submission_success_and_analysis_schema(client, student_auth, seeded_problem):
    access_token, _ = student_auth
    response = client.post(
        "/api/submissions",
        headers=auth_headers(access_token),
        json={
            "problem_id": seeded_problem["id"],
            "code": "def sum_even_numbers(numbers):\n    total = 0\n    for number in numbers:\n        if number % 2 == 0:\n            total += number\n    return total\n",
        },
    )
    assert response.status_code == 201
    payload = response.json()
    assert payload["run_status"] == "passed"
    assert payload["analysis_result"]["category"]
    assert payload["analysis_result"]["hint_level_1"]
    assert any("가" <= ch <= "힣" for ch in payload["analysis_result"]["hint_level_1"])
    assert "teacher_summary" not in payload["analysis_result"] or payload["analysis_result"]["teacher_summary"] == ""


def test_submission_timeout_and_runtime_error(client, student_auth, seeded_problem):
    access_token, _ = student_auth

    timeout_response = client.post(
        "/api/submissions",
        headers=auth_headers(access_token),
        json={
            "problem_id": seeded_problem["id"],
            "code": "def sum_even_numbers(numbers):\n    while True:\n        pass\n",
        },
    )
    assert timeout_response.status_code == 201
    assert timeout_response.json()["run_status"] == "timeout"

    runtime_response = client.post(
        "/api/submissions",
        headers=auth_headers(access_token),
        json={
            "problem_id": seeded_problem["id"],
            "code": "def sum_even_numbers(numbers):\n    return numbers[100]\n",
        },
    )
    assert runtime_response.status_code == 201
    assert runtime_response.json()["run_status"] == "runtime_error"


def test_submission_blocks_dangerous_import_and_builtin(client, student_auth, seeded_problem):
    access_token, _ = student_auth

    blocked_import = client.post(
        "/api/submissions",
        headers=auth_headers(access_token),
        json={
            "problem_id": seeded_problem["id"],
            "code": "import os\ndef sum_even_numbers(numbers):\n    return 0\n",
        },
    )
    assert blocked_import.status_code == 201
    assert blocked_import.json()["run_status"] == "blocked"

    blocked_builtin = client.post(
        "/api/submissions",
        headers=auth_headers(access_token),
        json={
            "problem_id": seeded_problem["id"],
            "code": "def sum_even_numbers(numbers):\n    open('/etc/passwd')\n    return 0\n",
        },
    )
    assert blocked_builtin.status_code == 201
    assert blocked_builtin.json()["run_status"] == "blocked"


def test_hidden_test_is_not_overexposed(client, student_auth, seeded_problem):
    access_token, _ = student_auth
    response = client.post(
        "/api/submissions",
        headers=auth_headers(access_token),
        json={
            "problem_id": seeded_problem["id"],
            "code": "def sum_even_numbers(numbers):\n    return 999\n",
        },
    )
    assert response.status_code == 201
    payload = response.json()
    hidden_failures = [item for item in payload["failure_summary"] if item.get("is_hidden")]
    assert hidden_failures
    assert all("expected_output" not in item for item in hidden_failures)
    assert all("actual_output" not in item for item in hidden_failures)


def test_submission_history_endpoint(client, student_auth, seeded_problem):
    access_token, _ = student_auth
    client.post(
        "/api/submissions",
        headers=auth_headers(access_token),
        json={
            "problem_id": seeded_problem["id"],
            "code": "def sum_even_numbers(numbers):\n    return 0\n",
        },
    )

    history = client.get(
        f"/api/problems/{seeded_problem['id']}/submissions/me",
        headers=auth_headers(access_token),
    )
    assert history.status_code == 200
    assert len(history.json()["items"]) == 1
