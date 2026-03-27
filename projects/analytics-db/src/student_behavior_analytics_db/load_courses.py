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


def load_courses(rows: list[dict[str, Any]]) -> pd.DataFrame:
    records = []
    for row in rows:
        course_id = _clean_text(row.get("course_id") or row.get("course_code"))
        if course_id is None:
            continue
        records.append(
            {
                "course_id": course_id,
                "course_code": _clean_text(row.get("course_code")),
                "course_name": _clean_text(row.get("course_name")),
                "course_type": _clean_text(row.get("course_type")),
                "credit": _clean_number(row.get("credit")),
                "hours": _clean_number(row.get("hours")),
                "assessment_type": _clean_text(row.get("assessment_type")),
            }
        )
    return pd.DataFrame(records, columns=_COURSE_COLUMNS)


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
