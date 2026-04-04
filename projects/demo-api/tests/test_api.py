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


def test_scalar_docs_page_is_available(client) -> None:
    response = client.get("/scalar")

    assert response.status_code == 200
    assert "Scalar" in response.text
    assert "/openapi.json" in response.text


def test_openapi_exposes_route_and_schema_descriptions(client) -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    payload = response.json()
    trajectory_operation = payload["paths"]["/api/analytics/trajectory"]["get"]
    assert trajectory_operation["summary"] == "获取学业轨迹演化与关键行为分析"
    assert "学期风险轨迹" in trajectory_operation["description"]

    login_schema = payload["components"]["schemas"]["DemoLoginRequest"]
    assert login_schema["properties"]["username"]["description"] == "演示登录用户名"
    assert login_schema["properties"]["role"]["description"] == "演示账号角色"


def test_openapi_exposes_tags_and_examples(client) -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    payload = response.json()
    tag_names = {tag["name"] for tag in payload["tags"]}
    assert {"认证", "总览分析", "画像分层", "轨迹分析", "发展分析", "模型说明", "学生画像", "学生报告", "风险预警"} <= tag_names

    warnings_operation = payload["paths"]["/api/warnings"]["get"]
    assert warnings_operation["tags"] == ["风险预警"]
    term_parameter = next(parameter for parameter in warnings_operation["parameters"] if parameter["name"] == "term")
    assert term_parameter["schema"]["examples"] == ["2024-2"]

    login_schema = payload["components"]["schemas"]["DemoLoginRequest"]
    assert login_schema["example"] == {
        "username": "demo_admin",
        "password": "demo_only",
        "role": "manager",
    }


def test_openapi_exposes_response_examples(client) -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    payload = response.json()

    login_examples = payload["paths"]["/api/auth/demo-login"]["post"]["responses"]["200"]["content"]["application/json"][
        "example"
    ]
    assert login_examples["data"]["session_token"] == "demo-token"

    trajectory_examples = payload["paths"]["/api/analytics/trajectory"]["get"]["responses"]["200"]["content"][
        "application/json"
    ]["example"]
    assert trajectory_examples["data"]["term"] == "2024-2"
    assert trajectory_examples["data"]["risk_trend_summary"][0]["term"] == "2024-1"

    warning_not_found = payload["paths"]["/api/warnings"]["get"]["responses"]["404"]["content"]["application/json"][
        "example"
    ]
    assert warning_not_found["message"] == "term not found"


def test_get_overview_returns_404_for_unknown_term(client) -> None:
    response = client.get("/api/analytics/overview", params={"term": "2099-1"})
    assert response.status_code == 404
    payload = response.json()
    assert payload["code"] == 404
    assert payload["message"] == "term not found"
    assert payload["data"] == {}
    assert payload["meta"]["term"] == "2099-1"


