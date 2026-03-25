from __future__ import annotations

from numbers import Real
import re


def normalize_student_id(raw: object) -> str | None:
    if raw is None:
        return None

    value = str(raw).strip()
    return value or None


def normalize_term_key(raw_xn: object, raw_xq: object) -> str | None:
    if raw_xn is None or raw_xq is None:
        return None

    xn = str(raw_xn).strip()
    match = re.fullmatch(r"(\d{4})-(\d{4})", xn)
    if match is None:
        return None

    left_year = int(match.group(1))
    right_year = int(match.group(2))
    if right_year != left_year + 1:
        return None

    if isinstance(raw_xq, bool):
        return None

    if isinstance(raw_xq, Real):
        try:
            xq = int(raw_xq)
        except (TypeError, ValueError, OverflowError):
            return None
        if raw_xq != xq:
            return None
    else:
        raw_xq_text = str(raw_xq).strip()
        if raw_xq_text not in {"1", "2"}:
            return None
        xq = int(raw_xq_text)

    if xq not in (1, 2):
        return None

    return f"{left_year}-{xq}"
