import importlib
import json
from pathlib import Path

import pandas as pd
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
    warnings_path = tmp_path / "artifacts" / "model_stubs" / "v1_student_results.csv"
    warnings_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        [
            {
                "student_id": "20230002",
                "term_key": "2023-1",
                "student_name": "Alice",
                "major_name": "软件工程",
                "quadrant_label": "情绪驱动型",
                "risk_probability": 0.92,
                "risk_level": "high",
                "dimension_scores_json": json.dumps([], ensure_ascii=False),
            },
            {
                "student_id": "20230001",
                "term_key": "2023-1",
                "student_name": "Bob",
                "major_name": "软件工程",
                "quadrant_label": "被动守纪型",
                "risk_probability": 0.81,
                "risk_level": "medium",
                "dimension_scores_json": json.dumps(
                    [{"dimension": "学业基础表现", "score": 88}],
                    ensure_ascii=False,
                ),
            },
        ]
    ).to_csv(warnings_path, index=False, encoding="utf-8-sig")
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
                    "top_factors": ["作业完成度偏低"],
                    "intervention_advice": ["继续保持稳定节奏"],
                    "report_text": "2022-2 report",
                },
                {
                    "student_id": "20230001",
                    "term_key": "2023-1",
                    "student_name": "Bob",
                    "major_name": "软件工程",
                    "top_factors": ["课堂互动不足"],
                    "intervention_advice": ["优先关注课程作业完成质量"],
                    "report_text": "2023-1 report",
                },
                {
                    "student_id": "20230002",
                    "term_key": "2023-1",
                    "student_name": "Alice",
                    "major_name": "软件工程",
                    "top_factors": ["课堂参与活跃"],
                    "intervention_advice": ["优先补齐课堂互动"],
                    "report_text": "2023-1 report for Alice",
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


def test_get_quadrants_returns_404_for_unknown_term(client) -> None:
    response = client.get("/api/analytics/quadrants", params={"term": "2099-1"})
    assert response.status_code == 404


def test_get_quadrants_returns_500_for_bad_schema(monkeypatch) -> None:
    class BrokenQuadrantsStore:
        def get_quadrants(self, term: str) -> dict:
            raise KeyError("top_factors")

    monkeypatch.setattr(main_module, "get_store", lambda: BrokenQuadrantsStore())
    client = TestClient(app, raise_server_exceptions=False)

    response = client.get("/api/analytics/quadrants", params={"term": "2023-1"})
    assert response.status_code == 500
    payload = response.json()
    assert set(payload) == {"code", "message", "data", "meta"}
    assert payload["code"] == 500
    assert payload["message"] == "artifacts unavailable"
    assert payload["data"] == {}
    assert payload["meta"]["term"] == "2023-1"


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


def test_get_student_report_returns_404_for_unknown_student(client) -> None:
    response = client.get("/api/students/404/report", params={"term": "2023-1"})
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
