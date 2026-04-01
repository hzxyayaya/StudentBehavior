import math
import re

import pytest

import student_behavior_model_stubs.scoring as scoring_module
from student_behavior_model_stubs.scoring import build_dimension_scores
from student_behavior_model_stubs.scoring import build_risk_calibration
from student_behavior_model_stubs.scoring import compute_group_segment
from student_behavior_model_stubs.scoring import compute_adjusted_risk_score
from student_behavior_model_stubs.scoring import compute_base_risk_score
from student_behavior_model_stubs.scoring import compute_risk_adjustment_score
from student_behavior_model_stubs.scoring import compute_risk_change_direction
from student_behavior_model_stubs.scoring import compute_risk_delta
from student_behavior_model_stubs.scoring import compute_risk_probability
from student_behavior_model_stubs.scoring import map_risk_level
from student_behavior_model_stubs.scoring import map_adjusted_risk_level


def _base_row() -> dict[str, object]:
    return {
        "student_id": "20230001",
        "term_key": "2024-1",
        "academic_base_score_raw": 82.0,
        "class_engagement_score_raw": 76.0,
        "online_activeness_score_raw": 71.0,
        "library_immersion_score_raw": 68.0,
        "network_habits_score_raw": 52.0,
        "daily_routine_boundary_score_raw": 65.0,
        "physical_resilience_score_raw": 88.0,
        "appraisal_status_alert_score_raw": 91.0,
        "failed_course_count": 1,
        "term_gpa": 3.6,
        "borderline_course_count": 2,
        "failed_course_ratio": 0.08,
        "attendance_rate": 0.93,
        "late_count": 1,
        "truancy_count": 0,
        "absence_count": 0,
        "video_completion_rate": 0.84,
        "online_test_avg_score": 81.0,
        "online_work_avg_score": 83.0,
        "online_exam_avg_score": 79.0,
        "platform_engagement_score": 72.0,
        "forum_interaction_total": 18,
        "library_completed_visit_count": 24,
        "avg_library_stay_minutes": 96.0,
        "weekly_library_visit_avg": 3.2,
        "monthly_online_duration_avg": 42.0,
        "term_online_duration_sum": 168.0,
        "online_duration_vs_school_avg_gap": 6.0,
        "first_daily_access_time_avg": 7.8,
        "first_daily_access_time_std": 0.9,
        "late_return_count": 2,
        "late_return_ratio": 0.11,
        "daily_access_time_variability": 1.3,
        "physical_test_avg_score": 86.0,
        "physical_test_pass_flag": 1,
        "weekly_running_count_avg": 2.7,
        "weekly_exercise_count_avg": 3.5,
        "scholarship_amount_sum": 3000.0,
        "scholarship_level_score": 2,
        "negative_status_alert_flag": 0,
        "status_change_count": 0,
    }


def _metric_map(item: dict[str, object]) -> dict[str, object]:
    return {metric["label"]: metric["value"] for metric in item["metrics"]}


def test_compute_risk_probability_is_deterministic() -> None:
    row = _base_row() | {
        "academic_base_score_raw": 40.0,
        "class_engagement_score_raw": 35.0,
        "online_activeness_score_raw": 42.0,
        "daily_routine_boundary_score_raw": 38.0,
        "failed_course_count": 2,
    }
    assert compute_risk_probability(row) == 0.64
    assert compute_risk_probability(row) == compute_risk_probability(row)


def test_map_risk_level_respects_frozen_thresholds() -> None:
    assert map_risk_level(0.80) == "high"
    assert map_risk_level(0.50) == "medium"
    assert map_risk_level(0.30) == "low"


def test_compute_risk_probability_is_clamped_and_rounded() -> None:
    row = _base_row() | {
        "academic_base_score_raw": 0.0,
        "class_engagement_score_raw": 0.0,
        "online_activeness_score_raw": 0.0,
        "daily_routine_boundary_score_raw": 0.0,
        "failed_course_count": 10,
    }
    probability = compute_risk_probability(row)
    assert 0.05 <= probability <= 0.95
    assert probability == round(probability, 2)
    assert probability == 0.95


