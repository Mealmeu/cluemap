from __future__ import annotations

from tests.conftest import auth_headers, browser_headers, register_user


def test_student_teacher_end_to_end_flow(client):
    student_payload = register_user(client, "flow-student@example.com", "password123", "student")
    student_access_token = student_payload["access_token"]
    student_id = student_payload["user"]["id"]

    student_me = client.get("/api/auth/me", headers=auth_headers(student_access_token))
    assert student_me.status_code == 200
    assert student_me.json()["role"] == "student"

    student_refresh = client.post("/api/auth/refresh", headers=browser_headers(client))
    assert student_refresh.status_code == 200
    student_access_token = student_refresh.json()["access_token"]

    student_logout = client.post("/api/auth/logout", headers=browser_headers(client))
    assert student_logout.status_code == 200

    student_refresh_after_logout = client.post("/api/auth/refresh", headers=browser_headers(client))
    assert student_refresh_after_logout.status_code == 403

    student_login = client.post(
        "/api/auth/login",
        headers=browser_headers(client, include_csrf=False),
        json={"email": "flow-student@example.com", "password": "password123"},
    )
    assert student_login.status_code == 200
    student_access_token = student_login.json()["access_token"]

    teacher_payload = register_user(client, "flow-teacher@example.com", "password123", "teacher")
    teacher_access_token = teacher_payload["access_token"]

    teacher_logout = client.post("/api/auth/logout", headers=browser_headers(client))
    assert teacher_logout.status_code == 200

    teacher_login = client.post(
        "/api/auth/login",
        headers=browser_headers(client, include_csrf=False),
        json={"email": "flow-teacher@example.com", "password": "password123"},
    )
    assert teacher_login.status_code == 200
    teacher_access_token = teacher_login.json()["access_token"]

    teacher_me = client.get("/api/auth/me", headers=auth_headers(teacher_access_token))
    assert teacher_me.status_code == 200
    assert teacher_me.json()["role"] == "teacher"

    problem_create = client.post(
        "/api/problems",
        headers={**browser_headers(client), **auth_headers(teacher_access_token)},
        json={
            "title": "흐름 검증 문제",
            "description": "리스트에서 짝수의 합을 구하는 함수를 작성하세요.",
            "starter_code": "def sum_even_numbers(numbers):\n    total = 0\n    return total\n",
            "reference_solution_summary": "짝수만 골라 누적 합을 구합니다.",
            "concept_tags": ["loop", "condition", "accumulator"],
            "misconception_taxonomy": ["wrong_condition_logic", "accumulator_missing"],
            "test_cases": [
                {"input_data": {"args": [[1, 2, 3, 4]]}, "expected_output": 6, "is_hidden": False, "order_index": 0},
                {"input_data": {"args": [[2, 6, 8]]}, "expected_output": 16, "is_hidden": True, "order_index": 1},
            ],
        },
    )
    assert problem_create.status_code == 201
    problem_id = problem_create.json()["id"]

    student_list = client.get("/api/problems", headers=auth_headers(student_access_token))
    assert student_list.status_code == 200
    assert any(item["id"] == problem_id for item in student_list.json())

    student_detail = client.get(f"/api/problems/{problem_id}", headers=auth_headers(student_access_token))
    assert student_detail.status_code == 200
    assert student_detail.json()["test_cases"][1]["expected_output"] is None

    submission_create = client.post(
        "/api/submissions",
        headers=auth_headers(student_access_token),
        json={
            "problem_id": problem_id,
            "code": "def sum_even_numbers(numbers):\n    total = 0\n    for number in numbers:\n        if number % 2 == 0:\n            total += number\n    return total\n",
        },
    )
    assert submission_create.status_code == 201
    submission_payload = submission_create.json()
    submission_id = submission_payload["id"]
    assert submission_payload["run_status"] == "passed"
    assert submission_payload["analysis_result"]["teacher_summary"] == ""
    assert any("\uac00" <= ch <= "\ud7a3" for ch in submission_payload["analysis_result"]["hint_level_1"])

    submission_detail = client.get(
        f"/api/submissions/{submission_id}",
        headers=auth_headers(student_access_token),
    )
    assert submission_detail.status_code == 200
    assert submission_detail.json()["id"] == submission_id

    analysis_detail = client.get(
        f"/api/submissions/{submission_id}/analysis",
        headers=auth_headers(student_access_token),
    )
    assert analysis_detail.status_code == 200
    assert analysis_detail.json()["teacher_summary"] == ""

    history = client.get(
        f"/api/problems/{problem_id}/submissions/me",
        headers=auth_headers(student_access_token),
    )
    assert history.status_code == 200
    assert len(history.json()["items"]) == 1

    failed_submission = client.post(
        "/api/submissions",
        headers=auth_headers(student_access_token),
        json={
            "problem_id": problem_id,
            "code": "def sum_even_numbers(numbers):\n    return 999\n",
        },
    )
    assert failed_submission.status_code == 201
    hidden_failures = [item for item in failed_submission.json()["failure_summary"] if item.get("is_hidden")]
    assert hidden_failures
    assert all("expected_output" not in item for item in hidden_failures)
    assert all("actual_output" not in item for item in hidden_failures)

    teacher_stats = client.get(
        f"/api/teacher/problems/{problem_id}/stats",
        headers=auth_headers(teacher_access_token),
    )
    assert teacher_stats.status_code == 200
    assert teacher_stats.json()["total_submissions"] >= 2

    teacher_insights = client.get(
        f"/api/teacher/problems/{problem_id}/insights",
        headers=auth_headers(teacher_access_token),
    )
    assert teacher_insights.status_code == 200
    assert any("\uac00" <= ch <= "\ud7a3" for ch in teacher_insights.json()["summary"])

    teacher_history = client.get(
        f"/api/teacher/students/{student_id}/history",
        headers=auth_headers(teacher_access_token),
    )
    assert teacher_history.status_code == 200
    assert len(teacher_history.json()["items"]) >= 2

    student_block = client.get(
        f"/api/teacher/problems/{problem_id}/stats",
        headers=auth_headers(student_access_token),
    )
    assert student_block.status_code == 403
