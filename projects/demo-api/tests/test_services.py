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
                "base_risk_score": 55.0,
                "risk_adjustment_score": -1.0,
                "adjusted_risk_score": 54.0,
                "risk_level": "low",
                "risk_delta": 0.0,
                "risk_change_direction": "steady",
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
                "top_risk_factors_json": json.dumps(
                    [{"feature": "academic_base", "feature_cn": "学业基础表现", "importance": 0.6}],
                    ensure_ascii=False,
                ),
                "top_protective_factors_json": json.dumps(
                    [{"feature": "class_engagement", "feature_cn": "课堂学习投入", "importance": 0.2}],
                    ensure_ascii=False,
                ),
                "base_risk_explanation": "base explanation",
                "behavior_adjustment_explanation": "adjustment explanation",
                "risk_change_explanation": "change explanation",
            },
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
                "top_risk_factors_json": json.dumps(
                    [{"feature": "academic_base", "feature_cn": "学业基础表现", "importance": 0.9}],
                    ensure_ascii=False,
                ),
                "top_protective_factors_json": json.dumps(
                    [{"feature": "library_immersion", "feature_cn": "图书馆沉浸度", "importance": 0.3}],
                    ensure_ascii=False,
                ),
                "base_risk_explanation": "base explanation",
                "behavior_adjustment_explanation": "adjustment explanation",
                "risk_change_explanation": "change explanation",
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
                "top_risk_factors_json": json.dumps(
                    [{"feature": "academic_base", "feature_cn": "学业基础表现", "importance": 0.7}],
                    ensure_ascii=False,
                ),
                "top_protective_factors_json": json.dumps(
                    [{"feature": "class_engagement", "feature_cn": "课堂学习投入", "importance": 0.2}],
                    ensure_ascii=False,
                ),
                "base_risk_explanation": "base explanation",
                "behavior_adjustment_explanation": "adjustment explanation",
                "risk_change_explanation": "change explanation",
            },
            {
                "student_id": "20230004",
                "term_key": "2023-1",
                "student_name": "Dora",
                "major_name": "软件工程",
                "group_segment": "综合发展优势组",
                "risk_probability": 0.77,
                "base_risk_score": 60.0,
                "risk_adjustment_score": 1.0,
                "adjusted_risk_score": 61.0,
                "risk_level": "medium",
                "risk_delta": 0.5,
                "risk_change_direction": "steady",
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
                "top_risk_factors_json": json.dumps(
                    [{"feature": "online_activeness", "feature_cn": "在线学习积极性", "importance": 0.5}],
                    ensure_ascii=False,
                ),
                "top_protective_factors_json": json.dumps(
                    [{"feature": "library_immersion", "feature_cn": "图书馆沉浸度", "importance": 0.4}],
                    ensure_ascii=False,
                ),
                "base_risk_explanation": "base explanation",
                "behavior_adjustment_explanation": "adjustment explanation",
                "risk_change_explanation": "change explanation",
            },
            {
                "student_id": "20230005",
                "term_key": "2023-1",
                "student_name": "Evan",
                "major_name": "软件工程",
                "group_segment": "综合发展优势组",
                "risk_probability": 0.73,
                "base_risk_score": 58.0,
                "risk_adjustment_score": -1.0,
                "adjusted_risk_score": 57.0,
                "risk_level": "medium",
                "risk_delta": -0.5,
                "risk_change_direction": "falling",
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
                "top_risk_factors_json": json.dumps(
                    [{"feature": "academic_base", "feature_cn": "学业基础表现", "importance": 0.6}],
                    ensure_ascii=False,
                ),
                "top_protective_factors_json": json.dumps(
                    [{"feature": "class_engagement", "feature_cn": "课堂学习投入", "importance": 0.2}],
                    ensure_ascii=False,
                ),
                "base_risk_explanation": "base explanation",
                "behavior_adjustment_explanation": "adjustment explanation",
                "risk_change_explanation": "change explanation",
            },
            {
                "student_id": "20230003",
                "term_key": "2024-1",
                "student_name": "Carol",
                "major_name": "软件工程",
                "group_segment": "学习投入稳定组",
                "risk_probability": 0.65,
                "base_risk_score": 50.0,
                "risk_adjustment_score": -3.0,
                "adjusted_risk_score": 47.0,
                "risk_level": "low",
                "risk_delta": -2.0,
                "risk_change_direction": "falling",
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
                "top_risk_factors_json": json.dumps(
                    [{"feature": "academic_base", "feature_cn": "学业基础表现", "importance": 0.4}],
                    ensure_ascii=False,
                ),
                "top_protective_factors_json": json.dumps(
                    [{"feature": "physical_resilience", "feature_cn": "体质及运动状况", "importance": 0.5}],
                    ensure_ascii=False,
                ),
                "base_risk_explanation": "base explanation",
                "behavior_adjustment_explanation": "adjustment explanation",
                "risk_change_explanation": "change explanation",
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


def test_get_overview_exposes_risk_band_distribution_and_factor_summary(
    tmp_path: Path, sample_artifacts_dir: Path
) -> None:
    overview_path = tmp_path / "artifacts" / "model_stubs" / "v1_overview_by_term.json"
    overview_path.parent.mkdir(parents=True, exist_ok=True)
    overview_path.write_text(
        json.dumps(
            {
                "student_count": 2,
                "risk_distribution": {"high": 1, "medium": 1, "low": 0},
                "risk_band_distribution": {"高风险": 1, "较高风险": 1, "一般风险": 0, "低风险": 0},
                "risk_factor_summary": [
                    {"feature": "academic_base", "feature_cn": "学业基础表现", "count": 2},
                ],
                "group_distribution": {"课堂参与薄弱组": 2},
                "major_risk_summary": [],
                "trend_summary": {"terms": [{"term_key": "2024-2"}]},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    warnings_path = tmp_path / "artifacts" / "model_stubs" / "v1_student_results.csv"
    warnings_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        [
            {
                "student_id": "20230001",
                "term_key": "2024-2",
                "student_name": "Bob",
                "major_name": "软件工程",
                "group_segment": "课堂参与薄弱组",
                "risk_probability": 0.52,
                "base_risk_score": 52.0,
                "risk_adjustment_score": 5.0,
                "adjusted_risk_score": 57.0,
                "risk_level": "较高风险",
                "risk_delta": 5.0,
                "risk_change_direction": "rising",
                "dimension_scores_json": json.dumps([], ensure_ascii=False),
                "top_risk_factors_json": json.dumps([], ensure_ascii=False),
                "top_protective_factors_json": json.dumps([], ensure_ascii=False),
                "base_risk_explanation": "base",
                "behavior_adjustment_explanation": "adjust",
                "risk_change_explanation": "change",
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


def test_overview_dimension_summary_prefers_available_dimension_details(sample_store: DemoApiStore) -> None:
    warnings_path = Path(sample_store._warnings_path)
    rows = pd.read_csv(warnings_path)
    rows.loc[rows["term_key"] == "2024-1", "dimension_scores_json"] = json.dumps(
        [
            {
                "dimension": "课堂学习投入",
                "dimension_code": "class_engagement",
                "score": 0.0,
                "level": "unavailable",
                "label": "当前学期无有效数据",
                "metrics": [],
                "explanation": "课堂学习投入当前学期无有效源表指标，暂不做该维度判定。",
                "provenance": {
                    "is_unavailable": True,
                    "unavailable_reason": "no_metrics",
                },
            },
            {
                "dimension": "图书馆沉浸度",
                "dimension_code": "library_immersion",
                "score": 0.0,
                "level": "unavailable",
                "label": "当前学期无有效数据",
                "metrics": [],
                "explanation": "图书馆沉浸度当前学期无有效源表指标，暂不做该维度判定。",
                "provenance": {
                    "is_unavailable": True,
                    "unavailable_reason": "no_metrics",
                },
            },
        ],
        ensure_ascii=False,
    )
    rows = pd.concat(
        [
            rows,
            pd.DataFrame(
                [
                    {
                        "student_id": "20239999",
                        "term_key": "2024-1",
                        "student_name": "Faye",
                        "major_name": "软件工程",
                        "group_segment": "学习投入稳定组",
                        "risk_probability": 0.42,
                        "base_risk_score": 42.0,
                        "risk_adjustment_score": 0.0,
                        "adjusted_risk_score": 42.0,
                        "risk_level": "low",
                        "risk_delta": 0.0,
                        "risk_change_direction": "steady",
                        "dimension_scores_json": json.dumps(
                            [
                                {
                                    "dimension": "课堂学习投入",
                                    "dimension_code": "class_engagement",
                                    "score": 0.64,
                                    "level": "medium",
                                    "label": "课堂投入稳定",
                                    "metrics": [
                                        {"name": "出勤率", "value": 0.93},
                                    ],
                                    "explanation": "课堂投入整体稳定，出勤率表现较好。",
                                    "provenance": {"is_unavailable": False},
                                }
                            ],
                            ensure_ascii=False,
                        ),
                        "top_risk_factors_json": "[]",
                        "top_protective_factors_json": "[]",
                        "base_risk_explanation": "base explanation",
                        "behavior_adjustment_explanation": "adjustment explanation",
                        "risk_change_explanation": "change explanation",
                    }
                ]
            ),
        ],
        ignore_index=True,
    )
    rows.to_csv(warnings_path, index=False, encoding="utf-8-sig")

    overview = sample_store.get_overview("2024-1")
    dimension_summary = {
        item["dimension_code"]: item for item in overview["dimension_summary"]
    }

    class_summary = dimension_summary["class_engagement"]
    assert class_summary["label"] == "课堂投入稳定"
    assert class_summary["metrics"] == [{"name": "出勤率", "value": 0.93}]
    assert class_summary["explanation"] == "课堂投入整体稳定，出勤率表现较好。"
    assert class_summary["provenance"] == {"is_unavailable": False}


def test_get_trajectory_analysis_repackages_overview_groups_and_warning_samples(sample_store: DemoApiStore) -> None:
    payload = sample_store.get_trajectory_analysis(term="2024-1")

    assert payload["term"] == "2024-1"
    assert payload["risk_trend_summary"]
    assert payload["current_dimensions"]
    assert payload["key_factors"]
    assert payload["group_changes"]
    assert payload["student_samples"]
    assert payload["student_samples"][0]["student_id"] == "20230003"
    assert payload["student_samples"][0]["top_risk_factors"][0]["feature_cn"] == "学业基础表现"


def test_get_development_analysis_repackages_major_group_and_dimension_views(sample_store: DemoApiStore) -> None:
    payload = sample_store.get_development_analysis(term="2024-1")

    assert payload["term"] == "2024-1"
    assert payload["major_comparison"]
    assert payload["group_direction_segments"]
    assert payload["dimension_highlights"]
    assert payload["direction_chains"]
    assert payload["disclaimer"] == "去向分析已接入真实毕业去向数据；无匹配数据时相关字段返回空结果"
    assert payload["group_direction_segments"][0]["group_segment"]
    assert "direction_label" in payload["group_direction_segments"][0]


def test_get_development_analysis_exposes_destination_analysis_when_available(
    tmp_path: Path, sample_artifacts_dir: Path
) -> None:
    overview_path = tmp_path / "artifacts" / "model_stubs" / "v1_overview_by_term.json"
    overview_path.parent.mkdir(parents=True, exist_ok=True)
    overview_path.write_text(
        json.dumps(
            {
                "student_count": 1,
                "risk_distribution": {"high": 0, "medium": 1, "low": 0},
                "risk_band_distribution": {"高风险": 0, "较高风险": 1, "一般风险": 0, "低风险": 0},
                "group_distribution": {"综合发展优势组": 1},
                "major_risk_summary": [],
                "destination_distribution": {"升学": 1},
                "major_destination_summary": [
                    {
                        "major_name": "软件工程",
                        "student_count": 1,
                        "destination_student_count": 1,
                        "top_destination_label": "升学",
                        "top_destination_count": 1,
                        "destination_distribution": {"升学": 1},
                    }
                ],
                "group_destination_association": [
                    {
                        "group_segment": "综合发展优势组",
                        "destination_label": "升学",
                        "student_count": 1,
                        "group_student_count": 1,
                        "share_within_group": 1.0,
                    }
                ],
                "dimension_summary": [{"dimension": "学业基础表现", "average_score": 0.82}],
                "trend_summary": {"terms": [{"term_key": "2024-2"}]},
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
                "term_key": "2024-2",
                "student_name": "Bob",
                "major_name": "软件工程",
                "group_segment": "综合发展优势组",
                "risk_probability": 0.52,
                "base_risk_score": 52.0,
                "risk_adjustment_score": -1.0,
                "adjusted_risk_score": 51.0,
                "risk_level": "一般风险",
                "risk_delta": -1.0,
                "risk_change_direction": "falling",
                "dimension_scores_json": json.dumps(
                    [{"dimension": "学业基础表现", "score": 82}],
                    ensure_ascii=False,
                ),
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
        overview_path=overview_path,
        model_summary_path=sample_artifacts_dir / "v1_model_summary.json",
        overview_term="2024-2",
        warnings_path=warnings_path,
        repo_root=tmp_path,
    )

    payload = store.get_development_analysis(term="2024-2")

    assert payload["destination_distribution"] == {"升学": 1}
    assert payload["major_destination_summary"] == [
        {
            "major_name": "软件工程",
            "student_count": 1,
            "destination_student_count": 1,
            "top_destination_label": "升学",
            "top_destination_count": 1,
            "destination_distribution": {"升学": 1},
        }
    ]
    assert payload["group_destination_association"] == [
        {
            "group_segment": "综合发展优势组",
            "destination_label": "升学",
            "student_count": 1,
            "group_student_count": 1,
            "share_within_group": 1.0,
        }
    ]
    assert payload["destination_segments"] == payload["group_destination_association"]
    assert payload["major_destination_comparison"] == payload["major_destination_summary"]
    assert payload["behavior_destination_association"] == payload["group_destination_association"]
    assert payload["disclaimer"] == "去向分析已接入真实毕业去向数据；无匹配数据时相关字段返回空结果"


def test_get_development_analysis_rebuilds_destination_analysis_for_term_fallback(
    tmp_path: Path, sample_artifacts_dir: Path
) -> None:
    overview_path = tmp_path / "artifacts" / "model_stubs" / "v1_overview_by_term.json"
    overview_path.parent.mkdir(parents=True, exist_ok=True)
    overview_path.write_text(
        json.dumps(
            {
                "student_count": 2,
                "risk_distribution": {"高风险": 0, "较高风险": 0, "一般风险": 1, "低风险": 1},
                "risk_band_distribution": {"高风险": 0, "较高风险": 0, "一般风险": 1, "低风险": 1},
                "group_distribution": {"作息失衡风险组": 2},
                "major_risk_summary": [],
                "trend_summary": {
                    "terms": [
                        {
                            "term_key": "2024-2",
                            "student_count": 2,
                            "risk_distribution": {"高风险": 0, "较高风险": 0, "一般风险": 1, "低风险": 1},
                        }
                    ]
                },
                "dimension_summary": [],
                "risk_factor_summary": [],
                "destination_distribution": {},
                "major_destination_summary": [],
                "group_destination_association": [],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    warnings_path = tmp_path / "artifacts" / "model_stubs" / "v1_student_results.csv"
    pd.DataFrame(
        [
            {
                "student_id": "20240001",
                "term_key": "2024-2",
                "student_name": "Alice",
                "major_name": "软件工程",
                "destination_label": "升学",
                "destination_source": "byqx_study",
                "group_segment": "作息失衡风险组",
                "risk_probability": 0.61,
                "risk_level": "一般风险",
                "dimension_scores_json": "[]",
            },
            {
                "student_id": "20240002",
                "term_key": "2024-2",
                "student_name": "Bob",
                "major_name": "软件工程",
                "destination_label": "企业就业",
                "destination_source": "byqx_employment",
                "group_segment": "作息失衡风险组",
                "risk_probability": 0.39,
                "risk_level": "低风险",
                "dimension_scores_json": "[]",
            },
        ]
    ).to_csv(warnings_path, index=False, encoding="utf-8-sig")

    store = DemoApiStore(
        overview_path=overview_path,
        model_summary_path=sample_artifacts_dir / "v1_model_summary.json",
        overview_term="2023-2",
        warnings_path=warnings_path,
        repo_root=tmp_path,
    )

    payload = store.get_development_analysis(term="2024-2")

    assert payload["destination_distribution"] == {"企业就业": 1, "升学": 1}
    assert payload["major_destination_summary"] == [
        {
            "major_name": "软件工程",
            "student_count": 2,
            "destination_student_count": 2,
            "top_destination_label": "企业就业",
            "top_destination_count": 1,
            "destination_distribution": {"企业就业": 1, "升学": 1},
        }
    ]
    assert payload["group_destination_association"] == [
        {
            "group_segment": "作息失衡风险组",
            "destination_label": "企业就业",
            "student_count": 1,
            "group_student_count": 2,
            "share_within_group": 0.5,
        },
        {
            "group_segment": "作息失衡风险组",
            "destination_label": "升学",
            "student_count": 1,
            "group_student_count": 2,
            "share_within_group": 0.5,
        },
    ]
    assert payload["disclaimer"] == "去向分析已接入真实毕业去向数据；无匹配数据时相关字段返回空结果"


def test_result_outputs_expose_destination_analysis_when_available(
    tmp_path: Path, sample_artifacts_dir: Path
) -> None:
    overview_path = tmp_path / "artifacts" / "model_stubs" / "v1_overview_by_term.json"
    overview_path.parent.mkdir(parents=True, exist_ok=True)
    overview_path.write_text(
        json.dumps(
            {
                "student_count": 1,
                "risk_distribution": {"high": 0, "medium": 1, "low": 0},
                "risk_band_distribution": {"高风险": 0, "较高风险": 1, "一般风险": 0, "低风险": 0},
                "group_distribution": {"综合发展优势组": 1},
                "major_risk_summary": [],
                "destination_distribution": {"升学": 1},
                "major_destination_summary": [
                    {
                        "major_name": "软件工程",
                        "student_count": 1,
                        "destination_student_count": 1,
                        "top_destination_label": "升学",
                        "top_destination_count": 1,
                        "destination_distribution": {"升学": 1},
                    }
                ],
                "group_destination_association": [
                    {
                        "group_segment": "综合发展优势组",
                        "destination_label": "升学",
                        "student_count": 1,
                        "group_student_count": 1,
                        "share_within_group": 1.0,
                    }
                ],
                "dimension_summary": [{"dimension": "学业基础表现", "average_score": 0.82}],
                "trend_summary": {"terms": [{"term_key": "2024-2"}]},
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
                "term_key": "2024-2",
                "student_name": "Bob",
                "major_name": "软件工程",
                "group_segment": "综合发展优势组",
                "risk_probability": 0.52,
                "base_risk_score": 52.0,
                "risk_adjustment_score": -1.0,
                "adjusted_risk_score": 51.0,
                "risk_level": "一般风险",
                "risk_delta": -1.0,
                "risk_change_direction": "falling",
                "dimension_scores_json": json.dumps(
                    [{"dimension": "学业基础表现", "score": 82}],
                    ensure_ascii=False,
                ),
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
        overview_path=overview_path,
        model_summary_path=sample_artifacts_dir / "v1_model_summary.json",
        overview_term="2024-2",
        warnings_path=warnings_path,
        repo_root=tmp_path,
    )

    major_payload = store.get_result_major_comparison(term="2024-2")
    behavior_payload = store.get_result_behavior_patterns(term="2024-2")

    assert major_payload["destination_distribution"] == {"升学": 1}
    assert major_payload["major_destination_summary"] == [
        {
            "major_name": "软件工程",
            "student_count": 1,
            "destination_student_count": 1,
            "top_destination_label": "升学",
            "top_destination_count": 1,
            "destination_distribution": {"升学": 1},
        }
    ]
    assert major_payload["major_destination_comparison"] == major_payload["major_destination_summary"]
    assert behavior_payload["behavior_destination_association"] == [
        {
            "group_segment": "综合发展优势组",
            "destination_label": "升学",
            "student_count": 1,
            "group_student_count": 1,
            "share_within_group": 1.0,
        }
    ]
    assert behavior_payload["destination_segments"] == behavior_payload["behavior_destination_association"]


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
                        "elevated_risk_count": 0,
                        "elevated_risk_ratio": 0.0,
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


def test_get_model_summary_preserves_legacy_stub_shape(sample_store) -> None:
    payload = sample_store.get_model_summary(term="2024-2")

    assert payload == {
        "cluster_method": "stub-eight-dimension-group-rules",
        "risk_model": "stub-eight-dimension-risk-rules",
        "target_label": "学期级八维学业风险",
        "auc": 0.91,
        "updated_at": "2024-09-01T00:00:00Z",
    }


def test_get_model_summary_exposes_trained_metrics_when_present(
    tmp_path: Path, sample_artifacts_dir: Path
) -> None:
    trained_summary_path = tmp_path / "artifacts" / "model_stubs" / "v1_model_summary.json"
    trained_summary_path.parent.mkdir(parents=True, exist_ok=True)
    trained_summary_path.write_text(
        json.dumps(
            {
                "cluster_method": "stub-eight-dimension-group-rules",
                "risk_model": "trained-academic-risk-model",
                "target_label": "学期级八维学业风险",
                "auc": 0.9342,
                "updated_at": "2026-04-09T09:00:00Z",
                "source": "trained",
                "accuracy": 0.88,
                "precision": 0.81,
                "recall": 0.79,
                "f1": 0.8,
                "trained_at": "2026-04-08T18:15:00Z",
                "evaluated_at": "2026-04-09T09:00:00Z",
                "train_sample_count": 120,
                "valid_sample_count": 30,
                "test_sample_count": 50,
                "feature_count": 64,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    store = DemoApiStore(
        overview_path=sample_artifacts_dir / "v1_overview_by_term.json",
        model_summary_path=trained_summary_path,
        overview_term="2024-2",
        warnings_path=sample_artifacts_dir / "v1_student_results.csv",
        repo_root=sample_artifacts_dir.parent.parent,
    )

    payload = store.get_model_summary(term="2024-2")

    assert payload["cluster_method"] == "stub-eight-dimension-group-rules"
    assert payload["risk_model"] == "trained-academic-risk-model"
    assert payload["source"] == "trained"
    assert payload["accuracy"] == 0.88
    assert payload["precision"] == 0.81
    assert payload["recall"] == 0.79
    assert payload["f1"] == 0.8
    assert payload["trained_at"] == "2026-04-08T18:15:00Z"
    assert payload["evaluated_at"] == "2026-04-09T09:00:00Z"
    assert payload["train_sample_count"] == 120
    assert payload["valid_sample_count"] == 30
    assert payload["test_sample_count"] == 50
    assert payload["feature_count"] == 64


def test_get_result_model_summary_preserves_reserved_api_fields(
    tmp_path: Path, sample_artifacts_dir: Path
) -> None:
    trained_summary_path = tmp_path / "artifacts" / "model_stubs" / "v1_model_summary.json"
    trained_summary_path.parent.mkdir(parents=True, exist_ok=True)
    trained_summary_path.write_text(
        json.dumps(
            {
                "cluster_method": "stub-eight-dimension-group-rules",
                "risk_model": "trained-academic-risk-model",
                "target_label": "学期级八维学业风险",
                "auc": 0.9342,
                "updated_at": "2026-04-09T09:00:00Z",
                "source": "trained",
                "term": "artifact-term",
                "result_key": "artifact-result-key",
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    store = DemoApiStore(
        overview_path=sample_artifacts_dir / "v1_overview_by_term.json",
        model_summary_path=trained_summary_path,
        overview_term="2024-2",
        warnings_path=sample_artifacts_dir / "v1_student_results.csv",
        repo_root=sample_artifacts_dir.parent.parent,
    )

    payload = store.get_result_model_summary(term="2024-2")

    assert payload["result_key"] == "model_summary"
    assert payload["term"] == "2024-2"
    assert payload["risk_model"] == "trained-academic-risk-model"
    assert "artifact-result-key" not in payload.values()
    assert "artifact-term" not in payload.values()


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
    assert set(payload) == {
        "top_factors",
        "intervention_advice",
        "report_text",
        "base_risk_explanation",
        "behavior_adjustment_explanation",
        "risk_change_explanation",
        "intervention_plan",
        "risk_level",
        "risk_probability",
        "base_risk_score",
        "risk_adjustment_score",
        "adjusted_risk_score",
        "risk_delta",
        "risk_change_direction",
        "trend",
    }
    assert payload["intervention_advice"][0].startswith("优先")


def test_get_result_intervention_advice_preserves_legacy_shape(sample_store) -> None:
    payload = sample_store.get_result_intervention_advice(student_id="20230001", term="2023-1")

    assert set(payload) == {
        "result_key",
        "term",
        "student_id",
        "intervention_advice",
        "report_text",
        "top_factors",
    }


def test_report_endpoints_surface_optional_llm_metadata(
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
                "group_segment": "综合发展优势组",
                "risk_probability": 0.81,
                "base_risk_score": 62.0,
                "risk_adjustment_score": -2.0,
                "adjusted_risk_score": 60.0,
                "risk_level": "medium",
                "risk_delta": -1.0,
                "risk_change_direction": "falling",
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
                "top_factors": [{"dimension": "课堂学习投入", "importance": 0.3}],
                "intervention_advice": ["优先关注课程作业完成质量"],
                "report_text": "2023-1 report",
                "report_source": "llm_stub",
                "prompt_version": "prompt-v3",
                "report_generation": {
                    "model": "stub-llm",
                    "generated_at": "2026-04-09T09:00:00Z",
                },
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

    report_payload = store.get_student_report(student_id="20230001", term="2023-1")
    intervention_payload = store.get_result_intervention_advice(student_id="20230001", term="2023-1")

    assert report_payload["report_source"] == "llm_stub"
    assert report_payload["prompt_version"] == "prompt-v3"
    assert report_payload["report_generation"] == {
        "model": "stub-llm",
        "generated_at": "2026-04-09T09:00:00Z",
    }
    assert intervention_payload["report_source"] == "llm_stub"
    assert intervention_payload["prompt_version"] == "prompt-v3"
    assert intervention_payload["report_generation"] == {
        "model": "stub-llm",
        "generated_at": "2026-04-09T09:00:00Z",
    }


def test_get_student_profile_includes_risk_metadata(sample_store) -> None:
    payload = sample_store.get_student_profile(student_id="20230001", term="2023-1")
    assert payload["risk_level"] == "medium"
    assert payload["base_risk_score"] == 62.0
    assert payload["risk_change_direction"] == "falling"


def test_get_student_report_includes_risk_explanations(
    tmp_path: Path, sample_artifacts_dir: Path
) -> None:
    warnings_path = tmp_path / "artifacts" / "model_stubs" / "v1_student_results.csv"
    warnings_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        [
            {
                "student_id": "20230001",
                "term_key": "2024-2",
                "student_name": "Bob",
                "major_name": "软件工程",
                "group_segment": "课堂参与薄弱组",
                "risk_probability": 0.52,
                "base_risk_score": 52.0,
                "risk_adjustment_score": 5.0,
                "adjusted_risk_score": 57.0,
                "risk_level": "较高风险",
                "risk_delta": 5.0,
                "risk_change_direction": "rising",
                "dimension_scores_json": json.dumps([], ensure_ascii=False),
                "top_risk_factors_json": json.dumps([], ensure_ascii=False),
                "top_protective_factors_json": json.dumps([], ensure_ascii=False),
                "base_risk_explanation": "base",
                "behavior_adjustment_explanation": "adjust",
                "risk_change_explanation": "change",
            },
        ]
    ).to_csv(warnings_path, index=False, encoding="utf-8-sig")
    reports_path = tmp_path / "artifacts" / "model_stubs" / "v1_student_reports.jsonl"
    reports_path.parent.mkdir(parents=True, exist_ok=True)
    reports_path.write_text(
        json.dumps(
            {
                "student_id": "20230001",
                "term_key": "2024-2",
                "student_name": "Bob",
                "major_name": "软件工程",
                "top_factors": [],
                "intervention_advice": ["plan"],
                "report_text": "report",
                "base_risk_explanation": "base",
                "behavior_adjustment_explanation": "adjust",
                "risk_change_explanation": "change",
                "intervention_plan": ["plan"],
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

    payload = store.get_student_report(student_id="20230001", term="2024-2")

    assert payload["base_risk_explanation"] == "base"
    assert payload["behavior_adjustment_explanation"] == "adjust"
    assert payload["risk_change_explanation"] == "change"
    assert payload["intervention_plan"] == ["plan"]


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


def test_get_groups_exposes_risk_summaries_and_factors(
    tmp_path: Path, sample_artifacts_dir: Path
) -> None:
    warnings_path = tmp_path / "artifacts" / "model_stubs" / "v1_student_results.csv"
    warnings_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        [
            {
                "student_id": "20230001",
                "term_key": "2024-2",
                "student_name": "Bob",
                "major_name": "软件工程",
                "group_segment": "课堂参与薄弱组",
                "risk_probability": 0.52,
                "base_risk_score": 52.0,
                "risk_adjustment_score": 5.0,
                "adjusted_risk_score": 57.0,
                "risk_level": "较高风险",
                "risk_delta": 5.0,
                "risk_change_direction": "rising",
                "dimension_scores_json": json.dumps([], ensure_ascii=False),
                "top_risk_factors_json": json.dumps(
                    [{"feature": "academic_base", "feature_cn": "学业基础表现", "importance": 0.9}],
                    ensure_ascii=False,
                ),
                "top_protective_factors_json": json.dumps(
                    [{"feature": "class_engagement", "feature_cn": "课堂学习投入", "importance": 0.2}],
                    ensure_ascii=False,
                ),
                "base_risk_explanation": "base",
                "behavior_adjustment_explanation": "adjust",
                "risk_change_explanation": "change",
            },
            {
                "student_id": "20230002",
                "term_key": "2024-2",
                "student_name": "Alice",
                "major_name": "软件工程",
                "group_segment": "课堂参与薄弱组",
                "risk_probability": 0.48,
                "base_risk_score": 48.0,
                "risk_adjustment_score": -3.0,
                "adjusted_risk_score": 45.0,
                "risk_level": "一般风险",
                "risk_delta": -2.0,
                "risk_change_direction": "falling",
                "dimension_scores_json": json.dumps([], ensure_ascii=False),
                "top_risk_factors_json": json.dumps(
                    [{"feature": "academic_base", "feature_cn": "学业基础表现", "importance": 0.7}],
                    ensure_ascii=False,
                ),
                "top_protective_factors_json": json.dumps(
                    [{"feature": "library_immersion", "feature_cn": "图书馆沉浸度", "importance": 0.4}],
                    ensure_ascii=False,
                ),
                "base_risk_explanation": "base",
                "behavior_adjustment_explanation": "adjust",
                "risk_change_explanation": "change",
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

    payload = store.get_groups(term="2024-2")

    group = payload["groups"][0]
    assert group["avg_risk_score"] == pytest.approx((57.0 + 45.0) / 2)
    assert group["avg_risk_level"] in {"较高风险", "一般风险"}
    assert group["risk_amplifiers"][0]["feature"] == "academic_base"
    assert group["protective_factors"][0]["feature"] in {"class_engagement", "library_immersion"}


def test_get_groups_aggregates_top_factors_from_reports(sample_store) -> None:
    payload = sample_store.get_groups(term="2023-1")
    dominant = next(item for item in payload["groups"] if item["group_segment"] == "综合发展优势组")
    counts = {item["dimension"]: item["count"] for item in dominant["top_factors"]}
    assert counts["图书馆沉浸度"] == 1
    assert counts["课堂学习投入"] == 3
    assert counts["图书馆沉浸度"] != counts["课堂学习投入"]


def test_get_groups_normalizes_report_ids_to_match_warning_rows(
    tmp_path: Path, sample_artifacts_dir: Path
) -> None:
    warnings_path = tmp_path / "artifacts" / "model_stubs" / "v1_student_results.csv"
    warnings_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        [
            {
                "student_id": "20230006",
                "term_key": "2023-1",
                "student_name": "Frank",
                "major_name": "软件工程",
                "group_segment": "综合发展优势组",
                "risk_probability": 0.66,
                "base_risk_score": 58.0,
                "risk_adjustment_score": -1.0,
                "adjusted_risk_score": 57.0,
                "risk_level": "medium",
                "risk_delta": -0.2,
                "risk_change_direction": "steady",
                "dimension_scores_json": json.dumps([], ensure_ascii=False),
                "top_risk_factors_json": json.dumps([], ensure_ascii=False),
                "top_protective_factors_json": json.dumps([], ensure_ascii=False),
                "base_risk_explanation": "base",
                "behavior_adjustment_explanation": "adjust",
                "risk_change_explanation": "change",
            }
        ]
    ).to_csv(warnings_path, index=False, encoding="utf-8-sig")
    reports_path = tmp_path / "artifacts" / "model_stubs" / "v1_student_reports.jsonl"
    reports_path.parent.mkdir(parents=True, exist_ok=True)
    reports_path.write_text(
        json.dumps(
            {
                "student_id": 20230006,
                "term_key": "2023-1",
                "student_name": "Frank",
                "major_name": "软件工程",
                "top_factors": [
                    {
                        "dimension": "课堂学习投入",
                        "importance": 0.8,
                        "feature": "class_engagement",
                        "feature_cn": "课堂学习投入",
                        "effect": "negative",
                    }
                ],
                "intervention_advice": ["补齐课堂互动"],
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

    payload = store.get_groups(term="2023-1")

    dominant = payload["groups"][0]
    assert dominant["top_factors"] == [
        {
            "dimension": "课堂学习投入",
            "importance": 0.8,
            "count": 1,
            "feature": "class_engagement",
            "feature_cn": "课堂学习投入",
            "effect": "negative",
        }
    ]


def test_get_groups_accepts_string_importance_in_report_factors(
    tmp_path: Path, sample_artifacts_dir: Path
) -> None:
    warnings_path = tmp_path / "artifacts" / "model_stubs" / "v1_student_results.csv"
    warnings_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        [
            {
                "student_id": "20230007",
                "term_key": "2023-1",
                "student_name": "Gina",
                "major_name": "软件工程",
                "group_segment": "综合发展优势组",
                "risk_probability": 0.66,
                "base_risk_score": 58.0,
                "risk_adjustment_score": -1.0,
                "adjusted_risk_score": 57.0,
                "risk_level": "medium",
                "risk_delta": -0.2,
                "risk_change_direction": "steady",
                "dimension_scores_json": json.dumps([], ensure_ascii=False),
                "top_risk_factors_json": json.dumps([], ensure_ascii=False),
                "top_protective_factors_json": json.dumps([], ensure_ascii=False),
                "base_risk_explanation": "base",
                "behavior_adjustment_explanation": "adjust",
                "risk_change_explanation": "change",
            }
        ]
    ).to_csv(warnings_path, index=False, encoding="utf-8-sig")
    reports_path = tmp_path / "artifacts" / "model_stubs" / "v1_student_reports.jsonl"
    reports_path.parent.mkdir(parents=True, exist_ok=True)
    reports_path.write_text(
        json.dumps(
            {
                "student_id": "20230007",
                "term_key": "2023-1",
                "student_name": "Gina",
                "major_name": "软件工程",
                "top_factors": [
                    {
                        "dimension": "图书馆沉浸度",
                        "importance": "0.6",
                        "feature": "library_immersion",
                        "feature_cn": "图书馆沉浸度",
                        "effect": "positive",
                    }
                ],
                "intervention_advice": ["增加自习"],
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

    payload = store.get_groups(term="2023-1")

    dominant = payload["groups"][0]
    assert dominant["top_factors"] == [
        {
            "dimension": "图书馆沉浸度",
            "importance": 0.6,
            "count": 1,
            "feature": "library_immersion",
            "feature_cn": "图书馆沉浸度",
            "effect": "positive",
        }
    ]


@pytest.mark.parametrize("importance_value", ["nan", "inf", "-inf", "not-a-number"])
def test_get_groups_rejects_non_finite_importance_in_report_factors(
    importance_value: str, tmp_path: Path, sample_artifacts_dir: Path
) -> None:
    warnings_path = tmp_path / "artifacts" / "model_stubs" / "v1_student_results.csv"
    warnings_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        [
            {
                "student_id": "20230008",
                "term_key": "2023-1",
                "student_name": "Hana",
                "major_name": "软件工程",
                "group_segment": "综合发展优势组",
                "risk_probability": 0.66,
                "base_risk_score": 58.0,
                "risk_adjustment_score": -1.0,
                "adjusted_risk_score": 57.0,
                "risk_level": "medium",
                "risk_delta": -0.2,
                "risk_change_direction": "steady",
                "dimension_scores_json": json.dumps([], ensure_ascii=False),
                "top_risk_factors_json": json.dumps([], ensure_ascii=False),
                "top_protective_factors_json": json.dumps([], ensure_ascii=False),
                "base_risk_explanation": "base",
                "behavior_adjustment_explanation": "adjust",
                "risk_change_explanation": "change",
            }
        ]
    ).to_csv(warnings_path, index=False, encoding="utf-8-sig")
    reports_path = tmp_path / "artifacts" / "model_stubs" / "v1_student_reports.jsonl"
    reports_path.parent.mkdir(parents=True, exist_ok=True)
    reports_path.write_text(
        json.dumps(
            {
                "student_id": "20230008",
                "term_key": "2023-1",
                "student_name": "Hana",
                "major_name": "软件工程",
                "top_factors": [
                    {
                        "dimension": "图书馆沉浸度",
                        "importance": importance_value,
                        "feature": "library_immersion",
                        "feature_cn": "图书馆沉浸度",
                        "effect": "positive",
                    }
                ],
                "intervention_advice": ["增加自习"],
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

    with pytest.raises(ValueError, match="top_factors items must be strings or factor objects"):
        store.get_groups(term="2023-1")


def test_get_student_profile_accepts_blank_dimension_scores_json(
    tmp_path: Path, sample_artifacts_dir: Path
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

    payload = store.get_student_profile(student_id="20230012", term="2023-1")

    assert payload["dimension_scores"] == []
    assert payload["trend"][0]["dimension_scores"] == []


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


def test_get_overview_enriches_sparse_dimension_summary_from_warning_rows(
    tmp_path: Path, sample_artifacts_dir: Path
) -> None:
    overview_path = tmp_path / "artifacts" / "model_stubs" / "v1_overview_by_term.json"
    overview_path.parent.mkdir(parents=True, exist_ok=True)
    overview_payload = json.loads(
        (sample_artifacts_dir / "v1_overview_by_term.json").read_text(encoding="utf-8")
    )
    overview_payload["dimension_summary"] = [
        {
            "dimension": "课堂学习投入",
            "dimension_code": "class_engagement",
            "average_score": 0.48,
        }
    ]
    overview_path.write_text(json.dumps(overview_payload, ensure_ascii=False), encoding="utf-8")

    warnings_path = tmp_path / "artifacts" / "model_stubs" / "v1_student_results.csv"
    calibrated_dimension_scores = [
        {
            "dimension": "课堂学习投入",
            "dimension_code": "class_engagement",
            "score": 0.48,
            "level": "low",
            "label": "课堂投入不足",
            "metrics": [{"name": "attendance_rate", "value": 0.63, "display": "63%"}],
            "explanation": "课堂到课率偏低。",
        }
    ]
    pd.DataFrame(
        [
            {
                "student_id": "20230001",
                "term_key": "2024-2",
                "student_name": "Bob",
                "major_name": "软件工程",
                "group_segment": "课堂参与薄弱组",
                "risk_probability": 0.81,
                "risk_level": "一般风险",
                "dimension_scores_json": json.dumps(calibrated_dimension_scores, ensure_ascii=False),
            },
            {
                "student_id": "20230002",
                "term_key": "2024-2",
                "student_name": "Alice",
                "major_name": "软件工程",
                "group_segment": "课堂参与薄弱组",
                "risk_probability": 0.83,
                "risk_level": "一般风险",
                "dimension_scores_json": json.dumps(calibrated_dimension_scores, ensure_ascii=False),
            },
        ]
    ).to_csv(warnings_path, index=False, encoding="utf-8-sig")

    store = DemoApiStore(
        overview_path=overview_path,
        model_summary_path=sample_artifacts_dir / "v1_model_summary.json",
        overview_term="2024-2",
        warnings_path=warnings_path,
        repo_root=tmp_path,
    )

    payload = store.get_overview("2024-2")

    assert payload["dimension_summary"] == [
        {
            "dimension": "课堂学习投入",
            "dimension_code": "class_engagement",
            "average_score": 0.48,
            "score_count": 2,
            "level": "low",
            "label": "课堂投入不足",
            "metrics": [{"name": "attendance_rate", "value": 0.63, "display": "63%"}],
            "explanation": "课堂到课率偏低。",
        }
    ]


def test_get_overview_prefers_richer_dimension_summary_fields_across_warning_rows(
    tmp_path: Path, sample_artifacts_dir: Path
) -> None:
    overview_path = tmp_path / "artifacts" / "model_stubs" / "v1_overview_by_term.json"
    overview_path.parent.mkdir(parents=True, exist_ok=True)
    overview_payload = json.loads(
        (sample_artifacts_dir / "v1_overview_by_term.json").read_text(encoding="utf-8")
    )
    overview_payload["dimension_summary"] = [
        {
            "dimension": "课堂学习投入",
            "dimension_code": "class_engagement",
            "average_score": 0.28,
        }
    ]
    overview_path.write_text(json.dumps(overview_payload, ensure_ascii=False), encoding="utf-8")

    warnings_path = tmp_path / "artifacts" / "model_stubs" / "v1_student_results.csv"
    pd.DataFrame(
        [
            {
                "student_id": "20230001",
                "term_key": "2024-2",
                "student_name": "Bob",
                "major_name": "软件工程",
                "group_segment": "课堂参与薄弱组",
                "risk_probability": 0.81,
                "risk_level": "一般风险",
                "dimension_scores_json": json.dumps(
                    [
                        {
                            "dimension": "课堂学习投入",
                            "dimension_code": "class_engagement",
                            "score": 0.28,
                            "level": "low",
                        }
                    ],
                    ensure_ascii=False,
                ),
            },
            {
                "student_id": "20230002",
                "term_key": "2024-2",
                "student_name": "Alice",
                "major_name": "软件工程",
                "group_segment": "课堂参与薄弱组",
                "risk_probability": 0.83,
                "risk_level": "一般风险",
                "dimension_scores_json": json.dumps(
                    [
                        {
                            "dimension": "课堂学习投入",
                            "dimension_code": "class_engagement",
                            "score": 0.28,
                            "level": "low",
                            "label": "课堂投入薄弱",
                            "metrics": [
                                {
                                    "name": "attendance_rate",
                                    "value": 0.64,
                                    "display": "64%",
                                }
                            ],
                            "explanation": "课堂到课率偏低，当前已进入关注区间。",
                        }
                    ],
                    ensure_ascii=False,
                ),
            },
        ]
    ).to_csv(warnings_path, index=False, encoding="utf-8-sig")

    store = DemoApiStore(
        overview_path=overview_path,
        model_summary_path=sample_artifacts_dir / "v1_model_summary.json",
        overview_term="2024-2",
        warnings_path=warnings_path,
        repo_root=tmp_path,
    )

    payload = store.get_overview("2024-2")

    assert payload["dimension_summary"] == [
        {
            "dimension": "课堂学习投入",
            "dimension_code": "class_engagement",
            "average_score": 0.28,
            "score_count": 2,
            "level": "low",
            "label": "课堂投入薄弱",
            "metrics": [{"name": "attendance_rate", "value": 0.64, "display": "64%"}],
            "explanation": "课堂到课率偏低，当前已进入关注区间。",
        }
    ]


def test_get_overview_replaces_empty_metric_placeholders_with_real_metrics(
    tmp_path: Path, sample_artifacts_dir: Path
) -> None:
    overview_path = tmp_path / "artifacts" / "model_stubs" / "v1_overview_by_term.json"
    overview_path.parent.mkdir(parents=True, exist_ok=True)
    overview_payload = json.loads(
        (sample_artifacts_dir / "v1_overview_by_term.json").read_text(encoding="utf-8")
    )
    overview_payload["dimension_summary"] = [
        {
            "dimension": "课堂学习投入",
            "dimension_code": "class_engagement",
            "average_score": 0.5,
        }
    ]
    overview_path.write_text(json.dumps(overview_payload, ensure_ascii=False), encoding="utf-8")

    warnings_path = tmp_path / "artifacts" / "model_stubs" / "v1_student_results.csv"
    pd.DataFrame(
        [
            {
                "student_id": "20230001",
                "term_key": "2024-2",
                "student_name": "Bob",
                "major_name": "软件工程",
                "group_segment": "课堂参与薄弱组",
                "risk_probability": 0.81,
                "risk_level": "一般风险",
                "dimension_scores_json": json.dumps(
                    [
                        {
                            "dimension": "课堂学习投入",
                            "dimension_code": "class_engagement",
                            "score": 0.0,
                            "level": "low",
                            "label": "课堂投入薄弱",
                            "metrics": [],
                            "explanation": "课堂学习投入处于课堂投入薄弱，主要依据是当前可用指标有限。",
                        }
                    ],
                    ensure_ascii=False,
                ),
            },
            {
                "student_id": "20230002",
                "term_key": "2024-2",
                "student_name": "Alice",
                "major_name": "软件工程",
                "group_segment": "课堂参与薄弱组",
                "risk_probability": 0.83,
                "risk_level": "一般风险",
                "dimension_scores_json": json.dumps(
                    [
                        {
                            "dimension": "课堂学习投入",
                            "dimension_code": "class_engagement",
                            "score": 1.0,
                            "level": "high",
                            "label": "课堂投入积极",
                            "metrics": [
                                {
                                    "metric": "attendance_rate",
                                    "label": "出勤率",
                                    "value": 1.0,
                                }
                            ],
                            "explanation": "课堂学习投入处于课堂投入积极，主要依据是出勤率 1.0。",
                        }
                    ],
                    ensure_ascii=False,
                ),
            },
        ]
    ).to_csv(warnings_path, index=False, encoding="utf-8-sig")

    store = DemoApiStore(
        overview_path=overview_path,
        model_summary_path=sample_artifacts_dir / "v1_model_summary.json",
        overview_term="2024-2",
        warnings_path=warnings_path,
        repo_root=tmp_path,
    )

    payload = store.get_overview("2024-2")

    assert payload["dimension_summary"] == [
        {
            "dimension": "课堂学习投入",
            "dimension_code": "class_engagement",
            "average_score": 0.5,
            "score_count": 2,
            "level": "low",
            "label": "课堂投入薄弱",
            "metrics": [{"metric": "attendance_rate", "label": "出勤率", "value": 1.0}],
            "explanation": "课堂学习投入处于课堂投入薄弱，主要依据是当前可用指标有限。",
        }
    ]


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
            "elevated_risk_count": 1,
            "elevated_risk_ratio": 1.0,
            "average_risk_probability": 0.91,
        },
        {
            "major_name": "软件工程",
            "student_count": 2,
            "high_risk_count": 0,
            "elevated_risk_count": 0,
            "elevated_risk_ratio": 0.0,
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


def test_get_student_profile_includes_risk_explanations(sample_store) -> None:
    payload = sample_store.get_student_profile(student_id="20230001", term="2023-1")

    assert payload["base_risk_explanation"] == "base explanation"
    assert payload["behavior_adjustment_explanation"] == "adjustment explanation"
    assert payload["risk_change_explanation"] == "change explanation"


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


def test_list_warnings_normalizes_risk_level_filter(
    tmp_path: Path, sample_artifacts_dir: Path
) -> None:
    warnings_path = tmp_path / "artifacts" / "model_stubs" / "v1_student_results.csv"
    warnings_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        [
            {
                "student_id": "20230001",
                "term_key": "2024-2",
                "student_name": "Bob",
                "major_name": "软件工程",
                "group_segment": "课堂参与薄弱组",
                "risk_probability": 0.92,
                "risk_level": "高风险",
                "dimension_scores_json": json.dumps([], ensure_ascii=False),
            },
            {
                "student_id": "20230002",
                "term_key": "2024-2",
                "student_name": "Alice",
                "major_name": "软件工程",
                "group_segment": "课堂参与薄弱组",
                "risk_probability": 0.48,
                "risk_level": "较高风险",
                "dimension_scores_json": json.dumps([], ensure_ascii=False),
            },
            {
                "student_id": "20230003",
                "term_key": "2024-2",
                "student_name": "Carol",
                "major_name": "软件工程",
                "group_segment": "课堂参与薄弱组",
                "risk_probability": 0.32,
                "risk_level": "一般风险",
                "dimension_scores_json": json.dumps([], ensure_ascii=False),
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

    payload = store.list_warnings(term="2024-2", risk_level="high")

    assert payload["total"] == 2
    assert [item["student_id"] for item in payload["items"]] == ["20230001", "20230002"]

    localized_payload = store.list_warnings(term="2024-2", risk_level="较高风险")

    assert localized_payload["total"] == 1
    assert localized_payload["items"][0]["student_id"] == "20230002"


def test_list_warnings_exposes_risk_fields_and_filters_by_change_direction(
    tmp_path: Path, sample_artifacts_dir: Path
) -> None:
    warnings_path = tmp_path / "artifacts" / "model_stubs" / "v1_student_results.csv"
    warnings_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        [
            {
                "student_id": "20230001",
                "term_key": "2024-2",
                "student_name": "Bob",
                "major_name": "软件工程",
                "group_segment": "课堂参与薄弱组",
                "risk_probability": 0.52,
                "base_risk_score": 52.0,
                "risk_adjustment_score": 5.0,
                "adjusted_risk_score": 57.0,
                "risk_level": "较高风险",
                "risk_delta": 5.0,
                "risk_change_direction": "rising",
                "dimension_scores_json": json.dumps([], ensure_ascii=False),
                "top_risk_factors_json": json.dumps(
                    [{"feature": "academic_base", "feature_cn": "学业基础表现", "importance": 0.9}],
                    ensure_ascii=False,
                ),
                "top_protective_factors_json": json.dumps(
                    [{"feature": "class_engagement", "feature_cn": "课堂学习投入", "importance": 0.2}],
                    ensure_ascii=False,
                ),
                "base_risk_explanation": "base",
                "behavior_adjustment_explanation": "adjust",
                "risk_change_explanation": "change",
            },
            {
                "student_id": "20230002",
                "term_key": "2024-2",
                "student_name": "Alice",
                "major_name": "软件工程",
                "group_segment": "课堂参与薄弱组",
                "risk_probability": 0.48,
                "base_risk_score": 48.0,
                "risk_adjustment_score": -3.0,
                "adjusted_risk_score": 45.0,
                "risk_level": "一般风险",
                "risk_delta": -2.0,
                "risk_change_direction": "falling",
                "dimension_scores_json": json.dumps([], ensure_ascii=False),
                "top_risk_factors_json": json.dumps([], ensure_ascii=False),
                "top_protective_factors_json": json.dumps([], ensure_ascii=False),
                "base_risk_explanation": "base",
                "behavior_adjustment_explanation": "adjust",
                "risk_change_explanation": "change",
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

    payload = store.list_warnings(term="2024-2", risk_change_direction="rising")

    assert payload["total"] == 1
    item = payload["items"][0]
    assert item["base_risk_score"] == 52.0
    assert item["risk_change_direction"] == "rising"
    assert item["top_risk_factors"][0]["feature"] == "academic_base"
    assert item["top_protective_factors"][0]["feature"] == "class_engagement"


def test_list_warnings_raises_for_unknown_term(sample_store) -> None:
    with pytest.raises(KeyError, match="2099-1"):
        sample_store.list_warnings(term="2099-1")


def test_list_warnings_raises_for_missing_term_key(
    tmp_path: Path, sample_artifacts_dir: Path
) -> None:
    warnings_path = tmp_path / "artifacts" / "model_stubs" / "v1_student_results.csv"
    warnings_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        [
            {
                "student_id": "20230001",
                "student_name": "Bob",
                "major_name": "软件工程",
                "group_segment": "综合发展优势组",
                "risk_probability": 0.55,
                "risk_level": "low",
                "dimension_scores_json": json.dumps([], ensure_ascii=False),
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

    with pytest.raises(ValueError, match="warnings rows must include term_key"):
        store.list_warnings(term="2023-1")


def test_list_warnings_raises_for_missing_group_segment(
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
                "risk_probability": 0.55,
                "risk_level": "low",
                "dimension_scores_json": json.dumps([], ensure_ascii=False),
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

    with pytest.raises(ValueError, match="warnings rows must include group_segment"):
        store.list_warnings(term="2023-1")


def test_get_groups_accepts_blank_dimension_scores_json(
    tmp_path: Path, sample_artifacts_dir: Path
) -> None:
    warnings_path = tmp_path / "artifacts" / "model_stubs" / "v1_student_results.csv"
    warnings_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        [
            {
                "student_id": "20230009",
                "term_key": "2023-1",
                "student_name": "Ian",
                "major_name": "软件工程",
                "group_segment": "综合发展优势组",
                "risk_probability": 0.66,
                "risk_level": "medium",
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

    payload = store.get_groups(term="2023-1")

    assert payload["groups"][0]["avg_dimension_scores"] == []


def test_get_groups_raises_for_missing_dimension_scores_json(
    tmp_path: Path, sample_artifacts_dir: Path
) -> None:
    warnings_path = tmp_path / "artifacts" / "model_stubs" / "v1_student_results.csv"
    warnings_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        [
            {
                "student_id": "20230010",
                "term_key": "2023-1",
                "student_name": "Jade",
                "major_name": "软件工程",
                "group_segment": "综合发展优势组",
                "risk_probability": 0.66,
                "risk_level": "medium",
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

    with pytest.raises(ValueError, match="warnings rows must include dimension_scores_json"):
        store.get_groups(term="2023-1")


@pytest.mark.parametrize("risk_probability", ["nan", "inf", "-inf"])
def test_list_warnings_rejects_non_finite_risk_probability(
    risk_probability: str, tmp_path: Path, sample_artifacts_dir: Path
) -> None:
    warnings_path = tmp_path / "artifacts" / "model_stubs" / "v1_student_results.csv"
    warnings_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        [
            {
                "student_id": "20230011",
                "term_key": "2023-1",
                "student_name": "Kai",
                "major_name": "软件工程",
                "group_segment": "综合发展优势组",
                "risk_probability": risk_probability,
                "risk_level": "low",
                "dimension_scores_json": json.dumps([], ensure_ascii=False),
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

    with pytest.raises(ValueError, match="warnings rows must include finite risk_probability"):
        store.list_warnings(term="2023-1")


def test_get_student_report_includes_risk_trend_metadata(
    tmp_path: Path, sample_artifacts_dir: Path
) -> None:
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
                "base_risk_score": 55.0,
                "risk_adjustment_score": -1.0,
                "adjusted_risk_score": 54.0,
                "risk_level": "low",
                "risk_delta": 0.0,
                "risk_change_direction": "steady",
                "dimension_scores_json": json.dumps([], ensure_ascii=False),
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
                "dimension_scores_json": json.dumps([], ensure_ascii=False),
            },
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

    payload = store.get_student_report(student_id="20230001", term="2023-1")

    assert payload["risk_level"] == "medium"
    assert payload["risk_delta"] == -1.0
    assert payload["risk_change_direction"] == "falling"
    assert [item["term"] for item in payload["trend"]] == ["2022-2", "2023-1"]


def test_get_overview_counts_localized_high_risk_levels(
    tmp_path: Path, sample_artifacts_dir: Path
) -> None:
    overview_path = tmp_path / "artifacts" / "model_stubs" / "v1_overview_by_term.json"
    overview_path.parent.mkdir(parents=True, exist_ok=True)
    overview_path.write_text(
        json.dumps(
            {
                "student_count": 1,
                "risk_distribution": {"high": 1, "medium": 0, "low": 0},
                "group_distribution": {"课堂参与薄弱组": 1},
                "major_risk_summary": [],
                "trend_summary": {"terms": [{"term_key": "2024-2"}]},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    warnings_path = tmp_path / "artifacts" / "model_stubs" / "v1_student_results.csv"
    warnings_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        [
            {
                "student_id": "20230001",
                "term_key": "2024-2",
                "student_name": "Bob",
                "major_name": "软件工程",
                "group_segment": "课堂参与薄弱组",
                "risk_probability": 0.91,
                "risk_level": "高风险",
                "dimension_scores_json": json.dumps([], ensure_ascii=False),
            }
        ]
    ).to_csv(warnings_path, index=False, encoding="utf-8-sig")
    reports_path = tmp_path / "artifacts" / "model_stubs" / "v1_student_reports.jsonl"
    reports_path.write_text("", encoding="utf-8")
    store = DemoApiStore(
        overview_path=overview_path,
        model_summary_path=sample_artifacts_dir / "v1_model_summary.json",
        overview_term="2024-1",
        warnings_path=warnings_path,
        repo_root=tmp_path,
    )

    payload = store.get_overview("2024-2")

    assert payload["major_risk_summary"][0]["high_risk_count"] == 1


def test_get_overview_normalizes_localized_risk_distribution(
    tmp_path: Path, sample_artifacts_dir: Path
) -> None:
    overview_path = tmp_path / "artifacts" / "model_stubs" / "v1_overview_by_term.json"
    overview_path.parent.mkdir(parents=True, exist_ok=True)
    overview_path.write_text(
        json.dumps(
            {
                "student_count": 4,
                "risk_distribution": {"high": 0, "medium": 0, "low": 0},
                "group_distribution": {"课堂参与薄弱组": 4},
                "major_risk_summary": [],
                "trend_summary": {"terms": [{"term_key": "2024-2"}]},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    warnings_path = tmp_path / "artifacts" / "model_stubs" / "v1_student_results.csv"
    warnings_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        [
            {
                "student_id": "20230001",
                "term_key": "2024-2",
                "student_name": "Bob",
                "major_name": "软件工程",
                "group_segment": "课堂参与薄弱组",
                "risk_probability": 0.91,
                "risk_level": "高风险",
                "dimension_scores_json": json.dumps([], ensure_ascii=False),
            },
            {
                "student_id": "20230002",
                "term_key": "2024-2",
                "student_name": "Alice",
                "major_name": "软件工程",
                "group_segment": "课堂参与薄弱组",
                "risk_probability": 0.88,
                "risk_level": "较高风险",
                "dimension_scores_json": json.dumps([], ensure_ascii=False),
            },
            {
                "student_id": "20230003",
                "term_key": "2024-2",
                "student_name": "Carol",
                "major_name": "软件工程",
                "group_segment": "课堂参与薄弱组",
                "risk_probability": 0.55,
                "risk_level": "一般风险",
                "dimension_scores_json": json.dumps([], ensure_ascii=False),
            },
            {
                "student_id": "20230004",
                "term_key": "2024-2",
                "student_name": "Dora",
                "major_name": "软件工程",
                "group_segment": "课堂参与薄弱组",
                "risk_probability": 0.2,
                "risk_level": "低风险",
                "dimension_scores_json": json.dumps([], ensure_ascii=False),
            },
        ]
    ).to_csv(warnings_path, index=False, encoding="utf-8-sig")
    reports_path = tmp_path / "artifacts" / "model_stubs" / "v1_student_reports.jsonl"
    reports_path.write_text("", encoding="utf-8")
    store = DemoApiStore(
        overview_path=overview_path,
        model_summary_path=sample_artifacts_dir / "v1_model_summary.json",
        overview_term="2024-1",
        warnings_path=warnings_path,
        repo_root=tmp_path,
    )

    payload = store.get_overview("2024-2")

    assert payload["risk_distribution"] == {"high": 2, "medium": 1, "low": 1}


def test_get_groups_avg_risk_level_scales_probability(
    tmp_path: Path, sample_artifacts_dir: Path
) -> None:
    warnings_path = tmp_path / "artifacts" / "model_stubs" / "v1_student_results.csv"
    warnings_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        [
            {
                "student_id": "20230001",
                "term_key": "2024-2",
                "student_name": "Bob",
                "major_name": "软件工程",
                "group_segment": "课堂参与薄弱组",
                "risk_probability": 0.82,
                "risk_level": "medium",
                "dimension_scores_json": json.dumps([], ensure_ascii=False),
            },
            {
                "student_id": "20230002",
                "term_key": "2024-2",
                "student_name": "Alice",
                "major_name": "软件工程",
                "group_segment": "课堂参与薄弱组",
                "risk_probability": 0.7,
                "risk_level": "medium",
                "dimension_scores_json": json.dumps([], ensure_ascii=False),
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

    payload = store.get_groups(term="2024-2")

    assert payload["groups"][0]["avg_risk_level"] == "较高风险"


def test_missing_default_artifact_resolution_only_uses_current_worktree(tmp_path: Path) -> None:
    current_artifact_root = tmp_path / "artifacts" / "model_stubs"
    sibling_artifact_root = tmp_path.parent / "v1-model-stubs" / "artifacts" / "model_stubs"
    sibling_artifact_root.mkdir(parents=True)
    (sibling_artifact_root / "v1_overview_by_term.json").write_text("{}", encoding="utf-8")
    (sibling_artifact_root / "v1_model_summary.json").write_text("{}", encoding="utf-8")

    with pytest.raises(FileNotFoundError):
        DemoApiStore(repo_root=tmp_path)
