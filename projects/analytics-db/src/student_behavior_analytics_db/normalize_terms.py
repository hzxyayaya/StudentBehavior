from __future__ import annotations

import re


def normalize_term_key(raw_year: object, raw_term: object) -> str | None:
    if raw_year is None or raw_term is None:
        return None
    if isinstance(raw_year, bool) or isinstance(raw_term, bool):
        return None

    year_text = str(raw_year).strip()
    match = re.fullmatch(r"(\d{4})-(\d{4})", year_text)
    if match is None:
        return None

    school_year_start = int(match.group(1))
    school_year_end = int(match.group(2))
    if school_year_end != school_year_start + 1:
        return None

    term_text = str(raw_term).strip()
    if term_text not in {"1", "2"}:
        return None

    return f"{school_year_start}-{term_text}"


def infer_term_from_month_only(raw_date: object) -> str | None:
    return None
