import json
from pathlib import Path

import pandas as pd
import pytest

import student_behavior_demo_api.main as main_module
from student_behavior_demo_api.services import DemoApiStore


@pytest.fixture
def sample_artifacts_dir(tmp_path: Path) -> Path:
    artifact_dir = tmp_path / "artifacts" / "model_stubs"
    artifact_dir.mkdir(parents=True, exist_ok=True)

    overview_payload = {
        "student_count": 179,
        "risk_distribution": {"high": 12, "medium": 64, "low": 103},
        "risk_band_distribution": {"高风险": 12, "较高风险": 24, "一般风险": 40, "低风险": 103},
        "risk_factor_summary": [
            {"feature": "academic_base", "feature_cn": "学业基础表现", "count": 12},
            {"feature": "class_engagement", "feature_cn": "课堂学习投入", "count": 9},
        ],
        "group_distribution": {
            "学习投入稳定组": 58,
            "综合发展优势组": 73,
            "作息失衡风险组": 21,
            "课堂参与薄弱组": 27,
        },
        "dimension_summary": [
            {"dimension": "学业基础表现", "average_score": 78.2},
            {"dimension": "课堂学习投入", "average_score": 73.4},
            {"dimension": "在线学习积极性", "average_score": 75.8},
            {"dimension": "图书馆沉浸度", "average_score": 69.1},
            {"dimension": "网络作息自律指数", "average_score": 66.0},
            {"dimension": "早晚生活作息规律", "average_score": 71.9},
            {"dimension": "体质及运动状况", "average_score": 74.3},
            {"dimension": "综合荣誉与异动预警", "average_score": 70.5},
        ],
        "major_risk_summary": [],
        "trend_summary": {
            "terms": [
                {"term_key": "2023-1"},
                {"term_key": "2023-2"},
                {"term_key": "2024-1"},
                {"term_key": "2024-2"},
            ]
        }
    }
    (artifact_dir / "v1_overview_by_term.json").write_text(
        json.dumps(overview_payload, ensure_ascii=False),
        encoding="utf-8",
    )

    model_summary_payload = {
        "cluster_method": "stub-eight-dimension-group-rules",
        "risk_model": "stub-eight-dimension-risk-rules",
        "target_label": "学期级八维学业风险",
        "auc": 0.91,
        "updated_at": "2024-09-01T00:00:00Z",
    }
    (artifact_dir / "v1_model_summary.json").write_text(
        json.dumps(model_summary_payload, ensure_ascii=False),
        encoding="utf-8",
    )

    warnings_path = artifact_dir / "v1_student_results.csv"
    pd.DataFrame(
        [
            {
                "student_id": "20230002",
                "term_key": "2023-1",
                "student_name": "Alice",
                "major_name": "软件工程",
                "group_segment": "课堂参与薄弱组",
                "risk_probability": 0.92,
                "base_risk_score": 82.0,
                "risk_adjustment_score": 6.0,
                "adjusted_risk_score": 88.0,
                "risk_level": "high",
                "risk_delta": 2.0,
                "risk_change_direction": "rising",
                "dimension_scores_json": json.dumps([], ensure_ascii=False),
                "top_risk_factors_json": json.dumps(
                    [
                        {"feature": "academic_base", "feature_cn": "学业基础表现", "importance": 0.9},
                    ],
                    ensure_ascii=False,
                ),
                "top_protective_factors_json": json.dumps(
                    [
                        {"feature": "class_engagement", "feature_cn": "课堂学习投入", "importance": 0.2},
                    ],
                    ensure_ascii=False,
                ),
                "base_risk_explanation": "base risk explanation",
                "behavior_adjustment_explanation": "behavior adjustment explanation",
                "risk_change_explanation": "risk change explanation",
            },
            {
                "student_id": "20230001",
                "term_key": "2023-1",
                "student_name": "Bob",
                "major_name": "软件工程",
                "group_segment": "综合发展优势组",
                "risk_probability": 0.81,
                "base_risk_score": 62.0,
                "risk_adjustment_score": -2.0,
                "adjusted_risk_score": 60.0,
                "risk_level": "medium",
                "risk_delta": -1.0,
                "risk_change_direction": "falling",
                "dimension_scores_json": json.dumps(
                    [
                        {"dimension": "学业基础表现", "score": 88},
                        {"dimension": "课堂学习投入", "score": 80},
                        {"dimension": "在线学习积极性", "score": 82},
                        {"dimension": "图书馆沉浸度", "score": 77},
                        {"dimension": "网络作息自律指数", "score": 65},
                        {"dimension": "早晚生活作息规律", "score": 72},
                        {"dimension": "体质及运动状况", "score": 84},
                        {"dimension": "综合荣誉与异动预警", "score": 79},
                    ],
                    ensure_ascii=False,
                ),
                "top_risk_factors_json": json.dumps(
                    [
                        {"feature": "academic_base", "feature_cn": "学业基础表现", "importance": 0.7},
                    ],
                    ensure_ascii=False,
                ),
                "top_protective_factors_json": json.dumps(
                    [
                        {"feature": "library_immersion", "feature_cn": "图书馆沉浸度", "importance": 0.4},
                    ],
                    ensure_ascii=False,
                ),
                "base_risk_explanation": "base risk explanation",
                "behavior_adjustment_explanation": "behavior adjustment explanation",
                "risk_change_explanation": "risk change explanation",
            },
        ]
    ).to_csv(warnings_path, index=False, encoding="utf-8-sig")

    reports_path = artifact_dir / "v1_student_reports.jsonl"
    reports_path.write_text(
        "\n".join(
            json.dumps(record, ensure_ascii=False)
            for record in [
                {
                    "student_id": "20230001",
                    "term_key": "2022-2",
                    "student_name": "Bob",
                    "major_name": "软件工程",
                    "top_factors": ["课堂学习投入"],
                    "intervention_advice": ["继续保持稳定节奏"],
                    "report_text": "2022-2 report",
                    "base_risk_explanation": "base risk explanation",
                    "behavior_adjustment_explanation": "behavior adjustment explanation",
                    "risk_change_explanation": "risk change explanation",
                    "intervention_plan": ["keep steady"],
                },
                {
                    "student_id": "20230001",
                    "term_key": "2023-1",
                    "student_name": "Bob",
                    "major_name": "软件工程",
                    "top_factors": ["网络作息自律指数"],
                    "intervention_advice": ["优先关注课程作业完成质量"],
                    "report_text": "2023-1 report",
                    "base_risk_explanation": "base risk explanation",
                    "behavior_adjustment_explanation": "behavior adjustment explanation",
                    "risk_change_explanation": "risk change explanation",
                    "intervention_plan": ["follow-up plan"],
                },
                {
                    "student_id": "20230002",
                    "term_key": "2023-1",
                    "student_name": "Alice",
                    "major_name": "软件工程",
                    "top_factors": ["课堂学习投入"],
                    "intervention_advice": ["优先补齐课堂互动"],
                    "report_text": "2023-1 report for Alice",
                    "base_risk_explanation": "base risk explanation",
                    "behavior_adjustment_explanation": "behavior adjustment explanation",
                    "risk_change_explanation": "risk change explanation",
                    "intervention_plan": ["priority plan"],
                },
            ]
        ),
        encoding="utf-8",
    )

    return artifact_dir


@pytest.fixture
def app_without_artifacts(monkeypatch: pytest.MonkeyPatch):
    class MissingArtifactStore:
        def get_overview(self, term: str) -> dict:
            raise FileNotFoundError("v1_overview_by_term.json")

        def get_model_summary(self, term: str | None = None) -> dict:
            raise FileNotFoundError("v1_model_summary.json")

        def get_groups(self, term: str) -> dict:
            raise FileNotFoundError("v1_student_results.csv")

        def get_student_profile(self, *, student_id: str, term: str) -> dict:
            raise FileNotFoundError("v1_student_results.csv")

        def get_student_report(self, *, student_id: str, term: str) -> dict:
            raise FileNotFoundError("v1_student_reports.jsonl")

        def list_warnings(self, **kwargs) -> dict:
            raise FileNotFoundError("v1_student_results.csv")

    monkeypatch.setattr(main_module, "get_store", lambda: MissingArtifactStore())
    return main_module.app
