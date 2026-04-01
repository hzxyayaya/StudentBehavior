from student_behavior_analytics_db.normalize_terms import (
    infer_term_from_month_only,
    normalize_term_key,
)


def test_normalize_term_key_from_school_year_and_term_no():
    assert normalize_term_key("2024-2025", 1) == "2024-1"


def test_normalize_term_key_from_stable_combined_format():
    assert normalize_term_key("2020-2021学年第1学期", None) == "2020-1"


def test_normalize_term_key_rejects_invalid_school_years():
    assert normalize_term_key("2020-2022", 1) is None


def test_normalize_term_key_rejects_invalid_term_numbers():
    assert normalize_term_key("2020-2021", 3) is None


def test_normalize_term_key_rejects_booleans():
    assert normalize_term_key(True, 1) is None
    assert normalize_term_key("2020-2021", False) is None


def test_normalize_term_key_rejects_unsupported_combined_format_when_raw_term_is_none():
    assert normalize_term_key("2020-2022学年第1学期", None) is None


def test_guess_based_term_inference_is_rejected():
    assert infer_term_from_month_only("2024-03-01") == "2023-2"
    assert infer_term_from_month_only("2024-09-01") == "2024-1"
    assert infer_term_from_month_only("2025-01-10") == "2024-1"