def test_compute_risk_probability_handles_null_metrics_without_crash() -> None:
    row = {
        "student_id": "20230003",
        "term_key": "2024-1",
        "academic_base_score_raw": None,
        "class_engagement_score_raw": None,
        "online_activeness_score_raw": None,
        "daily_routine_boundary_score_raw": None,
        "failed_course_count": None,
    }
    probability = compute_risk_probability(row)
    assert isinstance(probability, float)
    assert 0.05 <= probability <= 0.95


def test_compute_risk_probability_treats_nan_metrics_as_missing() -> None:
    row = {
        "student_id": "20230004",
        "term_key": "2024-1",
        "academic_base_score_raw": math.nan,
        "class_engagement_score_raw": math.nan,
        "online_activeness_score_raw": math.nan,
        "daily_routine_boundary_score_raw": math.nan,
        "failed_course_count": math.nan,
    }
    assert compute_risk_probability(row) == 0.52


def test_compute_base_risk_score_rewards_low_gpa_and_many_failed_courses() -> None:
    row = _base_row() | {
        "term_gpa": 1.55,
        "failed_course_count": 5,
        "borderline_course_count": 4,
        "failed_course_ratio": 0.3,
    }

    assert compute_base_risk_score(row) >= 90.0


def test_compute_risk_adjustment_score_moves_with_non_academic_dimensions() -> None:
    strong_support = build_risk_calibration(
        _base_row()
        | {
            "term_gpa": 2.4,
            "failed_course_count": 2,
            "borderline_course_count": 2,
            "failed_course_ratio": 0.12,
            "class_engagement_score_raw": 95.0,
            "online_activeness_score_raw": 94.0,
            "library_immersion_score_raw": 96.0,
            "network_habits_score_raw": 95.0,
            "daily_routine_boundary_score_raw": 93.0,
            "physical_resilience_score_raw": 97.0,
            "appraisal_status_alert_score_raw": 94.0,
        }
    )
    weak_support = build_risk_calibration(
        _base_row()
        | {
            "term_gpa": 2.4,
            "failed_course_count": 2,
            "borderline_course_count": 2,
            "failed_course_ratio": 0.12,
            "class_engagement_score_raw": 12.0,
            "online_activeness_score_raw": 14.0,
            "library_immersion_score_raw": 10.0,
            "network_habits_score_raw": 95.0,
            "daily_routine_boundary_score_raw": 93.0,
            "physical_resilience_score_raw": 11.0,
            "appraisal_status_alert_score_raw": 9.0,
            "attendance_rate": 0.45,
            "late_count": 6,
            "truancy_count": 3,
            "absence_count": 5,
            "video_completion_rate": 0.35,
            "online_test_avg_score": 60.0,
            "online_work_avg_score": 62.0,
            "online_exam_avg_score": 58.0,
            "platform_engagement_score": 40.0,
            "forum_interaction_total": 0,
            "library_completed_visit_count": 0,
            "avg_library_stay_minutes": 20.0,
            "weekly_library_visit_avg": 0.0,
            "monthly_online_duration_avg": 80.0,
            "term_online_duration_sum": 240.0,
            "online_duration_vs_school_avg_gap": 30.0,
            "first_daily_access_time_avg": 9.5,
            "first_daily_access_time_std": 2.5,
            "late_return_count": 8,
            "late_return_ratio": 0.3,
            "daily_access_time_variability": 3.0,
            "physical_test_avg_score": 60.0,
            "physical_test_pass_flag": 0,
            "weekly_running_count_avg": 0.0,
            "weekly_exercise_count_avg": 0.0,
            "scholarship_amount_sum": 0.0,
            "scholarship_level_score": 0.0,
            "negative_status_alert_flag": 1,
            "status_change_count": 3,
        }
    )

    assert strong_support["risk_adjustment_score"] < 0
    assert strong_support["adjusted_risk_score"] < strong_support["base_risk_score"]
    assert weak_support["risk_adjustment_score"] > 0
    assert weak_support["adjusted_risk_score"] > weak_support["base_risk_score"]
    assert weak_support["adjusted_risk_score"] > strong_support["adjusted_risk_score"]


