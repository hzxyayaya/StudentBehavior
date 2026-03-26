from student_behavior_analytics_db.normalize_terms import (
    infer_term_from_month_only,
    normalize_term_key,
)


def test_normalize_term_key_from_school_year_and_term_no():
    assert normalize_term_key("2024-2025", 1) == "2024-1"


def test_guess_based_term_inference_is_rejected():
    assert infer_term_from_month_only("2023-03-01") is None
