from __future__ import annotations

from math import isnan
from typing import Any

import pandas as pd

_MAJOR_COLUMNS = (
    "major_id",
    "major_name",
    "college_name",
)

_MAJOR_FIELD_ALIASES = {
    "major_id": ("major_id", "专业代码", "专业编号", "major_code"),
    "major_name": ("major_name", "专业名称", "专业"),
    "college_name": ("college_name", "学院名称", "学院"),
}


def load_majors(rows: list[dict[str, Any]]) -> pd.DataFrame:
    records = []
    for row in rows:
        major_id = _clean_text(_first_value(row, *_MAJOR_FIELD_ALIASES["major_id"]))
        major_name = _clean_text(_first_value(row, *_MAJOR_FIELD_ALIASES["major_name"]))
        college_name = _clean_text(_first_value(row, *_MAJOR_FIELD_ALIASES["college_name"]))
        if major_id is None and major_name is None:
            continue
        records.append(
            {
                "major_id": major_id,
                "major_name": major_name or major_id,
                "college_name": college_name,
            }
        )
    if not records:
        return pd.DataFrame(columns=_MAJOR_COLUMNS)
    deduped_records = []
    seen = set()
    for record in records:
        key = record["major_id"] if record["major_id"] is not None else (record["major_name"], record["college_name"])
        if key in seen:
            continue
        seen.add(key)
        if record["major_id"] is None:
            record = {**record, "major_id": record["major_name"]}
        deduped_records.append(record)
    frame = pd.DataFrame(deduped_records, columns=_MAJOR_COLUMNS)
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
