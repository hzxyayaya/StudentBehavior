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
                "group_segment": "综合发展优势组",
                "risk_probability": 0.55,
                "risk_level": "low",
                "dimension_scores_json": json.dumps(
                    [
                        {"dimension": "学业基础表现", "score": 82},
                        {"dimension": "课堂学习投入", "score": 74},
                        {"dimension": "在线学习积极性", "score": 78},
                        {"dimension": "图书馆沉浸度", "score": 72},
                        {"dimension": "网络作息自律指数", "score": 68},
                        {"dimension": "早晚生活作息规律", "score": 71},
                        {"dimension": "体质及运动状况", "score": 75},
                        {"dimension": "综合荣誉与异动预警", "score": 73},
                    ],
                    ensure_ascii=False,
                ),
            },
            {
                "student_id": "20230002",
                "term_key": "2023-1",
                "student_name": "Alice",
                "major_name": "软件工程",
                "group_segment": "课堂参与薄弱组",
                "risk_probability": 0.92,
                "risk_level": "high",
                "dimension_scores_json": json.dumps(
                    [
                        {"dimension": "学业基础表现", "score": 91},
                        {"dimension": "课堂学习投入", "score": 48},
                        {"dimension": "在线学习积极性", "score": 57},
                        {"dimension": "图书馆沉浸度", "score": 62},
                        {"dimension": "网络作息自律指数", "score": 44},
                        {"dimension": "早晚生活作息规律", "score": 51},
                        {"dimension": "体质及运动状况", "score": 70},
                        {"dimension": "综合荣誉与异动预警", "score": 68},
                    ],
                    ensure_ascii=False,
                ),
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
                    [
                        {"dimension": "学业基础表现", "score": 88},
                        {"dimension": "课堂学习投入", "score": 79},
                        {"dimension": "在线学习积极性", "score": 81},
                        {"dimension": "图书馆沉浸度", "score": 76},
                        {"dimension": "网络作息自律指数", "score": 66},
                        {"dimension": "早晚生活作息规律", "score": 74},
                        {"dimension": "体质及运动状况", "score": 83},
                        {"dimension": "综合荣誉与异动预警", "score": 80},
                    ],
                    ensure_ascii=False,
                ),
            },
            {
                "student_id": "20230004",
                "term_key": "2023-1",
                "student_name": "Dora",
                "major_name": "软件工程",
                "group_segment": "综合发展优势组",
                "risk_probability": 0.77,
                "risk_level": "medium",
                "dimension_scores_json": json.dumps(
                    [
                        {"dimension": "学业基础表现", "score": 84},
                        {"dimension": "课堂学习投入", "score": 71},
                        {"dimension": "在线学习积极性", "score": 73},
                        {"dimension": "图书馆沉浸度", "score": 75},
                        {"dimension": "网络作息自律指数", "score": 63},
                        {"dimension": "早晚生活作息规律", "score": 69},
                        {"dimension": "体质及运动状况", "score": 82},
                        {"dimension": "综合荣誉与异动预警", "score": 78},
                    ],
                    ensure_ascii=False,
                ),
            },
            {
                "student_id": "20230005",
                "term_key": "2023-1",
                "student_name": "Evan",
                "major_name": "软件工程",
                "group_segment": "综合发展优势组",
                "risk_probability": 0.73,
                "risk_level": "medium",
                "dimension_scores_json": json.dumps(
                    [
                        {"dimension": "学业基础表现", "score": 83},
                        {"dimension": "课堂学习投入", "score": 73},
                        {"dimension": "在线学习积极性", "score": 76},
                        {"dimension": "图书馆沉浸度", "score": 78},
                        {"dimension": "网络作息自律指数", "score": 64},
                        {"dimension": "早晚生活作息规律", "score": 70},
                        {"dimension": "体质及运动状况", "score": 79},
                        {"dimension": "综合荣誉与异动预警", "score": 81},
                    ],
                    ensure_ascii=False,
                ),
            },
            {
                "student_id": "20230003",
                "term_key": "2024-1",
                "student_name": "Carol",
                "major_name": "软件工程",
                "group_segment": "学习投入稳定组",
                "risk_probability": 0.65,
                "risk_level": "low",
                "dimension_scores_json": json.dumps(
                    [
                        {"dimension": "学业基础表现", "score": 95},
                        {"dimension": "课堂学习投入", "score": 87},
                        {"dimension": "在线学习积极性", "score": 86},
                        {"dimension": "图书馆沉浸度", "score": 80},
                        {"dimension": "网络作息自律指数", "score": 76},
                        {"dimension": "早晚生活作息规律", "score": 82},
                        {"dimension": "体质及运动状况", "score": 88},
                        {"dimension": "综合荣誉与异动预警", "score": 84},
                    ],
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
                        {"dimension": "网络作息自律指数", "importance": 0.95},
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
                        {"dimension": "图书馆沉浸度", "importance": 0.99},
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
                        "课堂学习投入",
                        "课堂学习投入",
                        "课堂学习投入",
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
                        {"dimension": "课堂学习投入", "importance": 0.99},
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
    assert len(payload["dimension_summary"]) == 8


@pytest.mark.parametrize(
    ("term_key", "student_count", "risk_distribution", "group_distribution", "major_risk_summary"),
    [
        ("2023-2", 0, {"high": 0, "medium": 0, "low": 0}, {}, []),
        (
            "2024-1",
            1,
            {"high": 0, "medium": 0, "low": 1},
            {"学习投入稳定组": 1},
            [
                {
                    "major_name": "软件工程",
                    "student_count": 1,
                    "high_risk_count": 0,
                    "average_risk_probability": 0.65,
                }
            ],
        ),
        ("2024-2", 179, {"high": 12, "medium": 64, "low": 103}, None, None),
    ],
)
def test_get_overview_accepts_all_real_terms(
    sample_store,
    term_key: str,
    student_count: int,
    risk_distribution: dict[str, int],
    group_distribution: dict[str, int] | None,
    major_risk_summary: list[dict[str, object]] | None,
) -> None:
    payload = sample_store.get_overview(term_key)
    assert payload["student_count"] == student_count
    assert payload["risk_distribution"] == risk_distribution
    if group_distribution is not None:
        assert payload["group_distribution"] == group_distribution
        assert payload["major_risk_summary"] == major_risk_summary
        assert payload["summary_term"] == term_key
        assert payload["summary_source"] == "term_fallback"
        assert payload["summary_unavailable_fields"] == ["trend_summary"]
        assert payload["trend_summary"] is None
    else:
        assert "summary_source" not in payload


def test_get_model_summary_returns_stub_summary(sample_store) -> None:
    payload = sample_store.get_model_summary(term="2024-2")
    assert payload["risk_model"] == "stub-eight-dimension-risk-rules"


def test_get_student_profile_expands_dimension_scores(sample_store) -> None:
    payload = sample_store.get_student_profile(student_id="20230001", term="2023-1")
    assert payload["dimension_scores"][0]["dimension"] == "学业基础表现"
    assert payload["group_segment"] == "综合发展优势组"
    assert len(payload["dimension_scores"]) == 8


def test_get_student_profile_builds_sorted_trend(sample_store) -> None:
    payload = sample_store.get_student_profile(student_id="20230001", term="2023-1")
    assert [item["term"] for item in payload["trend"]] == ["2022-2", "2023-1"]


def test_get_student_profile_preserves_calibrated_dimension_objects(
    tmp_path: Path, sample_artifacts_dir: Path
) -> None:
    calibrated_dimension_scores = [
        {
            "dimension": "学业基础表现",
            "score": 0.88,
            "level": "high",
            "label": "学业基础稳健",
            "metrics": [{"name": "GPA", "value": 3.8, "display": "3.8"}],
            "explanation": "GPA 与不及格课程表现稳定。",
        },
        {
            "dimension": "课堂学习投入",
            "score": 0.79,
            "level": "medium",
            "label": "课堂投入基本稳定",
            "metrics": [{"name": "attendance_rate", "value": 0.91, "display": "91%"}],
            "explanation": "课堂出勤稳定，但仍有提升空间。",
        },
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
            },
            {
                "student_id": "20230001",
                "term_key": "2024-1",
                "student_name": "Bob",
                "major_name": "软件工程",
                "group_segment": "综合发展优势组",
                "risk_probability": 0.74,
                "risk_level": "low",
                "dimension_scores_json": json.dumps(calibrated_dimension_scores, ensure_ascii=False),
            },
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

    payload = store.get_student_profile(student_id="20230001", term="2023-1")

    assert payload["dimension_scores"] == calibrated_dimension_scores
    assert payload["trend"][0]["dimension_scores"] == calibrated_dimension_scores
    assert payload["trend"][1]["dimension_scores"] == calibrated_dimension_scores


def test_get_student_report_returns_exact_term_record(sample_store) -> None:
    payload = sample_store.get_student_report(student_id="20230001", term="2023-1")
    assert set(payload) == {"top_factors", "intervention_advice", "report_text"}
    assert payload["intervention_advice"][0].startswith("优先")


def test_get_groups_groups_students_by_group_segment(sample_store) -> None:
    payload = sample_store.get_groups(term="2023-1")
    assert {item["group_segment"] for item in payload["groups"]} == {
        "综合发展优势组",
        "课堂参与薄弱组",
    }
    assert all("avg_risk_probability" in item for item in payload["groups"])
    dominant = next(item for item in payload["groups"] if item["group_segment"] == "综合发展优势组")
    assert dominant["avg_risk_probability"] == pytest.approx((0.81 + 0.77 + 0.73) / 3)
    assert len(dominant["avg_dimension_scores"]) == 8


def test_get_groups_aggregates_top_factors_from_reports(sample_store) -> None:
    payload = sample_store.get_groups(term="2023-1")
    dominant = next(item for item in payload["groups"] if item["group_segment"] == "综合发展优势组")
    counts = {item["dimension"]: item["count"] for item in dominant["top_factors"]}
    assert counts["图书馆沉浸度"] == 1
    assert counts["课堂学习投入"] == 3
    assert counts["图书馆沉浸度"] != counts["课堂学习投入"]


def test_get_groups_preserves_richer_factor_summary_fields(
    tmp_path: Path, sample_artifacts_dir: Path
) -> None:
    artifact_root = sample_artifacts_dir
    calibrated_scores = [
        {
            "feature": "class_engagement",
            "feature_cn": "课堂学习投入",
            "dimension": "课堂学习投入",
            "score": 0.48,
            "level": "low",
            "label": "课堂投入不足",
            "metrics": [{"name": "attendance_rate", "value": 0.63, "display": "63%"}],
            "explanation": "课堂到课率偏低。",
        }
    ]
    warnings_path = tmp_path / "artifacts" / "model_stubs" / "v1_student_results.csv"
    warnings_path.parent.mkdir(parents=True, exist_ok=True)
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
                "dimension_scores_json": json.dumps(calibrated_scores, ensure_ascii=False),
            }
        ]
    ).to_csv(warnings_path, index=False, encoding="utf-8-sig")
    reports_path = tmp_path / "artifacts" / "model_stubs" / "v1_student_reports.jsonl"
    reports_path.write_text(
        json.dumps(
            {
                "student_id": "20230002",
                "term_key": "2023-1",
                "student_name": "Alice",
                "major_name": "软件工程",
                "top_factors": [
                    {
                        "feature": "class_engagement",
                        "feature_cn": "课堂学习投入",
                        "effect": "negative",
                        "importance": 0.99,
                    }
                ],
                "intervention_advice": ["优先补齐课堂互动"],
                "report_text": "2023-1 report for Alice",
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

    payload = store.get_groups(term="2023-1")

    assert payload["groups"][0]["avg_dimension_scores"] == [
        {
            "feature": "class_engagement",
            "feature_cn": "课堂学习投入",
            "dimension": "课堂学习投入",
            "level": "low",
            "label": "课堂投入不足",
            "metrics": [{"name": "attendance_rate", "value": 0.63, "display": "63%"}],
            "explanation": "课堂到课率偏低。",
            "average_score": 0.48,
            "score_count": 1,
        }
    ]
    assert payload["groups"][0]["top_factors"] == [
        {
            "dimension": "课堂学习投入",
            "importance": 0.99,
            "count": 1,
            "feature": "class_engagement",
            "feature_cn": "课堂学习投入",
            "effect": "negative",
        }
    ]


def test_get_overview_preserves_richer_dimension_summary_when_present(
    tmp_path: Path, sample_artifacts_dir: Path
) -> None:
    overview_path = tmp_path / "artifacts" / "model_stubs" / "v1_overview_by_term.json"
    overview_path.parent.mkdir(parents=True, exist_ok=True)
    rich_dimension_summary = [
        {
            "dimension": "学业基础表现",
            "average_score": 0.78,
            "label": "学业基础稳健",
            "level": "high",
            "metrics": [{"name": "GPA", "value": 3.2, "display": "3.2"}],
            "explanation": "整体 GPA 保持稳定。",
        }
    ]
    overview_payload = json.loads(
        (sample_artifacts_dir / "v1_overview_by_term.json").read_text(encoding="utf-8")
    )
    overview_payload["dimension_summary"] = rich_dimension_summary
    overview_path.write_text(json.dumps(overview_payload, ensure_ascii=False), encoding="utf-8")

    store = DemoApiStore(
        overview_path=overview_path,
        model_summary_path=sample_artifacts_dir / "v1_model_summary.json",
        overview_term="2024-2",
        warnings_path=sample_artifacts_dir / "v1_student_results.csv",
        repo_root=tmp_path,
    )

    payload = store.get_overview("2024-2")

    assert payload["dimension_summary"] == rich_dimension_summary


def test_get_overview_uses_term_specific_fallback_when_stub_is_multi_term(
    tmp_path: Path, sample_artifacts_dir: Path
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
                        "label": "课堂投入稳定",
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
                            "label": "课堂投入偏弱",
                            "metrics": [{"name": "attendance_rate", "value": 0.63}],
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
                            "label": "课堂投入偏弱",
                            "metrics": [{"name": "attendance_rate", "value": 0.66}],
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
                            "label": "课堂投入偏弱",
                            "metrics": [{"name": "attendance_rate", "value": 0.61}],
                        }
                    ],
                    ensure_ascii=False,
                ),
            },
            {
                "student_id": "20230003",
                "term_key": "2024-2",
                "student_name": "Carol",
                "major_name": "软件工程",
                "group_segment": "学习投入稳定组",
                "risk_probability": 0.82,
                "risk_level": "medium",
                "dimension_scores_json": json.dumps(
                    [
                        {
                            "feature": "attendance",
                            "feature_cn": "课堂学习投入",
                            "dimension": "课堂学习投入",
                            "score": 0.91,
                            "label": "课堂投入稳定",
                            "metrics": [{"name": "attendance_rate", "value": 0.92}],
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

    payload = store.get_overview("2024-1")

    assert payload["student_count"] == 24
    assert payload["risk_distribution"] == {"high": 2, "medium": 6, "low": 16}
    assert payload["group_distribution"] == {
        "综合发展优势组": 1,
        "课堂参与薄弱组": 2,
    }
    assert payload["major_risk_summary"] == [
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
    assert payload["summary_term"] == "2024-1"
    assert payload["summary_source"] == "term_fallback"
    assert payload["summary_unavailable_fields"] == ["trend_summary"]
    assert payload["trend_summary"] is None
    assert payload["dimension_summary"] == [
        {
            "feature": "attendance",
            "feature_cn": "课堂学习投入",
            "dimension": "课堂参与表现",
            "label": "课堂投入偏弱",
            "metrics": [{"name": "attendance_rate", "value": 0.63}],
            "average_score": 0.44,
            "score_count": 3,
        }
    ]


def test_get_groups_uses_canonical_factor_identity_for_mixed_payloads(
    tmp_path: Path, sample_artifacts_dir: Path
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
                "group_segment": "课堂参与薄弱组",
                "risk_probability": 0.91,
                "risk_level": "high",
                "dimension_scores_json": json.dumps([], ensure_ascii=False),
            },
            {
                "student_id": "20230002",
                "term_key": "2023-1",
                "student_name": "Alice",
                "major_name": "软件工程",
                "group_segment": "课堂参与薄弱组",
                "risk_probability": 0.89,
                "risk_level": "high",
                "dimension_scores_json": json.dumps([], ensure_ascii=False),
            },
            {
                "student_id": "20230003",
                "term_key": "2023-1",
                "student_name": "Carol",
                "major_name": "软件工程",
                "group_segment": "课堂参与薄弱组",
                "risk_probability": 0.87,
                "risk_level": "medium",
                "dimension_scores_json": json.dumps([], ensure_ascii=False),
            },
        ]
    ).to_csv(warnings_path, index=False, encoding="utf-8-sig")
    reports_path = tmp_path / "artifacts" / "model_stubs" / "v1_student_reports.jsonl"
    reports_path.write_text(
        "\n".join(
            json.dumps(record, ensure_ascii=False)
            for record in [
                {
                    "student_id": "20230001",
                    "term_key": "2023-1",
                    "student_name": "Bob",
                    "major_name": "软件工程",
                    "top_factors": [
                        {
                            "feature": "class_engagement",
                            "feature_cn": "课堂学习投入",
                            "dimension": "课堂参与表现",
                            "effect": "negative",
                            "importance": 0.61,
                        }
                    ],
                    "intervention_advice": [],
                    "report_text": "r1",
                },
                {
                    "student_id": "20230002",
                    "term_key": "2023-1",
                    "student_name": "Alice",
                    "major_name": "软件工程",
                    "top_factors": [
                        {
                            "feature": "class_engagement",
                            "feature_cn": "课堂学习投入",
                            "dimension": "课堂学习投入",
                            "effect": "negative",
                            "importance": 0.99,
                        }
                    ],
                    "intervention_advice": [],
                    "report_text": "r2",
                },
                {
                    "student_id": "20230003",
                    "term_key": "2023-1",
                    "student_name": "Carol",
                    "major_name": "软件工程",
                    "top_factors": [
                        {
                            "feature": "class_engagement",
                            "feature_cn": "课堂学习投入",
                            "importance": 0.72,
                        }
                    ],
                    "intervention_advice": [],
                    "report_text": "r3",
                },
            ]
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

    payload = store.get_groups(term="2023-1")

    assert payload["groups"][0]["top_factors"] == [
        {
            "feature": "class_engagement",
            "feature_cn": "课堂学习投入",
            "dimension": "课堂参与表现",
            "effect": "negative",
            "importance": 0.99,
            "count": 3,
        }
    ]


def test_get_groups_raises_for_invalid_report_top_factors_schema(
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

    with pytest.raises(ValueError, match="top_factors must be a list"):
        store.get_groups(term="2023-1")


def test_get_groups_raises_for_invalid_report_top_factors_item_schema(
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

    with pytest.raises(ValueError, match="top_factors items must be strings or factor objects"):
        store.get_groups(term="2023-1")


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
                "group_segment": "综合发展优势组",
                "risk_probability": 0.55,
                "risk_level": "low",
                "dimension_scores_json": json.dumps(
                    [
                        {"dimension": "学业基础表现", "score": 82},
                        {"dimension": "课堂学习投入", "score": 74},
                        {"dimension": "在线学习积极性", "score": 78},
                        {"dimension": "图书馆沉浸度", "score": 72},
                        {"dimension": "网络作息自律指数", "score": 68},
                        {"dimension": "早晚生活作息规律", "score": 71},
                        {"dimension": "体质及运动状况", "score": 75},
                        {"dimension": "综合荣誉与异动预警", "score": 73},
                    ],
                    ensure_ascii=False,
                ),
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
                    [
                        {"dimension": "学业基础表现", "score": 88},
                        {"dimension": "课堂学习投入", "score": 79},
                        {"dimension": "在线学习积极性", "score": 81},
                        {"dimension": "图书馆沉浸度", "score": 76},
                        {"dimension": "网络作息自律指数", "score": 66},
                        {"dimension": "早晚生活作息规律", "score": 74},
                        {"dimension": "体质及运动状况", "score": 83},
                        {"dimension": "综合荣誉与异动预警", "score": 80},
                    ],
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
    assert len(payload["trend"][0]["dimension_scores"]) == 8


def test_list_warnings_filters_by_term_and_risk_level(sample_store) -> None:
    payload = sample_store.list_warnings(term="2023-1", risk_level="high")
    assert payload["total"] == 1
    assert payload["items"][0]["risk_level"] == "high"


def test_list_warnings_filters_by_group_segment(sample_store) -> None:
    payload = sample_store.list_warnings(term="2023-1", group_segment="综合发展优势组")
    assert payload["total"] == 3
    assert all(item["group_segment"] == "综合发展优势组" for item in payload["items"])


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
