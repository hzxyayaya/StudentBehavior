from __future__ import annotations

from math import isnan
from typing import Any

try:  # pragma: no cover - pandas is not installed in the project test env
    import pandas as pd
except ModuleNotFoundError:  # pragma: no cover
    pd = None

_MAJOR_COLUMNS = (
    "major_id",
    "major_name",
    "college_name",
)


def load_majors(rows: list[dict[str, Any]]) -> object:
    records = []
    for row in rows:
        major_id = _clean_text(row.get("major_id") or row.get("major_code") or row.get("major_name"))
        major_name = _clean_text(row.get("major_name"))
        if major_id is None and major_name is None:
            continue
        records.append(
            {
                "major_id": major_id or major_name,
                "major_name": major_name or major_id,
                "college_name": _clean_text(row.get("college_name")),
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


def _make_frame(records: list[dict[str, Any]]) -> object:
    if pd is not None:
        return pd.DataFrame(records, columns=_MAJOR_COLUMNS)
    return _MiniDataFrame(records, _MAJOR_COLUMNS)


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

