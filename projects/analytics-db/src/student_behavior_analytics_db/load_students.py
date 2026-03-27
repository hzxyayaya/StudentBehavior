from __future__ import annotations

from math import isnan
from typing import Any

import pandas as pd

from .normalize_ids import normalize_student_id

_STUDENT_COLUMNS = (
    "student_id",
    "gender",
    "ethnicity",
    "political_status",
    "major_name",
    "college_name",
    "class_name",
    "enrollment_year",
)

_STUDENT_ID_KEYS = (
    "student_id",
    "XH",
    "XSBH",
    "LOGIN_NAME",
    "USERNUM",
    "SID",
    "cardld",
    "IDSERTAL",
    "KS_XH",
    "XHHGH",
)


def load_students(rows: list[dict[str, Any]]) -> pd.DataFrame:
    records = []
    for row in rows:
        student_id = _pick_student_id(row)
        if student_id is None:
            continue

        record = {"student_id": student_id}
        for column in _STUDENT_COLUMNS[1:]:
            record[column] = _normalize_value(row.get(column))
        records.append(record)

    return pd.DataFrame(records, columns=_STUDENT_COLUMNS)


def _pick_student_id(row: dict[str, Any]) -> str | None:
    for key in _STUDENT_ID_KEYS:
        student_id = normalize_student_id(row.get(key))
        if student_id is not None:
            return student_id
    return None


def _normalize_value(raw: Any) -> Any:
    if raw is None or isinstance(raw, bool):
        return None
    if isinstance(raw, float) and isnan(raw):
        return None
    if isinstance(raw, str):
        value = raw.strip()
        return value or None
    if isinstance(raw, int) and not isinstance(raw, bool):
        return raw
    return raw
