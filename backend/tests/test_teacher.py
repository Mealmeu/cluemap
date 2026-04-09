from __future__ import annotations

from tests.conftest import auth_headers


def test_teacher_access_allowed_and_student_blocked(client, teacher_auth, student_auth, seeded_problem):
    teacher_token, teacher_user = teacher_auth
    student_token, student_user = student_auth

    for _ in range(2):
        client.post(
            "/api/submissions",
            headers=auth_headers(student_token),
            json={
                "problem_id": seeded_problem["id"],
                "code": "def sum_even_numbers(numbers):\n    return 0\n",
            },
        )

    teacher_stats = client.get(
        f"/api/teacher/problems/{seeded_problem['id']}/stats",
        headers=auth_headers(teacher_token),
    )
    assert teacher_stats.status_code == 200
    assert teacher_stats.json()["total_submissions"] == 2

    student_stats = client.get(
        f"/api/teacher/problems/{seeded_problem['id']}/stats",
        headers=auth_headers(student_token),
    )
    assert student_stats.status_code == 403

    history = client.get(
        f"/api/teacher/students/{student_user['id']}/history",
        headers=auth_headers(teacher_token),
    )
    assert history.status_code == 200
    assert len(history.json()["items"]) == 2
