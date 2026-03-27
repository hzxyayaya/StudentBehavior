from __future__ import annotations

from datetime import date, datetime, time
import re
from typing import Any, Iterable

import pandas as pd

from .normalize_ids import normalize_student_id
from .normalize_terms import normalize_term_key

_TASK_COLUMNS = (
    "student_id",
    "term_key",
    "user_id",
    "user_name",
    "department_name",
    "major_name",
    "class_name",
    "state",
    "school_year",
    "course_id",
    "course_name",
    "jwcourse_id",
    "created_at",
    "course_type",
    "course_status",
    "course_delete",
    "clazz_id",
    "clazz_name",
    "clazz_status",
    "clazz_state",
    "job_num",
    "job_rate",
    "videojob_num",
    "videojob_rate",
    "videojob_time",
    "test_num",
    "test_rate",
    "test_avgscore",
    "work_num",
    "work_rate",
    "work_avgscore",
    "exam_num",
    "exam_rate",
    "exam_avgscore",
    "pv",
    "sign_num",
    "sign_rate",
    "course_live_time",
    "special_time",
    "bbs_num",
    "topic_num",
    "reply_num",
    "points",
    "task_num",
    "task_rate",
    "updated_at",
    "inserted_at",
    "source_file",
    "source_row_hash",
)

_STUDENT_ID_KEYS = (
    "student_id",
    "LOGIN_NAME",
    "USERNUM",
    "USER_ID",
    "XH",
    "XSBH",
    "SID",
)

_TERM_YEAR_KEYS = ("XN", "xn", "school_year", "学年", "学年度", "开课学年")
_TERM_NO_KEYS = ("XQ", "xq", "term_no", "学期", "学期序号", "开课学期")
_COMBINED_TERM_KEYS = ("term_key", "学年学期", "学年学期名称", "学期名称", "xnxq", "XNXQ")
_STANDARD_TERM_KEY_RE = re.compile(r"^\d{4}-[12]$")


