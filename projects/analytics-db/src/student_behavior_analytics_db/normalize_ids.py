from __future__ import annotations

from math import isnan


def normalize_student_id(raw: object) -> str | None:
    if raw is None or isinstance(raw, bool):
        return None
    if isinstance(raw, float) and isnan(raw):
        return None

    value = str(raw).strip()
    return value or None
