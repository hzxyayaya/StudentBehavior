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
    "学号",
    "瀛﹀彿",
    "XH",
    "XSBH",
    "LOGIN_NAME",
    "USERNUM",
    "SID",
)

_STUDENT_FIELD_ALIASES = {
    "gender": ("gender", "XB", "性别", "鎬у埆"),
    "ethnicity": ("ethnicity", "MZMC", "民族", "姘戞棌"),
    "political_status": ("political_status", "ZZMMMC", "政治面貌", "鏀挎不闈㈣矊"),
    "major_name": ("major_name", "MAJOR_NAME", "ZYM", "专业名称", "涓撲笟鍚嶇О"),
    "college_name": ("college_name", "COLLEGE_NAME", "学院名称", "瀛﹂櫌鍚嶇О"),
    "class_name": ("class_name", "CLASS_NAME", "XSM", "班级名称", "鐝骇鍚嶇О"),
    "enrollment_year": ("enrollment_year", "RXSJ", "ENROLLMENT_YEAR", "入学年份", "鍏ュ骞翠唤"),
}


def load_students(rows: list[dict[str, Any]]) -> pd.DataFrame:
    records = []
    for row in rows:
        student_id = _pick_student_id(row)
        if student_id is None:
            continue

        record = {"student_id": student_id}
        for column in _STUDENT_COLUMNS[1:]:
            value = _first_value(row, *_STUDENT_FIELD_ALIASES[column])
            if column == "enrollment_year":
                record[column] = _normalize_enrollment_year(value)
            else:
                record[column] = _normalize_value(value)
        records.append(record)

    if not records:
        return pd.DataFrame(columns=_STUDENT_COLUMNS)

    frame = pd.DataFrame(records, columns=_STUDENT_COLUMNS)
    frame = frame.drop_duplicates(subset=["student_id"], keep="first", ignore_index=True)
    return frame.astype(object).where(pd.notna(frame), None)


def _pick_student_id(row: dict[str, Any]) -> str | None:
    for key in _STUDENT_ID_KEYS:
        student_id = normalize_student_id(row.get(key))
        if student_id is not None:
            return student_id
    return None


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


def _normalize_value(raw: Any) -> Any:
    if raw is None or isinstance(raw, bool):
        return None
    if isinstance(raw, float) and isnan(raw):
        return None
    if isinstance(raw, str):
        value = raw.strip()
        return value or None
    if isinstance(raw, int):
        return raw
    if isinstance(raw, float) and raw.is_integer():
        return int(raw)
    return raw


def _normalize_enrollment_year(raw: Any) -> int | None:
    value = _normalize_value(raw)
    if value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value[:4].isdigit():
        return int(value[:4])
    return None