def test_adjusted_risk_level_maps_to_four_chinese_labels() -> None:
    assert map_adjusted_risk_level(82.0) == "高风险"
    assert map_adjusted_risk_level(70.0) == "较高风险"
    assert map_adjusted_risk_level(55.0) == "一般风险"
    assert map_adjusted_risk_level(44.0) == "低风险"


def test_risk_delta_and_direction_helpers_are_consistent() -> None:
    assert compute_risk_delta(73.25, 60.0) == 13.25
    assert compute_risk_change_direction(13.25) == "rising"
    assert compute_risk_change_direction(-4.0) == "falling"
    assert compute_risk_change_direction(0.25) == "steady"


def test_compute_group_segment_returns_readable_group_label() -> None:
    label = compute_group_segment(
        _base_row()
        | {
            "term_gpa": 3.95,
            "failed_course_count": 0,
            "borderline_course_count": 0,
            "failed_course_ratio": 0.0,
            "attendance_rate": 0.98,
            "late_count": 0,
            "truancy_count": 0,
            "absence_count": 0,
            "video_completion_rate": 1.0,
            "online_test_avg_score": 90.0,
            "online_work_avg_score": 90.0,
            "online_exam_avg_score": 90.0,
            "platform_engagement_score": 90.0,
            "forum_interaction_total": 30,
            "first_daily_access_time_avg": 6.8,
            "first_daily_access_time_std": 0.1,
            "late_return_count": 0,
            "late_return_ratio": 0.0,
            "daily_access_time_variability": 0.2,
        }
    )
    assert label == "学习投入稳定组"


def test_compute_group_segment_uses_metric_calibrated_dimension_scores() -> None:
    label = compute_group_segment(
        _base_row()
        | {
            "academic_base_score_raw": 95.0,
            "class_engagement_score_raw": 95.0,
            "online_activeness_score_raw": 95.0,
            "network_habits_score_raw": 95.0,
            "daily_routine_boundary_score_raw": 95.0,
            "monthly_online_duration_avg": 80.0,
            "term_online_duration_sum": 240.0,
            "online_duration_vs_school_avg_gap": 30.0,
            "first_daily_access_time_avg": 9.5,
            "first_daily_access_time_std": 2.5,
            "late_return_count": 8,
            "late_return_ratio": 0.3,
            "daily_access_time_variability": 3.0,
            "physical_test_avg_score": 60.0,
            "physical_test_pass_flag": 0,
            "weekly_running_count_avg": 0.0,
            "weekly_exercise_count_avg": 0.0,
            "scholarship_amount_sum": 0.0,
            "scholarship_level_score": 0,
            "negative_status_alert_flag": 1,
            "status_change_count": 3,
        }
    )
    assert label == "作息失衡风险组"


def test_dimension_score_map_uses_dimension_code_keys() -> None:
    score_map = scoring_module._dimension_score_map(_base_row())

    assert set(score_map) == {
        "academic_base",
        "class_engagement",
        "online_activeness",
        "library_immersion",
        "network_habits",
        "daily_routine_boundary",
        "physical_resilience",
        "appraisal_status_alert",
    }
    assert "学业基础表现" not in score_map
    assert "课堂学习投入" not in score_map


def test_compute_group_segment_is_not_coupled_to_display_labels(monkeypatch: pytest.MonkeyPatch) -> None:
    original_labels = dict(scoring_module.DIMENSION_LABELS)
    monkeypatch.setattr(
        scoring_module,
        "DIMENSION_LABELS",
        {
            **original_labels,
            "academic_base": "标签已变更-学业",
            "class_engagement": "标签已变更-课堂",
            "online_activeness": "标签已变更-在线",
            "network_habits": "标签已变更-网络",
            "daily_routine_boundary": "标签已变更-作息",
            "physical_resilience": "标签已变更-体质",
            "appraisal_status_alert": "标签已变更-预警",
        },
    )

    label = compute_group_segment(
        _base_row()
        | {
            "term_gpa": 3.95,
            "failed_course_count": 0,
            "borderline_course_count": 0,
            "failed_course_ratio": 0.0,
            "attendance_rate": 0.98,
            "late_count": 0,
            "truancy_count": 0,
            "absence_count": 0,
            "video_completion_rate": 1.0,
            "online_test_avg_score": 90.0,
            "online_work_avg_score": 90.0,
            "online_exam_avg_score": 90.0,
            "platform_engagement_score": 90.0,
            "forum_interaction_total": 30,
            "first_daily_access_time_avg": 6.8,
            "first_daily_access_time_std": 0.1,
            "late_return_count": 0,
            "late_return_ratio": 0.0,
            "daily_access_time_variability": 0.2,
        }
    )

    assert label == "学习投入稳定组"