def test_get_trajectory_analysis_returns_envelope(client) -> None:
    response = client.get("/api/analytics/trajectory", params={"term": "2023-1"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["code"] == 200
    assert payload["meta"]["term"] == "2023-1"
    assert payload["data"]["term"] == "2023-1"
    assert "student_samples" in payload["data"]


def test_get_development_analysis_returns_envelope(client) -> None:
    response = client.get("/api/analytics/development", params={"term": "2023-1"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["code"] == 200
    assert payload["meta"]["term"] == "2023-1"
    assert payload["data"]["term"] == "2023-1"
    assert payload["data"]["disclaimer"] == "去向真值暂未接入"


@pytest.mark.parametrize(
    ("term", "student_count", "risk_distribution", "group_distribution", "major_risk_summary"),
    [
        ("2023-2", 0, {"high": 0, "medium": 0, "low": 0}, {}, []),
        (
            "2024-1",
            0,
            {"high": 0, "medium": 0, "low": 0},
            {},
            [],
        ),
        ("2024-2", 179, {"high": 12, "medium": 64, "low": 103}, None, None),
    ],
)
def test_get_overview_accepts_all_real_terms(
    client,
    term: str,
    student_count: int,
    risk_distribution: dict[str, int],
    group_distribution: dict[str, int] | None,
    major_risk_summary: list[dict[str, object]] | None,
) -> None:
    response = client.get("/api/analytics/overview", params={"term": term})
    assert response.status_code == 200
    payload = response.json()
    assert payload["code"] == 200
    assert payload["meta"]["term"] == term
    assert payload["data"]["student_count"] == student_count
    assert payload["data"]["risk_distribution"] == risk_distribution
    if group_distribution is not None:
        assert payload["data"]["group_distribution"] == group_distribution
        assert payload["data"]["major_risk_summary"] == major_risk_summary
        assert payload["data"]["summary_term"] == term
        assert payload["data"]["summary_source"] == "term_fallback"
        assert payload["data"]["summary_unavailable_fields"] == ["trend_summary"]
        assert payload["data"]["trend_summary"] is None
    else:
        assert "summary_source" not in payload["data"]


def test_get_overview_returns_term_specific_fallback_payload(
    monkeypatch, tmp_path: Path, sample_artifacts_dir: Path
) -> None:
    overview_path = tmp_path / "artifacts" / "model_stubs" / "v1_overview_by_term.json"
    overview_path.parent.mkdir(parents=True, exist_ok=True)
    overview_path.write_text(
        json.dumps(
            {
                "student_count": 12,
                "risk_distribution": {"high": 1, "medium": 4, "low": 7},
                "group_distribution": {
                    "学习投入稳定组": 12,
                },
                "dimension_summary": [
                    {
                        "feature": "attendance",
                        "feature_cn": "课堂学习投入",
                        "dimension": "课堂学习投入",
                        "average_score": 0.91,
                    }
                ],
                "major_risk_summary": [
                    {
                        "major_name": "电子信息工程",
                        "student_count": 12,
                        "high_risk_count": 1,
                        "average_risk_probability": 0.67,
                    }
                ],
                "trend_summary": {
                    "terms": [
                        {
                            "term_key": "2024-1",
                            "student_count": 24,
                            "risk_distribution": {"high": 2, "medium": 6, "low": 16},
                        },
                        {
                            "term_key": "2024-2",
                            "student_count": 12,
                            "risk_distribution": {"high": 1, "medium": 4, "low": 7},
                        },
                    ]
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    warnings_path = tmp_path / "artifacts" / "model_stubs" / "v1_student_results.csv"
    pd.DataFrame(
        [
            {
                "student_id": "20230001",
                "term_key": "2024-1",
                "student_name": "Bob",
                "major_name": "软件工程",
                "group_segment": "综合发展优势组",
                "risk_probability": 0.41,
                "risk_level": "low",
                "dimension_scores_json": json.dumps(
                    [
                        {
                            "feature": "attendance",
                            "feature_cn": "课堂学习投入",
                            "dimension": "课堂参与表现",
                            "score": 0.41,
                        }
                    ],
                    ensure_ascii=False,
                ),
            },
            {
                "student_id": "20230002",
                "term_key": "2024-1",
                "student_name": "Alice",
                "major_name": "软件工程",
                "group_segment": "课堂参与薄弱组",
                "risk_probability": 0.44,
                "risk_level": "low",
                "dimension_scores_json": json.dumps(
                    [
                        {
                            "feature": "attendance",
                            "feature_cn": "课堂学习投入",
                            "dimension": "课堂学习投入",
                            "score": 0.44,
                        }
                    ],
                    ensure_ascii=False,
                ),
            },
            {
                "student_id": "20230004",
                "term_key": "2024-1",
                "student_name": "Dave",
                "major_name": "电子信息工程",
                "group_segment": "课堂参与薄弱组",
                "risk_probability": 0.91,
                "risk_level": "high",
                "dimension_scores_json": json.dumps(
                    [
                        {
                            "feature": "attendance",
                            "feature_cn": "课堂学习投入",
                            "dimension": "课堂学习投入",
                            "score": 0.46,
                        }
                    ],
                    ensure_ascii=False,
                ),
            },
        ]
    ).to_csv(warnings_path, index=False, encoding="utf-8-sig")
    reports_path = tmp_path / "artifacts" / "model_stubs" / "v1_student_reports.jsonl"
    reports_path.write_text("", encoding="utf-8")
    store = DemoApiStore(
        overview_path=overview_path,
        model_summary_path=sample_artifacts_dir / "v1_model_summary.json",
        overview_term="2024-2",
        warnings_path=warnings_path,
        repo_root=tmp_path,
    )
    monkeypatch.setattr(main_module, "get_store", lambda: store)
    client = TestClient(app)

    response = client.get("/api/analytics/overview", params={"term": "2024-1"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["meta"]["term"] == "2024-1"
    assert payload["data"]["student_count"] == 24
    assert payload["data"]["group_distribution"] == {
        "综合发展优势组": 1,
        "课堂参与薄弱组": 2,
    }
    assert payload["data"]["major_risk_summary"] == [
        {
            "major_name": "电子信息工程",
            "student_count": 1,
            "high_risk_count": 1,
            "average_risk_probability": 0.91,
        },
        {
            "major_name": "软件工程",
            "student_count": 2,
            "high_risk_count": 0,
            "average_risk_probability": 0.42,
        },
    ]
    assert payload["data"]["summary_term"] == "2024-1"
    assert payload["data"]["summary_source"] == "term_fallback"
    assert payload["data"]["summary_unavailable_fields"] == ["trend_summary"]
    assert payload["data"]["trend_summary"] is None
    assert payload["data"]["dimension_summary"] == [
        {
            "feature": "attendance",
            "feature_cn": "课堂学习投入",
            "dimension": "课堂参与表现",
            "average_score": 0.44,
            "score_count": 3,
        }
    ]


def test_get_overview_exposes_risk_band_distribution_and_factor_summary(client) -> None:
    response = client.get("/api/analytics/overview", params={"term": "2024-2"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["code"] == 200
    assert "risk_band_distribution" in payload["data"]
    assert "risk_factor_summary" in payload["data"]


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


def test_get_groups_exposes_risk_fields(client) -> None:
    response = client.get("/api/analytics/groups", params={"term": "2023-1"})
    assert response.status_code == 200
    payload = response.json()
    group = payload["data"]["groups"][0]
    assert "avg_risk_score" in group
    assert "avg_risk_level" in group
    assert "risk_amplifiers" in group
    assert "protective_factors" in group


def test_get_models_summary_returns_envelope_payload(client) -> None:
    response = client.get("/api/models/summary", params={"term": "2024-2"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["code"] == 200
    assert payload["data"]["cluster_method"] == "stub-eight-dimension-group-rules"
    assert payload["data"]["risk_model"] == "stub-eight-dimension-risk-rules"
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


def test_get_warnings_exposes_richer_warning_fields(client) -> None:
    response = client.get("/api/warnings", params={"term": "2023-1"})
    assert response.status_code == 200
    payload = response.json()
    item = payload["data"]["items"][0]
    assert "base_risk_score" in item
    assert "risk_adjustment_score" in item
    assert "adjusted_risk_score" in item
    assert "risk_delta" in item
    assert "risk_change_direction" in item
    assert "top_risk_factors" in item
    assert "top_protective_factors" in item


def test_get_student_profile_returns_404_for_unknown_student(client) -> None:
    response = client.get("/api/students/404/profile", params={"term": "2023-1"})
    assert response.status_code == 404


def test_get_student_profile_returns_calibrated_dimension_payload(
    monkeypatch, tmp_path: Path, sample_artifacts_dir: Path
) -> None:
    calibrated_dimension_scores = [
        {
            "dimension": "学业基础表现",
            "score": 0.88,
            "level": "high",
            "label": "学业基础稳健",
            "metrics": [{"name": "GPA", "value": 3.8, "display": "3.8"}],
            "explanation": "GPA 与不及格课程表现稳定。",
        }
    ]
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
                "dimension_scores_json": json.dumps(calibrated_dimension_scores, ensure_ascii=False),
            }
        ]
    ).to_csv(warnings_path, index=False, encoding="utf-8-sig")
    reports_path = tmp_path / "artifacts" / "model_stubs" / "v1_student_reports.jsonl"
    reports_path.write_text("", encoding="utf-8")
    store = DemoApiStore(
        overview_path=sample_artifacts_dir / "v1_overview_by_term.json",
        model_summary_path=sample_artifacts_dir / "v1_model_summary.json",
        overview_term="2024-2",
        warnings_path=warnings_path,
        repo_root=tmp_path,
    )
    monkeypatch.setattr(main_module, "get_store", lambda: store)
    client = TestClient(app)

    response = client.get("/api/students/20230001/profile", params={"term": "2023-1"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["code"] == 200
    first_dimension = payload["data"]["dimension_scores"][0]
    assert first_dimension == calibrated_dimension_scores[0]


def test_get_student_profile_includes_risk_metadata(client) -> None:
    response = client.get("/api/students/20230001/profile", params={"term": "2023-1"})
    assert response.status_code == 200
    payload = response.json()
    assert "base_risk_score" in payload["data"]
    assert "risk_change_direction" in payload["data"]
    assert "base_risk_explanation" in payload["data"]
    assert "behavior_adjustment_explanation" in payload["data"]
    assert "risk_change_explanation" in payload["data"]


def test_get_student_report_returns_404_for_unknown_student(client) -> None:
    response = client.get("/api/students/404/report", params={"term": "2023-1"})
    assert response.status_code == 404


def test_get_student_profile_accepts_blank_dimension_scores_json(
    monkeypatch, tmp_path: Path, sample_artifacts_dir: Path
) -> None:
    warnings_path = tmp_path / "artifacts" / "model_stubs" / "v1_student_results.csv"
    warnings_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        [
            {
                "student_id": "20230012",
                "term_key": "2023-1",
                "student_name": "Luna",
                "major_name": "软件工程",
                "group_segment": "综合发展优势组",
                "risk_probability": 0.55,
                "risk_level": "low",
                "dimension_scores_json": "",
                "top_risk_factors_json": json.dumps([], ensure_ascii=False),
                "top_protective_factors_json": json.dumps([], ensure_ascii=False),
                "base_risk_explanation": "base",
                "behavior_adjustment_explanation": "adjust",
                "risk_change_explanation": "change",
            }
        ]
    ).to_csv(warnings_path, index=False, encoding="utf-8-sig")
    reports_path = tmp_path / "artifacts" / "model_stubs" / "v1_student_reports.jsonl"
    reports_path.write_text("", encoding="utf-8")

    store = DemoApiStore(
        overview_path=sample_artifacts_dir / "v1_overview_by_term.json",
        model_summary_path=sample_artifacts_dir / "v1_model_summary.json",
        overview_term="2024-2",
        warnings_path=warnings_path,
        repo_root=tmp_path,
    )
    monkeypatch.setattr(main_module, "get_store", lambda: store)
    client = TestClient(app)

    response = client.get("/api/students/20230012/profile", params={"term": "2023-1"})

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["dimension_scores"] == []
    assert payload["trend"][0]["dimension_scores"] == []


def test_get_student_report_includes_risk_explanations(client) -> None:
    response = client.get("/api/students/20230001/report", params={"term": "2023-1"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["base_risk_explanation"] == "base risk explanation"
    assert payload["data"]["behavior_adjustment_explanation"] == "behavior adjustment explanation"
    assert payload["data"]["risk_change_explanation"] == "risk change explanation"
    assert "intervention_plan" in payload["data"]
    assert "risk_level" in payload["data"]
    assert "risk_delta" in payload["data"]
    assert "risk_change_direction" in payload["data"]
    assert "trend" in payload["data"]


def test_get_student_report_falls_back_to_warning_explanations(
    monkeypatch, tmp_path: Path, sample_artifacts_dir: Path
) -> None:
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
                "base_risk_explanation": "warning base",
                "behavior_adjustment_explanation": "warning adjust",
                "risk_change_explanation": "warning change",
                "dimension_scores_json": json.dumps([], ensure_ascii=False),
            }
        ]
    ).to_csv(warnings_path, index=False, encoding="utf-8-sig")
    reports_path = tmp_path / "artifacts" / "model_stubs" / "v1_student_reports.jsonl"
    reports_path.parent.mkdir(parents=True, exist_ok=True)
    reports_path.write_text(
        json.dumps(
            {
                "student_id": "20230001",
                "term_key": "2023-1",
                "student_name": "Bob",
                "major_name": "软件工程",
                "top_factors": [],
                "intervention_advice": [],
                "report_text": "report",
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    store = DemoApiStore(
        overview_path=sample_artifacts_dir / "v1_overview_by_term.json",
        model_summary_path=sample_artifacts_dir / "v1_model_summary.json",
        overview_term="2024-2",
        warnings_path=warnings_path,
        repo_root=tmp_path,
    )
    monkeypatch.setattr(main_module, "get_store", lambda: store)
    client = TestClient(app)

    response = client.get("/api/students/20230001/report", params={"term": "2023-1"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["base_risk_explanation"] == "warning base"
    assert payload["data"]["behavior_adjustment_explanation"] == "warning adjust"
    assert payload["data"]["risk_change_explanation"] == "warning change"


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
