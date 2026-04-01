from __future__ import annotations

import re
from typing import Any

import pandas as pd

from .normalize_ids import normalize_student_id
from .normalize_terms import infer_term_from_month_only
from .normalize_terms import normalize_term_key

_GRADE_COLUMNS = (
    "student_id",
    "term_key",
    "course_id",
    "course_name",
    "score",
    "gpa",
    "passed",
    "source_file",
    "source_row_hash",
)

_STUDENT_ID_KEYS = ("student_id", "XH", "XSBH", "LOGIN_NAME", "USERNUM", "SID")
_TERM_YEAR_KEYS = ("XN", "xn", "school_year", "KKXN")
_TERM_NO_KEYS = ("XQ", "xq", "term_no", "KKXQ")
_COMBINED_TERM_KEYS = ("term_key", "xnxq", "XNXQ")
_STANDARD_TERM_KEY_RE = re.compile(r"^\d{4}-[12]$")


def load_fact_grades(rows: list[dict[str, Any]]) -> pd.DataFrame:
    records = []
    for row in rows:
        student_id = _pick_student_id(row)
        exam_at = _normalize_timestamp(_first_value(row, "KSSJ", "exam_at"))
        term_key = _pick_term_key(row, exam_at)
        source_file = _normalize_text(_first_value(row, "source_file"))
        source_row_hash = _normalize_text(_first_value(row, "source_row_hash", "row_hash"))
        if student_id is None or term_key is None or source_file is None or source_row_hash is None:
            continue

        score = _normalize_number(_first_value(row, "score", "KCCJ"))
        passed = _normalize_bool(_first_present_value(row, "passed"))
        if passed is None and score is not None:
            passed = score >= 60

        records.append(
            {
                "student_id": student_id,
                "term_key": term_key,
                "course_id": _normalize_text(_first_value(row, "course_id", "KCH")),
                "course_name": _normalize_text(_first_value(row, "course_name", "KCM")),
                "score": score,
                "gpa": _normalize_number(_first_value(row, "gpa", "JDCJ")),
                "passed": passed,
                "source_file": source_file,
                "source_row_hash": source_row_hash,
            }
        )

    return _as_frame(records, _GRADE_COLUMNS)


def _pick_student_id(row: dict[str, Any]) -> str | None:
    for key in _STUDENT_ID_KEYS:
        student_id = normalize_student_id(row.get(key))
        if student_id is not None:
            return student_id
    return None


def _pick_term_key(row: dict[str, Any], exam_at: str | None) -> str | None:
    for key in _COMBINED_TERM_KEYS:
        if key in row:
            term_key = _normalize_term_key_value(row.get(key))
            if term_key is not None:
                return term_key

    raw_year = _first_value(row, *_TERM_YEAR_KEYS)
    raw_term = _first_value(row, *_TERM_NO_KEYS)
    if raw_year is None or raw_term is None:
        return infer_term_from_month_only(exam_at)
    return normalize_term_key(raw_year, raw_term)


def _normalize_term_key_value(raw: Any) -> str | None:
    if raw is None or isinstance(raw, bool):
        return None
    text = str(raw).strip()
    if not text:
        return None
    if _STANDARD_TERM_KEY_RE.fullmatch(text):
        return text
    return normalize_term_key(text, None)


def _normalize_timestamp(raw: Any) -> str | None:
    if raw is None or isinstance(raw, bool):
        return None
    if isinstance(raw, float) and raw != raw:
        return None
    try:
        parsed = pd.to_datetime(raw, errors="coerce")
    except (TypeError, ValueError, OverflowError):
        return None
    if pd.isna(parsed):
        return None
    return pd.Timestamp(parsed).strftime("%Y-%m-%d %H:%M:%S")


def _first_value(row: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key not in row:
            continue
        value = row.get(key)
        if value is None or isinstance(value, bool):
            continue
        if isinstance(value, float) and value != value:
            continue
        if isinstance(value, str):
            text = value.strip()
            if text:
                return text
            continue
        return value
    return None


def _first_present_value(row: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key not in row:
            continue
        value = row.get(key)
        if isinstance(value, float) and value != value:
            continue
        if isinstance(value, str):
            text = value.strip()
            if text:
                return text
            continue
        return value
    return None


def _normalize_text(raw: Any) -> str | None:
    if raw is None or isinstance(raw, bool):
        return None
    if isinstance(raw, float) and raw != raw:
        return None
    text = str(raw).strip()
    return text or None


def _normalize_number(raw: Any) -> float | int | None:
    if raw is None or isinstance(raw, bool):
        return None
    if isinstance(raw, float) and raw != raw:
        return None
    if isinstance(raw, (int, float)):
        if isinstance(raw, float) and raw.is_integer():
            return int(raw)
        return raw
    text = str(raw).strip()
    if not text:
        return None
    try:
        number = float(text)
    except ValueError:
        return None
    if number.is_integer():
        return int(number)
    return number


def _normalize_bool(raw: Any) -> bool | None:
    if raw is None:
        return None
    if isinstance(raw, bool):
        return raw
    if isinstance(raw, int):
        return bool(raw)
    text = str(raw).strip().lower()
    if text in {"1", "true", "yes", "y"}:
        return True
    if text in {"0", "false", "no", "n"}:
        return False
    return None


def _as_frame(records: list[dict[str, Any]], columns: tuple[str, ...]) -> pd.DataFrame:
    if not records:
        return pd.DataFrame(columns=columns)
    frame = pd.DataFrame(records, columns=columns)
    return frame.astype(object).where(pd.notna(frame), None)
