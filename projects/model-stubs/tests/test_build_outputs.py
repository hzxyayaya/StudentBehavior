from datetime import datetime
import json

import pandas as pd
import pytest

from student_behavior_model_stubs.build_outputs import _coerce_dimension_scores
from student_behavior_model_stubs.build_outputs import build_model_summary
from student_behavior_model_stubs.build_outputs import build_overview_by_term
from student_behavior_model_stubs.build_outputs import build_student_reports
from student_behavior_model_stubs.build_outputs import build_student_results


def _feature_row() -> dict[str, object]:
    return {
        "student_id": "20230002",
        "term_key": "2024-1",
        "major_name": "软件工程",
        "term_gpa": 1.8,
        "academic_base_score_raw": 58.0,
        "class_engagement_score_raw": 40.0,
        "online_activeness_score_raw": 35.0,
        "library_immersion_score_raw": 28.0,
        "network_habits_score_raw": 22.0,
        "daily_routine_boundary_score_raw": 26.0,
        "physical_resilience_score_raw": 72.0,
        "appraisal_status_alert_score_raw": 64.0,
        "failed_course_count": 2,
        "borderline_course_count": 1,
        "failed_course_ratio": 0.2,
        "previous_adjusted_risk_score": 54.0,
    }


def test_build_student_results_outputs_risk_warning_contract() -> None:
    results = build_student_results(pd.DataFrame([_feature_row()]))
    dimension_scores = json.loads(results.loc[0, "dimension_scores_json"])

    assert {
        "student_id",
        "term_key",
        "student_name",
        "major_name",
        "group_segment",
        "risk_probability",
        "base_risk_score",
        "risk_adjustment_score",
        "adjusted_risk_score",
        "risk_level",
        "risk_delta",
        "risk_change_direction",
        "dimension_scores_json",
        "top_risk_factors",
        "top_risk_factors_json",
        "top_protective_factors",
        "top_protective_factors_json",
        "base_risk_explanation",
        "behavior_adjustment_explanation",
        "risk_change_explanation",
    }.issubset(results.columns)
    record = results.iloc[0].to_dict()
    assert record["student_id"] == "20230002"
    assert record["term_key"] == "2024-1"
    assert record["student_name"] == "20230002"
    assert record["major_name"] == "软件工程"
    assert record["group_segment"] == results.loc[0, "group_segment"]
    assert record["risk_probability"] == 0.63
    assert record["base_risk_score"] == results.loc[0, "base_risk_score"]
    assert record["risk_adjustment_score"] == results.loc[0, "risk_adjustment_score"]
    assert record["adjusted_risk_score"] == results.loc[0, "adjusted_risk_score"]
    assert record["risk_level"] == "一般风险"
    assert record["risk_delta"] == results.loc[0, "risk_delta"]
    assert record["risk_change_direction"] == "rising"
    assert record["dimension_scores_json"] == results.loc[0, "dimension_scores_json"]
    top_risk_factors = json.loads(record["top_risk_factors_json"])
    top_protective_factors = json.loads(record["top_protective_factors_json"])
    assert record["top_risk_factors_json"] == results.loc[0, "top_risk_factors_json"]
    assert record["top_protective_factors_json"] == results.loc[0, "top_protective_factors_json"]
    assert record["top_risk_factors"]
    assert record["top_protective_factors"]
    assert record["top_risk_factors"] == "、".join(
        str(item["feature_cn"]) for item in top_risk_factors if str(item.get("feature_cn", "")).strip()
    )
    assert record["top_protective_factors"] == "、".join(
        str(item["feature_cn"])
        for item in top_protective_factors
        if str(item.get("feature_cn", "")).strip()
    )
    assert record["base_risk_explanation"] == results.loc[0, "base_risk_explanation"]
    assert record["behavior_adjustment_explanation"] == results.loc[0, "behavior_adjustment_explanation"]
    assert record["risk_change_explanation"] == results.loc[0, "risk_change_explanation"]
    assert len(dimension_scores) == 8
    assert set(dimension_scores[0]) == {
        "dimension",
        "dimension_code",
        "score",
        "level",
        "label",
        "metrics",
        "explanation",
        "provenance",
    }
    assert dimension_scores[0]["dimension"] == "学业基础表现"
    assert dimension_scores[0]["dimension_code"] == "academic_base"
    assert isinstance(dimension_scores[0]["label"], str)
    assert dimension_scores[0]["label"] not in {"high", "medium", "low"}
    assert dimension_scores[0]["metrics"]
    assert "学期GPA" in dimension_scores[0]["explanation"]
    assert dimension_scores[0]["provenance"]["threshold_strategies"] == ["fixed"]


