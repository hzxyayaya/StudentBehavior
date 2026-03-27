import importlib
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import student_behavior_demo_api.main as main_module
from student_behavior_demo_api.services import DemoApiStore


app = main_module.app


@pytest.fixture
def client(monkeypatch, tmp_path: Path) -> TestClient:
    artifact_root = (
        Path(__file__).resolve().parents[4]
        / "v1-model-stubs"
        / "artifacts"
        / "model_stubs"
    )
    warnings_path = tmp_path / "v1_student_results.csv"
    warnings_path.write_text(
        "\ufeffstudent_id,term_key,student_name,major_name,quadrant_label,risk_probability,risk_level,dimension_scores_json\n"
        '20230002,2023-1,Alice,软件工程,情绪驱动型,0.92,high,"[]"\n'
        '20230001,2023-1,Bob,软件工程,被动守纪型,0.81,medium,"[]"\n',
        encoding="utf-8",
    )
    reports_path = tmp_path / "artifacts" / "model_stubs" / "v1_student_reports.jsonl"
    reports_path.parent.mkdir(parents=True, exist_ok=True)
    reports_path.write_text(
        "\n".join(
            json.dumps(record, ensure_ascii=False)
            for record in [
                {
                    "student_id": "20230001",
                    "term_key": "2022-2",
                    "student_name": "Bob",
                    "major_name": "软件工程",
                    "dimension_scores_json": json.dumps(
                        [{"dimension": "学业基础表现", "score": 82}],
                        ensure_ascii=False,
                    ),
                    "intervention_advice": ["继续保持稳定节奏"],
                },
                {
                    "student_id": "20230001",
                    "term_key": "2023-1",
                    "student_name": "Bob",
                    "major_name": "软件工程",
                    "dimension_scores_json": json.dumps(
                        [{"dimension": "学业基础表现", "score": 88}],
                        ensure_ascii=False,
                    ),
                    "intervention_advice": ["优先关注课程作业完成质量"],
                },
            ]
        ),
        encoding="utf-8",
    )
    store = DemoApiStore(
        overview_path=artifact_root / "v1_overview_by_term.json",
        model_summary_path=artifact_root / "v1_model_summary.json",
        overview_term="2024-2",
        warnings_path=warnings_path,
        repo_root=tmp_path,
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


def test_get_warnings_rejects_invalid_page(client) -> None:
    response = client.get("/api/warnings", params={"term": "2023-1", "page": 0})
    assert response.status_code == 422


def test_get_warnings_rejects_invalid_page_size(client) -> None:
    response = client.get("/api/warnings", params={"term": "2023-1", "page_size": 0})
    assert response.status_code == 422


def test_get_warnings_rejects_invalid_risk_level(client) -> None:
    response = client.get("/api/warnings", params={"term": "2023-1", "risk_level": "urgent"})
    assert response.status_code == 422


def test_get_warnings_rejects_invalid_quadrant_label(client) -> None:
    response = client.get("/api/warnings", params={"term": "2023-1", "quadrant_label": "other"})
    assert response.status_code == 422


def test_get_warnings_returns_404_for_unknown_term(client) -> None:
    response = client.get("/api/warnings", params={"term": "2099-1"})
    assert response.status_code == 404
    payload = response.json()
    assert payload["code"] == 404
    assert payload["message"] == "term not found"


def test_get_student_profile_returns_404_for_unknown_student(client) -> None:
    response = client.get("/api/students/404/profile", params={"term": "2023-1"})
    assert response.status_code == 404


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
