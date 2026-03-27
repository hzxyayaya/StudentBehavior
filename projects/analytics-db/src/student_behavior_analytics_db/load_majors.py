from __future__ import annotations

from math import isnan
from typing import Any

import pandas as pd

_MAJOR_COLUMNS = (
    "major_id",
    "major_name",
    "college_name",
)


def load_majors(rows: list[dict[str, Any]]) -> pd.DataFrame:
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
    return pd.DataFrame(records, columns=_MAJOR_COLUMNS)


def _clean_text(raw: Any) -> str | None:
    if raw is None or isinstance(raw, bool):
        return None
    if isinstance(raw, float) and isnan(raw):
        return None
    text = str(raw).strip()
    return text or None