def test_build_student_reports_outputs_jsonl_ready_records() -> None:
    results = build_student_results(pd.DataFrame([_feature_row()]))
    reports = build_student_reports(results)

    assert reports[0]["student_id"] == "20230002"
    assert reports[0]["term_key"] == "2024-1"
    assert reports[0]["version"] == "v1_calibrated_report"
    assert len(reports[0]["top_risk_factors"]) == 3
    assert len(reports[0]["top_protective_factors"]) == 3
    assert all(
        isinstance(factor["dimension_code"], str) and factor["dimension_code"]
        for factor in reports[0]["top_risk_factors"]
    )
    assert all(
        {"feature", "feature_cn", "effect", "importance", "dimension_code", "label", "explanation", "provenance"}
        <= set(factor)
        for factor in reports[0]["top_risk_factors"]
    )
    assert len(reports[0]["priority_interventions"]) == 3
    assert reports[0]["intervention_priority"] == 3
    assert "基础风险" in reports[0]["base_risk_explanation"]
    assert "行为调整" in reports[0]["behavior_adjustment_explanation"]
    assert "风险变化" in reports[0]["risk_change_explanation"]
    assert "一般风险" in reports[0]["intervention_plan"]
    first_factor = reports[0]["top_risk_factors"][0]["feature_cn"]
    first_dimension = next(
        item for item in _coerce_dimension_scores(results.loc[0, "dimension_scores_json"]) if item["dimension"] == first_factor
    )
    assert reports[0]["top_risk_factors"][0]["dimension_code"] == first_dimension["dimension_code"]
    assert reports[0]["top_risk_factors"][0]["label"] == first_dimension["label"]
    assert reports[0]["top_risk_factors"][0]["provenance"] == first_dimension["provenance"]
    assert "指标：" in reports[0]["report_text"]
    assert "当前维度得分 " in reports[0]["report_text"]
    if first_dimension["provenance"]["has_caveated_metrics"] or first_dimension["provenance"]["has_deferred_metrics"]:
        assert "证据提示：当前维度包含 caveated/deferred 证据" in reports[0]["report_text"]


def test_build_overview_top_warning_factors_are_ranked_by_weakness() -> None:
    student_results = build_student_results(
        pd.DataFrame(
            [
                _feature_row() | {"student_id": "20230001", "term_key": "2024-1"},
                _feature_row()
                | {
                    "student_id": "20230002",
                    "term_key": "2024-1",
                    "academic_base_score_raw": 84.0,
                    "class_engagement_score_raw": 78.0,
                    "online_activeness_score_raw": 72.0,
                    "network_habits_score_raw": 70.0,
                    "daily_routine_boundary_score_raw": 76.0,
                    "failed_course_count": 0,
                },
                _feature_row()
                | {
                    "student_id": "20230003",
                    "term_key": "2024-2",
                    "major_name": "数据科学",
                    "academic_base_score_raw": 22.0,
                    "class_engagement_score_raw": 20.0,
                    "online_activeness_score_raw": 18.0,
                    "network_habits_score_raw": 15.0,
                    "daily_routine_boundary_score_raw": 17.0,
                    "failed_course_count": 4,
                },
            ]
        )
    )

    overview = build_overview_by_term(student_results)
    expected_order = [
        item["dimension_code"]
        for item in sorted(
            overview["dimension_summary"],
            key=lambda item: (item["average_score"], item["dimension_code"]),
        )[:3]
    ]

    assert [factor["dimension_code"] for factor in overview["top_warning_factors"]] == expected_order


def test_build_student_reports_protective_factors_are_not_negative_effects() -> None:
    reports = build_student_reports(build_student_results(pd.DataFrame([_feature_row()])))

    assert all(factor["effect"] != "negative" for factor in reports[0]["top_protective_factors"])


def test_missing_student_name_falls_back_to_student_id_placeholder() -> None:
    results = build_student_results(
        pd.DataFrame([_feature_row() | {"student_id": "20230003", "student_name": ""}])
    )
    assert results.loc[0, "student_name"] == "20230003"


def test_build_student_results_sorts_by_student_id_and_term_key() -> None:
    features = pd.DataFrame(
        [
            _feature_row() | {"student_id": "20230010", "term_key": "2024-2"},
            _feature_row() | {"student_id": "20230002", "term_key": "2024-2"},
            _feature_row() | {"student_id": "20230002", "term_key": "2024-1"},
        ]
    )

    results = build_student_results(features)
    assert list(results["student_id"]) == ["20230002", "20230002", "20230010"]
    assert list(results["term_key"]) == ["2024-1", "2024-2", "2024-2"]


