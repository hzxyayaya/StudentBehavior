from __future__ import annotations

from datetime import date, datetime, time
import re
from typing import Any, Iterable

import pandas as pd

from .normalize_ids import normalize_student_id
from .normalize_terms import infer_term_from_month_only
from .normalize_terms import normalize_term_key

_LIBRARY_COLUMNS = (
    "student_id",
    "term_key",
    "visited_at",
    "visit_date",
    "source_file",
    "source_row_hash",
)

_STUDENT_ID_KEYS = ("student_id", "cardld", "cardid", "CARDID", "LOGIN_NAME", "USERNUM", "XH")
_COMBINED_TERM_KEYS = ("term_key", "学年学期", "学年学期名称", "学期名称", "xnxq", "XNXQ")
_TERM_YEAR_KEYS = ("XN", "xn", "school_year", "学年", "学年度", "开课学年")
_TERM_NO_KEYS = ("XQ", "xq", "term_no", "学期", "学期序号", "开课学期")
_STANDARD_TERM_KEY_RE = re.compile(r"^\d{4}-[12]$")


def load_fact_library(
    rows: list[dict[str, Any]], terms: Iterable[dict[str, Any]] | pd.DataFrame | None = None
) -> pd.DataFrame:
    term_calendar = _build_term_calendar(terms)
    records = []
    for row in rows:
        student_id = _pick_student_id(row)
        visited_at = _normalize_timestamp(_first_value(row, "visittime", "visit_time", "VISITTIME"))
        term_key = _pick_term_key(row, visited_at, term_calendar)
        source_file = _normalize_text(_first_value(row, "source_file", "源文件"))
        source_row_hash = _normalize_text(_first_value(row, "source_row_hash", "row_hash"))
        if (
            student_id is None
            or term_key is None
            or visited_at is None
            or source_file is None
            or source_row_hash is None
        ):
            continue

        records.append(
            {
                "student_id": student_id,
                "term_key": term_key,
                "visited_at": visited_at,
                "visit_date": visited_at[:10],
                "source_file": source_file,
                "source_row_hash": source_row_hash,
            }
        )

    return _as_frame(records, _LIBRARY_COLUMNS)


def _pick_student_id(row: dict[str, Any]) -> str | None:
    for key in _STUDENT_ID_KEYS:
        student_id = normalize_student_id(row.get(key))
        if student_id is not None:
            return student_id
    return None


def _pick_term_key(
    row: dict[str, Any], visited_at: str | None, term_calendar: list[dict[str, Any]]
) -> str | None:
    direct_term_key = _normalize_term_key_value(_first_value(row, "term_key"))
    if direct_term_key is not None:
        return direct_term_key

    for key in _COMBINED_TERM_KEYS:
        if key == "term_key":
            continue
        if key in row:
            direct_term_key = _normalize_term_key_value(row.get(key))
            if direct_term_key is not None:
                return direct_term_key

    raw_year = _first_value(row, *_TERM_YEAR_KEYS)
    raw_term = _first_value(row, *_TERM_NO_KEYS)
    if raw_year is not None and raw_term is not None:
        term_key = normalize_term_key(raw_year, raw_term)
        if term_key is not None:
            return term_key

    return _term_key_from_calendar(visited_at, term_calendar) or infer_term_from_month_only(visited_at)


def _normalize_term_key_value(raw: Any) -> str | None:
    if raw is None or isinstance(raw, bool):
        return None
    text = str(raw).strip()
    if not text:
        return None
    if _STANDARD_TERM_KEY_RE.fullmatch(text):
        return text
    return normalize_term_key(text, None)


def _build_term_calendar(
    terms: Iterable[dict[str, Any]] | pd.DataFrame | None,
) -> list[dict[str, Any]]:
    if terms is None:
        return []
    if isinstance(terms, pd.DataFrame):
        rows = terms.to_dict(orient="records")
    else:
        rows = list(terms)

    calendar: list[dict[str, Any]] = []
    for row in rows:
        term_key = _normalize_term_key_value(_first_value(row, "term_key"))
        if term_key is None:
            continue
        start_date = _normalize_date(_first_value(row, "start_date", "起始日期", "开始日期"))
        end_date = _normalize_date(_first_value(row, "end_date", "结束日期", "终止日期"))
        if start_date is None or end_date is None:
            continue
        calendar.append({"term_key": term_key, "start_date": start_date, "end_date": end_date})
    return calendar


def _term_key_from_calendar(visited_at: str | None, term_calendar: list[dict[str, Any]]) -> str | None:
    if visited_at is None or not term_calendar:
        return None
    try:
        visited_date = pd.to_datetime(visited_at, errors="coerce").date()
    except (TypeError, ValueError, AttributeError):
        return None
    if pd.isna(visited_date):
        return None

    matches = []
    for term in term_calendar:
        start_date = pd.to_datetime(term["start_date"], errors="coerce")
        end_date = pd.to_datetime(term["end_date"], errors="coerce")
        if pd.isna(start_date) or pd.isna(end_date):
            continue
        if start_date.date() <= visited_date <= end_date.date():
            matches.append(term["term_key"])

    if len(matches) == 1:
        return matches[0]
    return None


def _normalize_timestamp(raw: Any) -> str | None:
    if raw is None or isinstance(raw, bool):
        return None
    if isinstance(raw, time):
        return None
    if isinstance(raw, float) and raw != raw:
        return None
    try:
        parsed = pd.to_datetime(raw, errors="coerce")
    except (TypeError, ValueError, OverflowError):
        return None
    if pd.isna(parsed):
        return None
    return pd.Timestamp(parsed).strftime("%Y-%m-%d %H:%M:%S")


def _normalize_date(raw: Any) -> str | None:
    if raw is None or isinstance(raw, bool):
        return None
    if isinstance(raw, float) and raw != raw:
        return None
    if isinstance(raw, (datetime, date)):
        return raw.date().isoformat() if isinstance(raw, datetime) else raw.isoformat()
    text = str(raw).strip()
    if not text:
        return None
    parsed = pd.to_datetime(text, errors="coerce")
    if pd.isna(parsed):
        return None
    return pd.Timestamp(parsed).date().isoformat()


def _first_value(row: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key not in row:
            continue
        value = row.get(key)
        if value is None or isinstance(value, bool):
            continue
        if isinstance(value, float) and value != value:
            continue
        if isinstance(value, str):
            text = value.strip()
            if text:
                return text
            continue
        return value
    return None


def _normalize_text(raw: Any) -> str | None:
    if raw is None or isinstance(raw, bool):
        return None
    if isinstance(raw, float) and raw != raw:
        return None
    text = str(raw).strip()
    return text or None


def _as_frame(records: list[dict[str, Any]], columns: tuple[str, ...]) -> pd.DataFrame:
    if not records:
        return pd.DataFrame(columns=columns)
    frame = pd.DataFrame(records, columns=columns)
    return frame.astype(object).where(pd.notna(frame), None)
