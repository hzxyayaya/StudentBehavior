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
        "academic_base_score_raw": 58.0,
        "class_engagement_score_raw": 40.0,
        "online_activeness_score_raw": 35.0,
        "library_immersion_score_raw": 28.0,
        "network_habits_score_raw": 22.0,
        "daily_routine_boundary_score_raw": 26.0,
        "physical_resilience_score_raw": 72.0,
        "appraisal_status_alert_score_raw": 64.0,
        "failed_course_count": 2,
    }


def test_build_student_results_outputs_contract_aligned_columns() -> None:
    results = build_student_results(pd.DataFrame([_feature_row()]))
    dimension_scores = json.loads(results.loc[0, "dimension_scores_json"])

    assert list(results.columns) == [
        "student_id",
        "term_key",
        "student_name",
        "major_name",
        "group_segment",
        "risk_probability",
        "risk_level",
        "dimension_scores_json",
    ]
    assert results.to_dict(orient="records") == [
        {
            "student_id": "20230002",
            "term_key": "2024-1",
            "student_name": "20230002",
            "major_name": "软件工程",
            "group_segment": results.loc[0, "group_segment"],
            "risk_probability": 0.63,
            "risk_level": "medium",
            "dimension_scores_json": results.loc[0, "dimension_scores_json"],
        }
    ]
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
    assert len(reports[0]["top_factors"]) == 3
    assert all(isinstance(factor["dimension_code"], str) and factor["dimension_code"] for factor in reports[0]["top_factors"])
    assert all(
        {"feature", "feature_cn", "effect", "importance", "dimension_code", "label", "explanation", "provenance"}
        <= set(factor)
        for factor in reports[0]["top_factors"]
    )
    assert len(reports[0]["intervention_advice"]) == 3
    assert len(reports[0]["intervention_advice_items"]) == 3
    assert [item["priority"] for item in reports[0]["intervention_advice_items"]] == [1, 2, 3]
    assert [item["text"] for item in reports[0]["intervention_advice_items"]] == reports[0]["intervention_advice"]
    assert all({"key", "priority", "text"} <= set(item) for item in reports[0]["intervention_advice_items"])
    first_factor = reports[0]["top_factors"][0]["feature_cn"]
    first_dimension = next(
        item for item in _coerce_dimension_scores(results.loc[0, "dimension_scores_json"]) if item["dimension"] == first_factor
    )
    assert reports[0]["top_factors"][0]["dimension_code"] == first_dimension["dimension_code"]
    assert reports[0]["top_factors"][0]["label"] == first_dimension["label"]
    assert reports[0]["top_factors"][0]["provenance"] == first_dimension["provenance"]
    assert "指标：" in reports[0]["report_text"]
    assert "当前维度得分 " in reports[0]["report_text"]
    if first_dimension["provenance"]["has_caveated_metrics"] or first_dimension["provenance"]["has_deferred_metrics"]:
        assert "证据提示：当前维度包含 caveated/deferred 证据" in reports[0]["report_text"]


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
        "risk_distribution",
        "group_distribution",
        "major_risk_summary",
        "trend_summary",
        "dimension_summary",
        "group_score_summary",
    }.issubset(overview)
    assert isinstance(overview["trend_summary"], dict)
    assert overview["dimension_summary"] == expected_dimension_summary
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