def test_build_student_reports_sorts_by_student_id_and_term_key() -> None:
    student_results = build_student_results(
        pd.DataFrame(
            [
                _feature_row() | {"student_id": "20230010", "term_key": "2024-2"},
                _feature_row() | {"student_id": "20230002", "term_key": "2024-1"},
            ]
        )
    )

    reports = build_student_reports(student_results)
    assert [record["student_id"] for record in reports] == ["20230002", "20230010"]
    assert [record["term_key"] for record in reports] == ["2024-1", "2024-2"]


def test_build_overview_by_term_includes_required_sections() -> None:
    student_results = build_student_results(
        pd.DataFrame(
            [
                _feature_row() | {"student_id": "20230001", "term_key": "2024-1"},
                _feature_row()
                | {
                    "student_id": "20230002",
                    "term_key": "2024-1",
                    "academic_base_score_raw": 84.0,
                    "class_engagement_score_raw": 78.0,
                    "online_activeness_score_raw": 72.0,
                    "network_habits_score_raw": 70.0,
                    "daily_routine_boundary_score_raw": 76.0,
                    "failed_course_count": 0,
                },
                _feature_row()
                | {
                    "student_id": "20230003",
                    "term_key": "2024-2",
                    "major_name": "数据科学",
                    "academic_base_score_raw": 22.0,
                    "class_engagement_score_raw": 20.0,
                    "online_activeness_score_raw": 18.0,
                    "network_habits_score_raw": 15.0,
                    "daily_routine_boundary_score_raw": 17.0,
                    "failed_course_count": 4,
                },
            ]
        )
    )
    student_results.loc[:, "risk_level"] = ["高风险", "较高风险", "低风险"]

    overview = build_overview_by_term(student_results)
    expected_dimension_summary = sorted(
        [
            {
                "dimension": item["dimension"],
                "dimension_code": item["dimension_code"],
                "average_score": round(
                    sum(
                        next(
                            score["score"]
                            for score in _coerce_dimension_scores(value)
                            if score["dimension_code"] == item["dimension_code"]
                        )
                        for value in student_results["dimension_scores_json"]
                    )
                    / len(student_results),
                    2,
                ),
            }
            for item in _coerce_dimension_scores(student_results.iloc[0]["dimension_scores_json"])
        ],
        key=lambda item: item["dimension_code"],
    )
    assert {
        "student_count",
        "risk_band_distribution",
        "group_distribution",
        "major_risk_summary",
        "risk_trend_summary",
        "dimension_summary",
        "group_score_summary",
        "top_warning_factors",
        "intervention_priority_summary",
    }.issubset(overview)
    assert isinstance(overview["risk_trend_summary"], dict)
    assert set(overview["risk_band_distribution"]) == {"高风险", "较高风险", "一般风险", "低风险"}
    assert overview["dimension_summary"] == expected_dimension_summary
    assert len(overview["top_warning_factors"]) == 3
    assert len(overview["intervention_priority_summary"]) == 4
    assert overview["risk_trend_summary"] == overview["trend_summary"]
    assert overview["risk_band_distribution"] == overview["risk_distribution"]
    assert next(
        item for item in overview["major_risk_summary"] if item["major_name"] == "软件工程"
    )["high_risk_count"] == 1
    for group_segment, entries in overview["group_score_summary"].items():
        assert group_segment in overview["group_distribution"]
        assert [entry["dimension_code"] for entry in entries] == [
            item["dimension_code"] for item in expected_dimension_summary
        ]


def test_build_model_summary_uses_fixed_now_for_updated_at_and_stub_fields() -> None:
    fixed_now = datetime(2024, 1, 2, 3, 4, 5)
    summary = build_model_summary(now=fixed_now)

    assert summary == {
        "cluster_method": "stub-eight-dimension-group-rules",
        "risk_model": "stub-eight-dimension-risk-rules",
        "target_label": "学期级八维学业风险",
        "auc": 0.8347,
        "updated_at": "2024-01-02T03:04:05",
    }


def test_build_model_summary_updated_at_is_not_placeholder_text() -> None:
    summary = build_model_summary(now=datetime(2024, 1, 2, 3, 4, 5))
    assert summary["updated_at"] not in {"", "TBD", "PLACEHOLDER", "updated_at"}


def test_build_model_summary_rejects_placeholder_like_now() -> None:
    with pytest.raises(TypeError, match="now must be a datetime"):
        build_model_summary(now="PLACEHOLDER")
