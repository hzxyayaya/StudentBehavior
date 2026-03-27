import json
from pathlib import Path

import pandas as pd
import pytest

from student_behavior_demo_api.services import DemoApiStore


@pytest.fixture
def sample_store(tmp_path: Path) -> DemoApiStore:
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
                "student_id": "20230001",
                "term_key": "2022-2",
                "student_name": "Bob",
                "major_name": "软件工程",
                "quadrant_label": "被动守纪型",
                "risk_probability": 0.55,
                "risk_level": "low",
                "dimension_scores_json": json.dumps(
                    [
                        {"dimension": "学业基础表现", "score": 82},
                        {"dimension": "课堂参与表现", "score": 74},
                    ],
                    ensure_ascii=False,
                ),
            },
            {
                "student_id": "20230002",
                "term_key": "2023-1",
                "student_name": "Alice",
                "major_name": "软件工程",
                "quadrant_label": "情绪驱动型",
                "risk_probability": 0.92,
                "risk_level": "high",
                "dimension_scores_json": json.dumps(
                    [{"dimension": "学业基础表现", "score": 91}],
                    ensure_ascii=False,
                ),
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
                    [
                        {"dimension": "学业基础表现", "score": 88},
                        {"dimension": "课堂参与表现", "score": 79},
                    ],
                    ensure_ascii=False,
                ),
            },
            {
                "student_id": "20230003",
                "term_key": "2024-1",
                "student_name": "Carol",
                "major_name": "软件工程",
                "quadrant_label": "自律共鸣型",
                "risk_probability": 0.65,
                "risk_level": "low",
                "dimension_scores_json": json.dumps(
                    [{"dimension": "学业基础表现", "score": 95}],
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
    return DemoApiStore(
        overview_path=artifact_root / "v1_overview_by_term.json",
        model_summary_path=artifact_root / "v1_model_summary.json",
        overview_term="2024-2",
        warnings_path=warnings_path,
        repo_root=tmp_path,
    )


def test_get_overview_by_term_returns_single_term_payload(sample_store) -> None:
    payload = sample_store.get_overview("2024-2")
    assert payload["student_count"] == 179


def test_get_model_summary_returns_stub_summary(sample_store) -> None:
    payload = sample_store.get_model_summary(term="2024-2")
    assert payload["risk_model"] == "stub-risk-rules"


def test_get_student_profile_expands_dimension_scores(sample_store) -> None:
    payload = sample_store.get_student_profile(student_id="20230001", term="2023-1")
    assert payload["dimension_scores"][0]["dimension"] == "学业基础表现"


def test_get_student_profile_builds_sorted_trend(sample_store) -> None:
    payload = sample_store.get_student_profile(student_id="20230001", term="2023-1")
    assert [item["term"] for item in payload["trend"]] == ["2022-2", "2023-1"]


def test_get_student_report_returns_exact_term_record(sample_store) -> None:
    payload = sample_store.get_student_report(student_id="20230001", term="2023-1")
    assert set(payload) == {"top_factors", "intervention_advice", "report_text"}
    assert payload["intervention_advice"][0].startswith("优先")


def test_get_student_profile_uses_injected_results_path(tmp_path: Path) -> None:
    warnings_path = tmp_path / "custom" / "student_results.csv"
    warnings_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        [
            {
                "student_id": "20230001",
                "term_key": "2022-2",
                "student_name": "Bob",
                "major_name": "软件工程",
                "quadrant_label": "被动守纪型",
                "risk_probability": 0.55,
                "risk_level": "low",
                "dimension_scores_json": json.dumps(
                    [{"dimension": "学业基础表现", "score": 82}],
                    ensure_ascii=False,
                ),
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

    store = DemoApiStore(
        overview_path=(
            Path(__file__).resolve().parents[4]
            / "v1-model-stubs"
            / "artifacts"
            / "model_stubs"
            / "v1_overview_by_term.json"
        ),
        model_summary_path=(
            Path(__file__).resolve().parents[4]
            / "v1-model-stubs"
            / "artifacts"
            / "model_stubs"
            / "v1_model_summary.json"
        ),
        overview_term="2024-2",
        warnings_path=warnings_path,
        repo_root=tmp_path,
    )

    payload = store.get_student_profile(student_id="20230001", term="2023-1")

    assert payload["dimension_scores"][0]["dimension"] == "学业基础表现"
    assert [item["term"] for item in payload["trend"]] == ["2022-2", "2023-1"]


def test_list_warnings_filters_by_term_and_risk_level(sample_store) -> None:
    payload = sample_store.list_warnings(term="2023-1", risk_level="high")
    assert payload["total"] == 1
    assert payload["items"][0]["risk_level"] == "high"


def test_list_warnings_sorts_by_risk_probability_desc_then_student_id(sample_store) -> None:
    payload = sample_store.list_warnings(term="2023-1", page=1, page_size=2)
    assert [item["student_id"] for item in payload["items"]] == ["20230002", "20230001"]


def test_list_warnings_raises_for_unknown_term(sample_store) -> None:
    with pytest.raises(KeyError, match="2099-1"):
        sample_store.list_warnings(term="2099-1")


def test_missing_default_artifact_resolution_only_uses_current_worktree(tmp_path: Path) -> None:
    current_artifact_root = tmp_path / "artifacts" / "model_stubs"
    sibling_artifact_root = tmp_path.parent / "v1-model-stubs" / "artifacts" / "model_stubs"
    sibling_artifact_root.mkdir(parents=True)
    (sibling_artifact_root / "v1_overview_by_term.json").write_text("{}", encoding="utf-8")
    (sibling_artifact_root / "v1_model_summary.json").write_text("{}", encoding="utf-8")

    with pytest.raises(FileNotFoundError):
        DemoApiStore(repo_root=tmp_path)