def test_build_dimension_scores_returns_eight_dimensions() -> None:
    scores = build_dimension_scores(_base_row())

    assert [item["dimension"] for item in scores] == [
        "学业基础表现",
        "课堂学习投入",
        "在线学习积极性",
        "图书馆沉浸度",
        "网络作息自律指数",
        "早晚生活作息规律",
        "体质及运动状况",
        "综合荣誉与异动预警",
    ]
    assert len(scores) == 8
    for item in scores:
        assert set(item) == {
            "dimension",
            "dimension_code",
            "score",
            "level",
            "label",
            "metrics",
            "explanation",
            "provenance",
        }
        assert 0.0 <= item["score"] <= 1.0
        assert item["level"] in {"high", "medium", "low"}
        assert isinstance(item["label"], str)
        assert item["label"] not in {"high", "medium", "low", "高", "中", "低"}
        assert isinstance(item["metrics"], list)
        assert item["metrics"]
        assert isinstance(item["explanation"], str)
        assert item["explanation"]
        assert isinstance(item["provenance"], dict)


def test_build_dimension_scores_preserves_expected_metric_values() -> None:
    score_map = {item["dimension"]: item for item in build_dimension_scores(_base_row())}

    academic_base = score_map["学业基础表现"]
    assert _metric_map(academic_base) == {
        "学期GPA": 3.6,
        "挂科门数": 1,
        "边缘课程数": 2,
        "挂科占比": 0.08,
    }
    assert "3.6" in academic_base["explanation"]
    assert "挂科" in academic_base["explanation"]

    network_habits = score_map["网络作息自律指数"]
    assert _metric_map(network_habits) == {
        "月均上网时长": 42.0,
        "学期总上网时长": 168.0,
        "相对学校平均值偏差": 6.0,
    }
    assert "不声称深夜指标" in network_habits["explanation"]
    assert "0:00-6:00" in network_habits["explanation"]
    assert all("深夜" not in metric["label"] for metric in network_habits["metrics"])


def test_build_dimension_scores_derive_score_from_metric_calibration() -> None:
    score_map = {
        item["dimension"]: item
        for item in build_dimension_scores(
            _base_row()
            | {
                "academic_base_score_raw": 99.0,
                "term_gpa": 2.1,
                "failed_course_count": 4,
                "borderline_course_count": 5,
                "failed_course_ratio": 0.3,
            }
        )
    }

    academic_base = score_map["学业基础表现"]
    assert academic_base["score"] == 0.01
    assert academic_base["score"] != 0.99
    assert academic_base["level"] == "low"
    assert academic_base["label"] == "学业基础预警"


def test_build_dimension_scores_explanation_is_business_facing_and_deterministic() -> None:
    score_map = {item["dimension"]: item for item in build_dimension_scores(_base_row())}

    academic_base = score_map["学业基础表现"]
    assert academic_base["explanation"] == "学业基础表现处于学业基础承压，主要依据是学期GPA 3.6、挂科门数 1，当前表现存在波动，需要持续观察。"

    network_habits = score_map["网络作息自律指数"]
    assert re.fullmatch(
        r"网络作息自律指数处于[\u4e00-\u9fff]+，主要依据是月均上网时长 42、学期总上网时长 168，当前网络使用强度需结合聚合时长观察。 说明：不声称深夜指标，不使用 0:00-6:00 明细；仅允许聚合上网强度。",
        network_habits["explanation"],
    )


