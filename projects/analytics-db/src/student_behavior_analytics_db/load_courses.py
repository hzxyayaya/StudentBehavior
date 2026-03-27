from __future__ import annotations

from math import isnan
from typing import Any

try:  # pragma: no cover - pandas is not installed in the project test env
    import pandas as pd
except ModuleNotFoundError:  # pragma: no cover
    pd = None

_COURSE_COLUMNS = (
    "course_id",
    "course_code",
    "course_name",
    "course_type",
    "credit",
    "hours",
    "assessment_type",
)


def load_courses(rows: list[dict[str, Any]]) -> object:
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
    return _make_frame(records)


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


def _make_frame(records: list[dict[str, Any]]) -> object:
    if pd is not None:
        return pd.DataFrame(records, columns=_COURSE_COLUMNS)
    return _MiniDataFrame(records, _COURSE_COLUMNS)


class _MiniDataFrame:
    def __init__(self, records: list[dict[str, Any]], columns: tuple[str, ...]) -> None:
        self._records = [
            {column: record.get(column) for column in columns} for record in records
        ]
        self._columns = list(columns)

    @property
    def columns(self) -> list[str]:
        return list(self._columns)

    def to_dict(self, orient: str = "dict") -> list[dict[str, Any]]:
        if orient != "records":
            raise ValueError("MiniDataFrame only supports orient='records'")
        return [dict(record) for record in self._records]

