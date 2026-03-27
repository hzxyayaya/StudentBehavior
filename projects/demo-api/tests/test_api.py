import importlib
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import student_behavior_demo_api.main as main_module
from student_behavior_demo_api.services import DemoApiStore


app = main_module.app


@pytest.fixture
def client(monkeypatch) -> TestClient:
    artifact_root = (
        Path(__file__).resolve().parents[4]
        / "v1-model-stubs"
        / "artifacts"
        / "model_stubs"
    )
    store = DemoApiStore(
        overview_path=artifact_root / "v1_overview_by_term.json",
        model_summary_path=artifact_root / "v1_model_summary.json",
        overview_term="2024-2",
    )
    monkeypatch.setattr(main_module, "get_store", lambda: store)
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
    payload = response.json()
    assert payload["code"] == 404
    assert payload["message"] == "term not found"
    assert payload["data"] == {}
    assert payload["meta"]["term"] == "2099-1"


def test_get_models_summary_returns_envelope_payload(client) -> None:
    response = client.get("/api/models/summary", params={"term": "2024-2"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["code"] == 200
    assert payload["data"]["cluster_method"] == "stub-quadrant-rules"
    assert payload["data"]["risk_model"] == "stub-risk-rules"
    assert payload["meta"]["term"] == "2024-2"


def test_missing_artifacts_app_starts_and_fails_on_request(monkeypatch) -> None:
    class MissingArtifactStore:
        def get_overview(self, term: str) -> dict:
            raise FileNotFoundError("v1_overview_by_term.json")

        def get_model_summary(self, term: str | None = None) -> dict:
            raise FileNotFoundError("v1_model_summary.json")

    reloaded_main = importlib.reload(main_module)
    monkeypatch.setattr(reloaded_main, "get_store", lambda: MissingArtifactStore())

    client = TestClient(reloaded_main.app)
    response = client.get("/api/analytics/overview", params={"term": "2024-2"})

    assert response.status_code == 500
    payload = response.json()
    assert payload["code"] == 500
    assert payload["message"] == "artifacts unavailable"
    assert payload["data"] == {}
