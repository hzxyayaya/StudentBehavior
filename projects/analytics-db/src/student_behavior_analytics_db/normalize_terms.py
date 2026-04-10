from __future__ import annotations

import re

import pandas as pd

_SCHOOL_YEAR_RE = re.compile(r"^(\d{4})-(\d{4})$")
_DATE_YYYYMMDD_RE = re.compile(r"^(\d{4})(\d{2})(\d{2})$")
_COMBINED_TERM_PATTERNS = (
    re.compile(r"^(\d{4})-(\d{4})学年(?:第)?([12])学期$"),
    re.compile(r"^(\d{4})-(\d{4})\s*([12])$"),
    re.compile(r"^(\d{4})-(\d{4})[-_]?([12])$"),
)


def normalize_term_key(raw_year: object, raw_term: object) -> str | None:
    if raw_term is None:
        return _normalize_combined_term_key(raw_year)
    if raw_year is None or isinstance(raw_year, bool) or isinstance(raw_term, bool):
        return None

    school_year_start = _normalize_school_year(raw_year)
    if school_year_start is None:
        return None

    term_text = str(raw_term).strip()
    if term_text not in {"1", "2"}:
        return None

    return f"{school_year_start}-{term_text}"


def infer_term_from_month_only(raw_date: object) -> str | None:
    if raw_date is None or isinstance(raw_date, bool):
        return None
    parsed = _parse_date_like(raw_date)
    if parsed is None:
        return None
    year = int(parsed.year)
    month = int(parsed.month)
    if 9 <= month <= 12:
        return f"{year}-1"
    if month == 1:
        return f"{year - 1}-1"
    if 2 <= month <= 8:
        return f"{year - 1}-2"
    return None


def _parse_date_like(raw_date: object) -> pd.Timestamp | None:
    if raw_date is None or isinstance(raw_date, bool):
        return None
    text = str(raw_date).strip()
    if not text:
        return None
    compact_match = _DATE_YYYYMMDD_RE.fullmatch(text)
    if compact_match is not None:
        try:
            parsed = pd.Timestamp(
                year=int(compact_match.group(1)),
                month=int(compact_match.group(2)),
                day=int(compact_match.group(3)),
            )
        except ValueError:
            return None
        return parsed
    try:
        parsed = pd.to_datetime(raw_date, errors="coerce")
    except (TypeError, ValueError, OverflowError):
        return None
    if pd.isna(parsed):
        return None
    return pd.Timestamp(parsed)


def _normalize_combined_term_key(raw_year: object) -> str | None:
    if raw_year is None or isinstance(raw_year, bool):
        return None

    text = str(raw_year).strip()
    if not text:
        return None

    for pattern in _COMBINED_TERM_PATTERNS:
        match = pattern.fullmatch(text)
        if match is None:
            continue
        school_year_start = int(match.group(1))
        school_year_end = int(match.group(2))
        if school_year_end != school_year_start + 1:
            return None
        return f"{school_year_start}-{match.group(3)}"
    return None


def _normalize_school_year(raw_year: object) -> int | None:
    text = str(raw_year).strip()
    match = _SCHOOL_YEAR_RE.fullmatch(text)
    if match is None:
        return None

    school_year_start = int(match.group(1))
    school_year_end = int(match.group(2))
    if school_year_end != school_year_start + 1:
        return None
    return school_year_start
