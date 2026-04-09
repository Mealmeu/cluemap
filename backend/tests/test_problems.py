from __future__ import annotations

from tests.conftest import auth_headers


def test_problem_list_and_detail(client, student_auth, seeded_problem):
    access_token, _ = student_auth
    list_response = client.get("/api/problems", headers=auth_headers(access_token))
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    detail_response = client.get(
        f"/api/problems/{seeded_problem['id']}",
        headers=auth_headers(access_token),
    )
    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail["title"] == "테스트 문제"
    assert detail["test_cases"][1]["expected_output"] is None
