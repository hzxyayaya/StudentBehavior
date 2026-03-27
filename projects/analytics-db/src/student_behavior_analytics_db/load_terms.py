from __future__ import annotations

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

_TERM_COMBINED_KEYS = (
    "term_name",
    "term_key",
    "学年学期",
    "学年学期名称",
    "学期名称",
    "xnxq",
    "XNXQ",
)

_TERM_SCHOOL_YEAR_KEYS = (
    "school_year",
    "学年",
    "学年度",
    "开课学年",
    "XN",
    "xn",
)

_TERM_NO_KEYS = (
    "term_no",
    "学期",
    "学期序号",
    "开课学期",
    "XQ",
    "xq",
)

_TERM_DATE_KEYS = {
    "start_date": ("start_date", "起始日期", "开始日期"),
    "end_date": ("end_date", "结束日期", "终止日期"),
}

_TERM_BOOL_KEYS = ("is_analysis_term", "是否分析学期", "分析学期")


def load_terms(rows: list[dict[str, Any]]) -> pd.DataFrame:
    records = []
    for row in rows:
        record = _build_term_record(row)
        if record is not None:
            records.append(record)
    if not records:
        return pd.DataFrame(columns=_TERM_COLUMNS)
    frame = pd.DataFrame(records, columns=_TERM_COLUMNS)
    frame = frame.drop_duplicates(subset=["term_key"], keep="first", ignore_index=True)
    return frame.astype(object).where(pd.notna(frame), None)


def _build_term_record(row: dict[str, Any]) -> dict[str, Any] | None:
    combined_term = _first_text(row, *_TERM_COMBINED_KEYS)
    school_year = _first_text(row, *_TERM_SCHOOL_YEAR_KEYS)
    term_no = _first_term_no(row)

    term_key = None
    term_name = None

    if combined_term is not None:
        term_key = _normalize_combined_term_key(combined_term)
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
        "start_date": _normalize_date(_first_value(row, *_TERM_DATE_KEYS["start_date"])),
        "end_date": _normalize_date(_first_value(row, *_TERM_DATE_KEYS["end_date"])),
        "is_analysis_term": _normalize_bool(_first_value(row, *_TERM_BOOL_KEYS), default=True),
    }


def _split_term_key(term_key: str) -> tuple[str, int]:
    school_year_start, term_no = term_key.split("-")
    return f"{school_year_start}-{int(school_year_start) + 1}", int(term_no)


def _first_text(row: dict[str, Any], *keys: str) -> str | None:
    for key in keys:
        if key not in row:
            continue
        value = row.get(key)
        if value is None or isinstance(value, bool):
            continue
        text = str(value).strip()
        if text:
            return text
    return None


def _first_term_no(row: dict[str, Any]) -> int | str | None:
    value = _first_value(row, *_TERM_NO_KEYS)
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    text = str(value).strip()
    if text in {"1", "2"}:
        return int(text)
    return None


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


def _normalize_combined_term_key(raw: object) -> str | None:
    if raw is None or isinstance(raw, bool):
        return None
    text = str(raw).strip()
    if not text:
        return None
    direct = normalize_term_key(text, None)
    if direct is not None:
        return direct

    text = text.replace("第", "").replace("学期", "")
    if "学年" in text and "学期" not in text:
        return None
    for separator in ("-", "—", "–", "~", "～", "至"):
        if separator in text:
            parts = text.split(separator)
            if len(parts) == 3 and parts[2] in {"1", "2"}:
                school_year = f"{parts[0]}-{parts[1]}"
                return normalize_term_key(school_year, parts[2])
    return None