def load_fact_tasks(
    rows: list[dict[str, Any]], terms: Iterable[dict[str, Any]] | pd.DataFrame | None = None
) -> pd.DataFrame:
    # Draft source: raw workbook event times are currently time-only, so this loader
    # only guarantees staged rows with an explicit term key or a caller-supplied term calendar.
    term_calendar = _build_term_calendar(terms)
    records = []
    for row in rows:
        student_id = _pick_student_id(row)
        created_at = _normalize_timestamp(
            _first_value(row, "CREATE_TIME", "UPDATE_TIME", "INSERT_TIME")
        )
        term_key = _pick_term_key(row, created_at, term_calendar)
        source_file = _normalize_text(_first_value(row, "source_file", "源文件"))
        source_row_hash = _normalize_text(_first_value(row, "source_row_hash", "row_hash"))
        if (
            student_id is None
            or term_key is None
            or created_at is None
            or source_file is None
            or source_row_hash is None
        ):
            continue

        records.append(
            {
                "student_id": student_id,
                "term_key": term_key,
                "user_id": _normalize_number(_first_value(row, "USER_ID", "user_id")),
                "user_name": _normalize_text(_first_value(row, "USER_NAME", "user_name")),
                "department_name": _normalize_text(
                    _first_value(row, "DEPARTMENT_NAME", "department_name")
                ),
                "major_name": _normalize_text(_first_value(row, "MAJOR_NAME", "major_name")),
                "class_name": _normalize_text(_first_value(row, "CLASS_NAME", "class_name")),
                "state": _normalize_number(_first_value(row, "STATE", "state")),
                "school_year": _normalize_number(_first_value(row, "SCHOOL_YEAR", "school_year")),
                "course_id": _normalize_number(_first_value(row, "COURSE_ID", "course_id")),
                "course_name": _normalize_text(_first_value(row, "COURSE_NAME", "course_name")),
                "jwcourse_id": _normalize_text(_first_value(row, "JWCOURSE_ID", "jwcourse_id")),
                "created_at": created_at,
                "course_type": _normalize_number(_first_value(row, "COURSE_TYPE", "course_type")),
                "course_status": _normalize_number(_first_value(row, "COURSE_STATUS", "course_status")),
                "course_delete": _normalize_number(_first_value(row, "COURSE_DELETE", "course_delete")),
                "clazz_id": _normalize_number(_first_value(row, "CLAZZ_ID", "clazz_id")),
                "clazz_name": _normalize_text(_first_value(row, "CLAZZ_NAME", "clazz_name")),
                "clazz_status": _normalize_number(_first_value(row, "CLAZZ_STATUS", "clazz_status")),
                "clazz_state": _normalize_number(_first_value(row, "CLAZZ_STATE", "clazz_state")),
                "job_num": _normalize_number(_first_value(row, "JOB_NUM", "job_num")),
                "job_rate": _normalize_number(_first_value(row, "JOB_RATE", "job_rate")),
                "videojob_num": _normalize_number(_first_value(row, "VIDEOJOB_NUM", "videojob_num")),
                "videojob_rate": _normalize_number(_first_value(row, "VIDEOJOB_RATE", "videojob_rate")),
                "videojob_time": _normalize_number(_first_value(row, "VIDEOJOB_TIME", "videojob_time")),
                "test_num": _normalize_number(_first_value(row, "TEST_NUM", "test_num")),
                "test_rate": _normalize_number(_first_value(row, "TEST_RATE", "test_rate")),
                "test_avgscore": _normalize_number(_first_value(row, "TEST_AVGSCORE", "test_avgscore")),
                "work_num": _normalize_number(_first_value(row, "WORK_NUM", "work_num")),
                "work_rate": _normalize_number(_first_value(row, "WORK_RATE", "work_rate")),
                "work_avgscore": _normalize_number(_first_value(row, "WORK_AVGSCORE", "work_avgscore")),
                "exam_num": _normalize_number(_first_value(row, "EXAM_NUM", "exam_num")),
                "exam_rate": _normalize_number(_first_value(row, "EXAM_RATE", "exam_rate")),
                "exam_avgscore": _normalize_number(_first_value(row, "EXAM_AVGSCORE", "exam_avgscore")),
                "pv": _normalize_number(_first_value(row, "PV", "pv")),
                "sign_num": _normalize_number(_first_value(row, "SIGN_NUM", "sign_num")),
                "sign_rate": _normalize_number(_first_value(row, "SIGN_RATE", "sign_rate")),
                "course_live_time": _normalize_number(
                    _first_value(row, "COURSE_LIVE_TIME", "course_live_time")
                ),
                "special_time": _normalize_number(_first_value(row, "SPECIAL_TIME", "special_time")),
                "bbs_num": _normalize_number(_first_value(row, "BBS_NUM", "bbs_num")),
                "topic_num": _normalize_number(_first_value(row, "TOPIC_NUM", "topic_num")),
                "reply_num": _normalize_number(_first_value(row, "REPLY_NUM", "reply_num")),
                "points": _normalize_number(_first_value(row, "POINTS", "points")),
                "task_num": _normalize_number(_first_value(row, "TASK_NUM", "task_num")),
                "task_rate": _normalize_number(_first_value(row, "TASK_RATE", "task_rate")),
                "updated_at": _normalize_timestamp(_first_value(row, "UPDATE_TIME", "updated_at")),
                "inserted_at": _normalize_timestamp(_first_value(row, "INSERT_TIME", "inserted_at")),
                "source_file": source_file,
                "source_row_hash": source_row_hash,
            }
        )

    return _as_frame(records, _TASK_COLUMNS)


def _pick_student_id(row: dict[str, Any]) -> str | None:
    for key in _STUDENT_ID_KEYS:
        student_id = normalize_student_id(row.get(key))
        if student_id is not None:
            return student_id
    return None


def _pick_term_key(
    row: dict[str, Any], created_at: str | None, term_calendar: list[dict[str, Any]]
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

    return _term_key_from_calendar(created_at, term_calendar)


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


def _term_key_from_calendar(created_at: str | None, term_calendar: list[dict[str, Any]]) -> str | None:
    if created_at is None or not term_calendar:
        return None
    try:
        created_date = pd.to_datetime(created_at, errors="coerce").date()
    except (TypeError, ValueError, AttributeError):
        return None
    if pd.isna(created_date):
        return None

    matches = []
    for term in term_calendar:
        start_date = pd.to_datetime(term["start_date"], errors="coerce")
        end_date = pd.to_datetime(term["end_date"], errors="coerce")
        if pd.isna(start_date) or pd.isna(end_date):
            continue
        if start_date.date() <= created_date <= end_date.date():
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
    return text or None


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


def _normalize_number(raw: Any) -> float | int | None:
    if raw is None or isinstance(raw, bool):
        return None
    if isinstance(raw, float) and raw != raw:
        return None
    if isinstance(raw, (int, float)):
        if isinstance(raw, float) and raw.is_integer():
            return int(raw)
        return raw
    text = str(raw).strip()
    if not text:
        return None
    try:
        number = float(text)
    except ValueError:
        return None
    if number.is_integer():
        return int(number)
    return number


def _as_frame(records: list[dict[str, Any]], columns: tuple[str, ...]) -> pd.DataFrame:
    if not records:
        return pd.DataFrame(columns=columns)
    frame = pd.DataFrame(records, columns=columns)
    return frame.astype(object).where(pd.notna(frame), None)
