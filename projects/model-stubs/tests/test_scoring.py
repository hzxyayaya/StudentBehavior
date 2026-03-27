import math

from student_behavior_model_stubs.scoring import compute_risk_probability
from student_behavior_model_stubs.scoring import map_risk_level


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
