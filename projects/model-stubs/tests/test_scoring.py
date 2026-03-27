import math

from student_behavior_model_stubs.scoring import compute_risk_probability
from student_behavior_model_stubs.scoring import map_risk_level
from student_behavior_model_stubs.scoring import build_dimension_scores
from student_behavior_model_stubs.scoring import compute_quadrant_label


def test_compute_risk_probability_is_deterministic() -> None:
    row = {
        "student_id": "20230001",
        "term_key": "2023-1",
        "risk_label": 1,
        "failed_course_count": 2,
        "avg_course_score": 61.0,
        "attendance_normal_rate": 0.42,
    }
    assert compute_risk_probability(row) == 0.67
    assert compute_risk_probability(row) == compute_risk_probability(row)


def test_map_risk_level_respects_frozen_thresholds() -> None:
    assert map_risk_level(0.80) == "high"
    assert map_risk_level(0.50) == "medium"
    assert map_risk_level(0.30) == "low"


def test_compute_risk_probability_is_clamped_and_rounded() -> None:
    row = {
        "student_id": "20230002",
        "term_key": "2023-1",
        "risk_label": 1,
        "failed_course_count": 10,
        "avg_course_score": 0.0,
        "attendance_normal_rate": 0.0,
    }
    probability = compute_risk_probability(row)
    assert 0.05 <= probability <= 0.95
    assert probability == round(probability, 2)
    assert probability == 0.95


def test_compute_risk_probability_handles_null_metrics_without_crash() -> None:
    row = {
        "student_id": "20230003",
        "term_key": "2023-1",
        "risk_label": None,
        "failed_course_count": None,
        "avg_course_score": None,
        "attendance_normal_rate": None,
    }
    probability = compute_risk_probability(row)
    assert isinstance(probability, float)
    assert 0.05 <= probability <= 0.95


def test_compute_risk_probability_treats_nan_metrics_as_missing() -> None:
    row = {
        "student_id": "20230004",
        "term_key": "2023-1",
        "risk_label": math.nan,
        "failed_course_count": math.nan,
        "avg_course_score": math.nan,
        "attendance_normal_rate": math.nan,
    }
    assert compute_risk_probability(row) == 0.38


def test_compute_quadrant_label_returns_frozen_enum() -> None:
    label = compute_quadrant_label(
        {
            "student_id": "20230001",
            "term_key": "2023-1",
            "attendance_normal_rate": 0.88,
            "sign_event_count": 20,
            "selected_course_count": 9,
            "avg_course_score": 86,
            "failed_course_count": 0,
            "library_visit_count": 25,
        }
    )
    assert label in {"自律共鸣型", "被动守纪型", "脱节离散型", "情绪驱动型"}


def test_build_dimension_scores_returns_four_dimensions() -> None:
    scores = build_dimension_scores(
        {
            "student_id": "20230001",
            "term_key": "2023-1",
            "attendance_normal_rate": 0.88,
            "sign_event_count": 20,
            "selected_course_count": 9,
            "avg_course_score": 86,
            "failed_course_count": 0,
            "library_visit_count": 25,
        }
    )

    assert [item["dimension"] for item in scores] == [
        "学业基础表现",
        "课堂学习投入",
        "学习行为活跃度",
        "生活规律与资源使用",
    ]
    assert len(scores) == 4
    for item in scores:
        assert 0.0 <= item["score"] <= 1.0


def test_dimension_scores_are_clamped_and_rounded() -> None:
    scores = build_dimension_scores(
        {
            "student_id": "20230002",
            "term_key": "2023-1",
            "attendance_normal_rate": 1.7,
            "sign_event_count": -3,
            "selected_course_count": 99,
            "avg_course_score": 120,
            "failed_course_count": 50,
            "library_visit_count": -10,
        }
    )

    assert len(scores) == 4
    for item in scores:
        assert 0.0 <= item["score"] <= 1.0
        assert item["score"] == round(item["score"], 2)


def test_compute_quadrant_label_handles_missing_library_metrics() -> None:
    label = compute_quadrant_label(
        {
            "student_id": "20230003",
            "term_key": "2023-1",
            "attendance_normal_rate": 0.74,
            "sign_event_count": 12,
            "selected_course_count": 7,
            "avg_course_score": 77,
            "failed_course_count": 1,
        }
    )

    assert label in {"自律共鸣型", "被动守纪型", "脱节离散型", "情绪驱动型"}
