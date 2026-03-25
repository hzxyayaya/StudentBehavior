from decimal import Decimal
from fractions import Fraction

import pytest

from student_behavior_etl.normalize import normalize_student_id, normalize_term_key


def test_normalize_student_id_trims_whitespace() -> None:
    assert normalize_student_id("  pjxyqxbj337  ") == "pjxyqxbj337"


def test_normalize_student_id_returns_none_for_blank_value() -> None:
    assert normalize_student_id("   ") is None


def test_normalize_student_id_returns_none_for_none() -> None:
    assert normalize_student_id(None) is None


def test_normalize_student_id_returns_none_for_pandas_missing_values() -> None:
    import pandas as pd

    assert normalize_student_id(pd.NA) is None
    assert normalize_student_id(float("nan")) is None


def test_normalize_term_key_formats_valid_term() -> None:
    assert normalize_term_key("2023-2024", 2) == "2023-2"


def test_normalize_term_key_formats_first_term() -> None:
    assert normalize_term_key("2023-2024", 1) == "2023-1"


@pytest.mark.parametrize(
    "raw_xn, raw_xq",
    [
        ("", 1),
        (None, 1),
        ("2023-2024", None),
        ("2023-2024", 3),
        ("2023-2024", 1.9),
        ("2023-2024", Decimal("1.9")),
        ("2023-2024", Fraction(3, 2)),
        ("2023-2024", True),
        ("2023-2024", False),
        ("2023/2024", 1),
        ("foo-bar", 1),
        ("23-2024", 1),
        ("2023-2025", 1),
    ],
)
def test_normalize_term_key_rejects_invalid_values(raw_xn, raw_xq) -> None:
    assert normalize_term_key(raw_xn, raw_xq) is None
