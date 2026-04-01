from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from typing import Any

import pandas as pd

from .normalize_ids import normalize_student_id
from .normalize_terms import normalize_term_key

_LABEL_COLUMNS = (
    "student_id",
    "term_key",
    "risk_label",
    "evaluation_source",
    "source_file",
    "source_row_hash",
)

_STUDENT_ID_KEYS = ("student_id", "XH", "XSBH", "LOGIN_NAME", "USERNUM", "SID")
_TERM_YEAR_KEYS = ("XN", "xn", "school_year", "PDXN", "CPXN")
_TERM_NO_KEYS = ("XQ", "xq", "term_no", "PDXQ", "CPXQ")
_COMBINED_TERM_KEYS = ("term_key", "xnxq", "XNXQ")
_STANDARD_TERM_KEY_RE = re.compile(r"^\d{4}-[12]$")


def load_fact_evaluation_labels(rows: list[dict[str, Any]]) -> pd.DataFrame:
    records = []
    for row in rows:
        student_id = _pick_student_id(row)
        cpxq = _normalize_text(_first_value(row, "CPXQ", "PDXQ", "cpxq"))
        source_file = _normalize_text(_first_value(row, "source_file"))
        source_row_hash = _normalize_text(_first_value(row, "source_row_hash", "row_hash"))
        if student_id is None or cpxq is None or source_file is None or source_row_hash is None:
            continue

        term_key, evaluation_source = _term_key_and_source(row, cpxq)
        if term_key is None or evaluation_source is None:
            continue

        risk_label = _risk_label(row)
        if risk_label is None:
            continue

        records.append(
            {
                "student_id": student_id,
                "term_key": term_key,
                "risk_label": risk_label,
                "evaluation_source": evaluation_source,
                "source_file": source_file,
                "source_row_hash": source_row_hash,
            }
        )

    return _as_frame(records, _LABEL_COLUMNS)


def _term_key_and_source(row: dict[str, Any], cpxq: str) -> tuple[str | None, str | None]:
    if cpxq == "9":
        return "annual_or_unknown_term", "annual_or_unknown_term"

    direct_term_key = _normalize_term_key_value(_first_value(row, "term_key"))
    if direct_term_key is not None:
        return direct_term_key, f"supervised_term_{cpxq}"

    for key in _COMBINED_TERM_KEYS:
        if key == "term_key":
            continue
        if key in row:
            direct_term_key = _normalize_term_key_value(row.get(key))
            if direct_term_key is not None:
                return direct_term_key, f"supervised_term_{cpxq}"

    raw_year = _first_value(row, *_TERM_YEAR_KEYS)
    raw_term = _first_value(row, *_TERM_NO_KEYS)
    if raw_year is None or raw_term is None:
        return None, None

    term_key = normalize_term_key(raw_year, raw_term)
    if term_key is None:
        return None, None

    return term_key, f"supervised_term_{cpxq}"


def _risk_label(row: dict[str, Any]) -> int | None:
    rank = _normalize_decimal(_first_value(row, "ZYNJPM", "major_grade_rank"))
    total = _normalize_decimal(_first_value(row, "ZYNJRS", "major_grade_total"))
    if rank is None or total is None or total == 0:
        return None
    major_grade_rank_pct = rank / total
    return 1 if major_grade_rank_pct >= Decimal("0.80") else 0


def _pick_student_id(row: dict[str, Any]) -> str | None:
    for key in _STUDENT_ID_KEYS:
        student_id = normalize_student_id(row.get(key))
        if student_id is not None:
            return student_id
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


def _normalize_text(raw: Any) -> str | None:
    if raw is None or isinstance(raw, bool):
        return None
    if isinstance(raw, float) and raw != raw:
        return None
    text = str(raw).strip()
    return text or None


def _normalize_term_key_value(raw: Any) -> str | None:
    if raw is None or isinstance(raw, bool):
        return None
    text = str(raw).strip()
    if not text:
        return None
    if _STANDARD_TERM_KEY_RE.fullmatch(text):
        return text
    return normalize_term_key(text, None)


def _normalize_decimal(raw: Any) -> Decimal | None:
    if raw is None or isinstance(raw, bool):
        return None
    if isinstance(raw, Decimal):
        return raw
    if isinstance(raw, float) and raw != raw:
        return None
    if isinstance(raw, (int, float)):
        return Decimal(str(raw))
    text = str(raw).strip()
    if not text:
        return None
    try:
        return Decimal(text)
    except (InvalidOperation, ValueError):
        return None


def _as_frame(records: list[dict[str, Any]], columns: tuple[str, ...]) -> pd.DataFrame:
    if not records:
        return pd.DataFrame(columns=columns)
    frame = pd.DataFrame(records, columns=columns)
    return frame.astype(object).where(pd.notna(frame), None)
