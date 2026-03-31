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
        "group_distribution": {
            "学习投入稳定组": 58,
            "综合发展优势组": 73,
            "作息失衡风险组": 21,
            "课堂参与薄弱组": 27,
        },
        "major_risk_summary": [],
        "trend_summary": {
            "terms": [
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
        "cluster_method": "stub-group-rules",
        "risk_model": "stub-risk-rules",
        "target_label": "risk_level",
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
                "risk_level": "high",
                "dimension_scores_json": json.dumps([], ensure_ascii=False),
            },
            {
                "student_id": "20230001",
                "term_key": "2023-1",
                "student_name": "Bob",
                "major_name": "软件工程",
                "group_segment": "综合发展优势组",
                "risk_probability": 0.81,
                "risk_level": "medium",
                "dimension_scores_json": json.dumps(
                    [{"dimension": "学业基础表现", "score": 88}],
                    ensure_ascii=False,
                ),
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
