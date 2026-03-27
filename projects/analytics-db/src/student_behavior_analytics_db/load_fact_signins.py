from __future__ import annotations

import re
from typing import Any

import pandas as pd

from .normalize_ids import normalize_student_id
from .normalize_terms import normalize_term_key

_SIGNIN_COLUMNS = (
    "student_id",
    "term_key",
    "signed_in_at",
    "source_file",
    "source_row_hash",
)

_STUDENT_ID_KEYS = (
    "student_id",
    "学号",
    "学生学号",
    "学籍号",
    "XH",
    "XSBH",
    "LOGIN_NAME",
    "USERNUM",
    "SID",
)

_TERM_YEAR_KEYS = ("XN", "xn", "school_year", "学年", "学年度", "开课学年")
_TERM_NO_KEYS = ("XQ", "xq", "term_no", "学期", "学期序号", "开课学期")
_COMBINED_TERM_KEYS = ("term_key", "学年学期", "学年学期名称", "学期名称", "xnxq", "XNXQ")
_STANDARD_TERM_KEY_RE = re.compile(r"^\d{4}-[12]$")


def load_fact_signins(rows: list[dict[str, Any]]) -> pd.DataFrame:
    records = []
    for row in rows:
        student_id = _pick_student_id(row)
        term_key = _pick_term_key(row)
        source_file = _normalize_text(_first_value(row, "source_file", "源文件"))
        source_row_hash = _normalize_text(_first_value(row, "source_row_hash", "row_hash"))
        if student_id is None or term_key is None or source_file is None or source_row_hash is None:
            continue

        records.append(
            {
                "student_id": student_id,
                "term_key": term_key,
                "signed_in_at": _normalize_text(_first_value(row, "signed_in_at", "签到时间", "签到时刻")),
                "source_file": source_file,
                "source_row_hash": source_row_hash,
            }
        )

    return _as_frame(records, _SIGNIN_COLUMNS)


def _pick_student_id(row: dict[str, Any]) -> str | None:
    for key in _STUDENT_ID_KEYS:
        student_id = normalize_student_id(row.get(key))
        if student_id is not None:
            return student_id
    return None


def _pick_term_key(row: dict[str, Any]) -> str | None:
    for key in _COMBINED_TERM_KEYS:
        if key in row:
            term_key = _normalize_term_key_value(row.get(key))
            if term_key is not None:
                return term_key

    raw_year = _first_value(row, *_TERM_YEAR_KEYS)
    raw_term = _first_value(row, *_TERM_NO_KEYS)
    if raw_year is None or raw_term is None:
        return None
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


def _normalize_text(raw: Any) -> str | None:
    if raw is None or isinstance(raw, bool):
        return None
    if isinstance(raw, float) and raw != raw:
        return None
    text = str(raw).strip()
    return text or None


def _as_frame(records: list[dict[str, Any]], columns: tuple[str, ...]) -> pd.DataFrame:
    if not records:
        return pd.DataFrame(columns=columns)
    frame = pd.DataFrame(records, columns=columns)
    return frame.astype(object).where(pd.notna(frame), None)
