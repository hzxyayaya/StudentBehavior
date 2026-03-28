import json
from pathlib import Path

import pandas as pd
import pytest

from student_behavior_demo_api.services import DemoApiStore


@pytest.fixture
def sample_store(tmp_path: Path, sample_artifacts_dir: Path) -> DemoApiStore:
    artifact_root = sample_artifacts_dir
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
                "student_id": "20230004",
                "term_key": "2023-1",
                "student_name": "Dora",
                "major_name": "软件工程",
                "quadrant_label": "被动守纪型",
                "risk_probability": 0.77,
                "risk_level": "medium",
                "dimension_scores_json": json.dumps(
                    [
                        {"dimension": "学业基础表现", "score": 84},
                        {"dimension": "课堂参与表现", "score": 71},
                    ],
                    ensure_ascii=False,
                ),
            },
            {
                "student_id": "20230005",
                "term_key": "2023-1",
                "student_name": "Evan",
                "major_name": "软件工程",
                "quadrant_label": "被动守纪型",
                "risk_probability": 0.73,
                "risk_level": "medium",
                "dimension_scores_json": json.dumps(
                    [
                        {"dimension": "学业基础表现", "score": 83},
                        {"dimension": "课堂参与表现", "score": 73},
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
                    "top_factors": [
                        {"dimension": "课堂学习投入", "importance": 0.4},
                        {"dimension": "作业完成度", "importance": 0.95},
                    ],
                    "intervention_advice": ["继续保持稳定节奏"],
                    "report_text": "2022-2 report",
                },
                {
                    "student_id": "20230001",
                    "term_key": "2023-1",
                    "student_name": "Bob",
                    "major_name": "软件工程",
                    "top_factors": [
                        {"dimension": "课堂学习投入", "importance": 0.3},
                    ],
                    "intervention_advice": ["优先关注课程作业完成质量"],
                    "report_text": "2023-1 report",
                },
                {
                    "student_id": "20230004",
                    "term_key": "2023-1",
                    "student_name": "Dora",
                    "major_name": "软件工程",
                    "top_factors": [
                        {"dimension": "课堂学习投入", "importance": 0.2},
                        {"dimension": "作业完成度", "importance": 0.99},
                    ],
                    "intervention_advice": ["优先关注课堂投入"],
                    "report_text": "2023-1 report for Dora",
                },
                {
                    "student_id": "20230005",
                    "term_key": "2023-1",
                    "student_name": "Evan",
                    "major_name": "软件工程",
                    "top_factors": [
                        "课堂参与表现",
                        "课堂学习投入",
                        "课堂参与表现",
                    ],
                    "intervention_advice": ["优先关注课堂互动"],
                    "report_text": "2023-1 report for Evan",
                },
                {
                    "student_id": "20230002",
                    "term_key": "2023-1",
                    "student_name": "Alice",
                    "major_name": "软件工程",
                    "top_factors": [
                        {"dimension": "作业完成度", "importance": 0.99},
                    ],
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


@pytest.mark.parametrize("term_key", ["2023-2", "2024-1", "2024-2"])
def test_get_overview_accepts_all_real_terms(sample_store, term_key: str) -> None:
    payload = sample_store.get_overview(term_key)
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


def test_get_quadrants_groups_students_by_quadrant(sample_store) -> None:
    payload = sample_store.get_quadrants(term="2023-1")
    assert {item["quadrant_label"] for item in payload["quadrants"]} == {
        "被动守纪型",
        "情绪驱动型",
    }
    assert all("avg_risk_probability" in item for item in payload["quadrants"])
    passive = next(item for item in payload["quadrants"] if item["quadrant_label"] == "被动守纪型")
    assert passive["avg_risk_probability"] == pytest.approx((0.81 + 0.77 + 0.73) / 3)


def test_get_quadrants_aggregates_top_factors_from_reports(sample_store) -> None:
    payload = sample_store.get_quadrants(term="2023-1")
    passive = next(item for item in payload["quadrants"] if item["quadrant_label"] == "被动守纪型")
    counts = {item["dimension"]: item["count"] for item in passive["top_factors"]}
    assert counts["课堂参与表现"] == 2
    assert counts["课堂学习投入"] == 3
    assert counts["课堂参与表现"] != counts["课堂学习投入"]


def test_get_quadrants_raises_for_invalid_report_top_factors_schema(
    tmp_path: Path, sample_artifacts_dir: Path
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
                "quadrant_label": "被动守纪型",
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

    with pytest.raises(ValueError, match="top_factors must be a list"):
        store.get_quadrants(term="2023-1")


def test_get_quadrants_raises_for_invalid_report_top_factors_item_schema(
    tmp_path: Path, sample_artifacts_dir: Path
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
                "quadrant_label": "被动守纪型",
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

    with pytest.raises(ValueError, match="top_factors items must be strings or factor objects"):
        store.get_quadrants(term="2023-1")


def test_get_student_profile_uses_injected_results_path(
    tmp_path: Path, sample_artifacts_dir: Path
) -> None:
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
        overview_path=sample_artifacts_dir / "v1_overview_by_term.json",
        model_summary_path=sample_artifacts_dir / "v1_model_summary.json",
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
