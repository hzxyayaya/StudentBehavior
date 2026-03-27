import pytest
from fastapi.testclient import TestClient

from student_behavior_demo_api.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_health_style_response_uses_envelope_shape() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/auth/demo-login",
        json={"username": "demo_admin", "password": "demo_only", "role": "manager"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert set(payload) == {"code", "message", "data", "meta"}


def test_demo_login_returns_fixed_demo_session() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/auth/demo-login",
        json={"username": "demo_admin", "password": "demo_only", "role": "manager"},
    )
    assert response.json()["data"]["session_token"] == "demo-token"


def test_get_overview_returns_404_for_unknown_term(client) -> None:
    response = client.get("/api/analytics/overview", params={"term": "2099-1"})
    assert response.status_code == 404
