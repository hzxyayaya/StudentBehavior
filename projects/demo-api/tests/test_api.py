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
def client(monkeypatch, sample_artifacts_dir: Path) -> TestClient:
    store = DemoApiStore(
        overview_path=sample_artifacts_dir / "v1_overview_by_term.json",
        model_summary_path=sample_artifacts_dir / "v1_model_summary.json",
        overview_term="2024-2",
        warnings_path=sample_artifacts_dir / "v1_student_results.csv",
        repo_root=sample_artifacts_dir.parent.parent,
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


@pytest.mark.parametrize("term", ["2023-2", "2024-1", "2024-2"])
def test_get_overview_accepts_all_real_terms(client, term: str) -> None:
    response = client.get("/api/analytics/overview", params={"term": term})
    assert response.status_code == 200
    payload = response.json()
    assert payload["code"] == 200
    assert payload["meta"]["term"] == term
    assert payload["data"]["student_count"] == 179


def test_api_returns_500_when_artifacts_missing(app_without_artifacts) -> None:
    client = TestClient(app_without_artifacts)
    response = client.get("/api/analytics/overview", params={"term": "2023-1"})
    assert response.status_code == 500
    assert response.json()["message"] == "overview artifact unavailable"


def test_error_responses_keep_envelope_shape(client) -> None:
    response = client.get("/api/analytics/overview", params={"term": "2099-1"})
    payload = response.json()
    assert set(payload) == {"code", "message", "data", "meta"}


def test_get_groups_returns_404_for_unknown_term(client) -> None:
    response = client.get("/api/analytics/groups", params={"term": "2099-1"})
    assert response.status_code == 404


def test_get_groups_returns_500_for_bad_schema(monkeypatch) -> None:
    class BrokenGroupsStore:
        def get_groups(self, term: str) -> dict:
            raise KeyError("top_factors")

    monkeypatch.setattr(main_module, "get_store", lambda: BrokenGroupsStore())
    client = TestClient(app, raise_server_exceptions=False)

    response = client.get("/api/analytics/groups", params={"term": "2023-1"})
    assert response.status_code == 500
    payload = response.json()
    assert set(payload) == {"code", "message", "data", "meta"}
    assert payload["code"] == 500
    assert payload["message"] == "artifacts unavailable"
    assert payload["data"] == {}
    assert payload["meta"]["term"] == "2023-1"


def test_get_groups_returns_500_envelope_for_invalid_report_top_factors_schema(
    monkeypatch, tmp_path: Path, sample_artifacts_dir: Path
) -> None:
    artifact_root = sample_artifacts_dir
    warnings_path = tmp_path / "artifacts" / "model_stubs" / "v1_student_results.csv"
    warnings_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        [
            {
                "student_id": "20230001",
                "term_key": "2023-1",
                "student_name": "Bob",
                "major_name": "软件工程",
                "group_segment": "综合发展优势组",
                "risk_probability": 0.81,
                "risk_level": "medium",
                "dimension_scores_json": json.dumps([], ensure_ascii=False),
            },
        ]
    ).to_csv(warnings_path, index=False, encoding="utf-8-sig")
    reports_path = tmp_path / "artifacts" / "model_stubs" / "v1_student_reports.jsonl"
    reports_path.write_text(
        json.dumps(
            {
                "student_id": "20230001",
                "term_key": "2023-1",
                "student_name": "Bob",
                "major_name": "软件工程",
                "top_factors": {"dimension": "课堂学习投入"},
                "intervention_advice": ["优先关注课程作业完成质量"],
                "report_text": "2023-1 report",
            },
            ensure_ascii=False,
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
    client = TestClient(app)

    response = client.get("/api/analytics/groups", params={"term": "2023-1"})
    assert response.status_code == 500
    payload = response.json()
    assert set(payload) == {"code", "message", "data", "meta"}
    assert payload["code"] == 500
    assert payload["message"] == "artifacts unavailable"
    assert payload["data"] == {}
    assert payload["meta"]["term"] == "2023-1"


def test_get_groups_returns_500_envelope_for_invalid_report_top_factors_item_schema(
    monkeypatch, tmp_path: Path, sample_artifacts_dir: Path
) -> None:
    artifact_root = sample_artifacts_dir
    warnings_path = tmp_path / "artifacts" / "model_stubs" / "v1_student_results.csv"
    warnings_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        [
            {
                "student_id": "20230001",
                "term_key": "2023-1",
                "student_name": "Bob",
                "major_name": "软件工程",
                "group_segment": "综合发展优势组",
                "risk_probability": 0.81,
                "risk_level": "medium",
                "dimension_scores_json": json.dumps([], ensure_ascii=False),
            },
        ]
    ).to_csv(warnings_path, index=False, encoding="utf-8-sig")
    reports_path = tmp_path / "artifacts" / "model_stubs" / "v1_student_reports.jsonl"
    reports_path.write_text(
        json.dumps(
            {
                "student_id": "20230001",
                "term_key": "2023-1",
                "student_name": "Bob",
                "major_name": "软件工程",
                "top_factors": [123],
                "intervention_advice": ["优先关注课程作业完成质量"],
                "report_text": "2023-1 report",
            },
            ensure_ascii=False,
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
    client = TestClient(app)

    response = client.get("/api/analytics/groups", params={"term": "2023-1"})
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
    assert payload["data"]["cluster_method"] == "stub-group-rules"
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


def test_get_warnings_rejects_invalid_group_segment(client) -> None:
    response = client.get("/api/warnings", params={"term": "2023-1", "group_segment": ""})
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
    assert payload["message"] == "overview artifact unavailable"
    assert payload["data"] == {}
