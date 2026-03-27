from __future__ import annotations

import re
from datetime import date, datetime
from typing import Any

import pandas as pd

from .normalize_terms import normalize_term_key

_TERM_COLUMNS = (
    "term_key",
    "school_year",
    "term_no",
    "term_name",
    "start_date",
    "end_date",
    "is_analysis_term",
)


def load_terms(rows: list[dict[str, Any]]) -> pd.DataFrame:
    records = []
    for row in rows:
        record = _build_term_record(row)
        if record is not None:
            records.append(record)
    return pd.DataFrame(records, columns=_TERM_COLUMNS)


def _build_term_record(row: dict[str, Any]) -> dict[str, Any] | None:
    combined_term = _first_text(row, "term_name", "term_key", "xnxq", "XNXQ")
    school_year = _first_text(row, "school_year", "xn", "schoolYear", "XN")
    term_no = _first_term_no(row)

    term_key = None
    term_name = None

    if combined_term is not None:
        term_key = normalize_term_key(combined_term, None)
        if term_key is not None:
            school_year, term_no = _split_term_key(term_key)
            term_name = combined_term.strip()

    if term_key is None and school_year is not None and term_no is not None:
        term_key = normalize_term_key(school_year, term_no)
        if term_key is not None:
            term_name = f"{school_year}学年第{term_no}学期"

    if term_key is None:
        return None

    return {
        "term_key": term_key,
        "school_year": school_year,
        "term_no": term_no,
        "term_name": term_name,
        "start_date": _normalize_date(row.get("start_date")),
        "end_date": _normalize_date(row.get("end_date")),
        "is_analysis_term": _normalize_bool(row.get("is_analysis_term"), default=True),
    }


def _split_term_key(term_key: str) -> tuple[str, int]:
    school_year_start, term_no = term_key.split("-")
    return f"{school_year_start}-{int(school_year_start) + 1}", int(term_no)


def _first_text(row: dict[str, Any], *keys: str) -> str | None:
    for key in keys:
        value = row.get(key)
        if value is None or isinstance(value, bool):
            continue
        text = str(value).strip()
        if text:
            return text
    return None


def _first_term_no(row: dict[str, Any]) -> int | str | None:
    value = row.get("term_no")
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    text = str(value).strip()
    if text in {"1", "2"}:
        return int(text)
    return None


def _normalize_date(raw: Any) -> str | None:
    if raw is None:
        return None
    if isinstance(raw, datetime):
        return raw.date().isoformat()
    if isinstance(raw, date):
        return raw.isoformat()
    text = str(raw).strip()
    return text or None


def _normalize_bool(raw: Any, default: bool) -> bool:
    if raw is None:
        return default
    if isinstance(raw, bool):
        return raw
    if isinstance(raw, int):
        return bool(raw)
    text = str(raw).strip().lower()
    if text in {"1", "true", "yes", "y", "是"}:
        return True
    if text in {"0", "false", "no", "n", "否"}:
        return False
    return default
