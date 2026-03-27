from __future__ import annotations

from math import isnan
from typing import Any

import pandas as pd

_COURSE_COLUMNS = (
    "course_id",
    "course_code",
    "course_name",
    "course_type",
    "credit",
    "hours",
    "assessment_type",
)

_COURSE_FIELD_ALIASES = {
    "course_id": ("course_id", "课程号", "课程编号", "课程代码", "course_code"),
    "course_code": ("course_code", "课程代码", "课程编号", "课程号"),
    "course_name": ("course_name", "课程名称", "课程名"),
    "course_type": ("course_type", "课程类型"),
    "credit": ("credit", "学分"),
    "hours": ("hours", "学时"),
    "assessment_type": ("assessment_type", "考核方式"),
}


def load_courses(rows: list[dict[str, Any]]) -> pd.DataFrame:
    records = []
    for row in rows:
        course_id = _clean_text(_first_value(row, *_COURSE_FIELD_ALIASES["course_id"]))
        if course_id is None:
            continue
        records.append(
            {
                "course_id": course_id,
                "course_code": _clean_text(_first_value(row, *_COURSE_FIELD_ALIASES["course_code"])),
                "course_name": _clean_text(_first_value(row, *_COURSE_FIELD_ALIASES["course_name"])),
                "course_type": _clean_text(_first_value(row, *_COURSE_FIELD_ALIASES["course_type"])),
                "credit": _clean_number(_first_value(row, *_COURSE_FIELD_ALIASES["credit"])),
                "hours": _clean_number(_first_value(row, *_COURSE_FIELD_ALIASES["hours"])),
                "assessment_type": _clean_text(_first_value(row, *_COURSE_FIELD_ALIASES["assessment_type"])),
            }
        )
    if not records:
        return pd.DataFrame(columns=_COURSE_COLUMNS)
    frame = pd.DataFrame(records, columns=_COURSE_COLUMNS)
    frame = frame.drop_duplicates(subset=["course_id"], keep="first", ignore_index=True)
    return frame.astype(object).where(pd.notna(frame), None)


def _first_value(row: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key not in row:
            continue
        value = row.get(key)
        if value is None or isinstance(value, bool):
            continue
        if isinstance(value, float) and isnan(value):
            continue
        if isinstance(value, str):
            text = value.strip()
            if text:
                return text
            continue
        return value
    return None


def _clean_text(raw: Any) -> str | None:
    if raw is None or isinstance(raw, bool):
        return None
    if isinstance(raw, float) and isnan(raw):
        return None
    text = str(raw).strip()
    return text or None


def _clean_number(raw: Any) -> int | float | None:
    if raw is None or isinstance(raw, bool):
        return None
    if isinstance(raw, float) and isnan(raw):
        return None
    if isinstance(raw, (int, float)):
        return raw
    text = str(raw).strip()
    if not text:
        return None
    try:
        number = float(text)
    except ValueError:
        return None
    return int(number) if number.is_integer() else number