def test_build_dimension_scores_preserves_calibration_provenance_metadata() -> None:
    score_map = {item["dimension_code"]: item for item in build_dimension_scores(_base_row())}

    class_engagement = score_map["class_engagement"]
    attendance_metric = next(
        metric for metric in class_engagement["metrics"] if metric["metric"] == "attendance_rate"
    )
    assert class_engagement["dimension"] == "课堂学习投入"
    assert class_engagement["provenance"] == {
        "has_caveated_metrics": True,
        "has_deferred_metrics": True,
        "threshold_strategies": ["fixed"],
    }
    assert attendance_metric["threshold_strategy"] == "fixed"
    assert attendance_metric["deferred_status"] == {
        "state": "caveated",
        "condition": "student_linkage_proven_for_attention_metrics",
        "fallback": "attendance_derived_only",
    }
    assert attendance_metric["caveat"] == "课堂注意力指标在学生链接未证明前暂缓，先使用出勤衍生指标。"

    network_habits = score_map["network_habits"]
    duration_metric = next(
        metric
        for metric in network_habits["metrics"]
        if metric["metric"] == "monthly_online_duration_avg"
    )
    assert network_habits["provenance"] == {
        "has_caveated_metrics": True,
        "has_deferred_metrics": True,
        "threshold_strategies": ["hybrid"],
    }
    assert duration_metric["threshold_strategy"] == "hybrid"
    assert duration_metric["deferred_status"]["state"] == "caveated"
    assert duration_metric["caveat"] == "不声称深夜指标，不使用 0:00-6:00 明细；仅允许聚合上网强度。"


def test_build_dimension_scores_surfaces_caveat_in_dimension_explanation() -> None:
    score_map = {item["dimension_code"]: item for item in build_dimension_scores(_base_row())}

    class_engagement = score_map["class_engagement"]
    assert "课堂注意力指标在学生链接未证明前暂缓" in class_engagement["explanation"]
    assert class_engagement["provenance"]["has_caveated_metrics"] is True


def test_build_dimension_scores_uses_distribution_context_for_hybrid_metrics() -> None:
    scores = build_dimension_scores(
        _base_row()
        | {
            "monthly_online_duration_avg": 50.0,
            "term_online_duration_sum": 160.0,
            "online_duration_vs_school_avg_gap": 6.0,
            "distribution_context": {
                "monthly_online_duration_avg": {"q33": 45.0, "q67": 55.0},
                "term_online_duration_sum": {"q33": 150.0, "q67": 170.0},
                "online_duration_vs_school_avg_gap": {"q33": 4.0, "q67": 8.0},
            },
        }
    )
    network_habits = next(item for item in scores if item["dimension_code"] == "network_habits")

    assert network_habits["score"] == 0.55
    assert network_habits["level"] == "medium"
    assert network_habits["provenance"]["threshold_strategies"] == ["hybrid"]


def test_dimension_scores_are_clamped_and_rounded() -> None:
    scores = build_dimension_scores(
        _base_row()
        | {
            "academic_base_score_raw": 120,
            "class_engagement_score_raw": -5,
            "online_activeness_score_raw": 50.555,
            "library_immersion_score_raw": None,
            "network_habits_score_raw": math.nan,
            "daily_routine_boundary_score_raw": 101,
            "physical_resilience_score_raw": 66.666,
            "appraisal_status_alert_score_raw": -100,
        }
    )

    assert len(scores) == 8
    for item in scores:
        assert 0.0 <= item["score"] <= 1.0
        assert item["score"] == round(item["score"], 2)
        assert item["level"] in {"high", "medium", "low"}


def test_build_dimension_scores_handles_missing_raw_metrics() -> None:
    scores = build_dimension_scores(
        _base_row()
        | {
            "library_immersion_score_raw": None,
            "network_habits_score_raw": None,
            "appraisal_status_alert_score_raw": None,
        }
    )

    score_map = {item["dimension"]: item for item in scores}
    assert score_map["图书馆沉浸度"]["score"] == 0.73
    assert score_map["网络作息自律指数"]["score"] == 0.63
    assert score_map["综合荣誉与异动预警"]["score"] == 0.82
    assert score_map["图书馆沉浸度"]["metrics"]
    assert score_map["网络作息自律指数"]["metrics"]
    assert score_map["综合荣誉与异动预警"]["metrics"]
