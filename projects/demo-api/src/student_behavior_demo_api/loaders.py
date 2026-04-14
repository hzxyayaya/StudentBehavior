from __future__ import annotations

import json
import sqlite3
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import pandas as pd

STUDENT_RESULTS_REQUIRED_COLUMNS = {
    "student_id",
    "term_key",
    "student_name",
    "major_name",
    "group_segment",
    "risk_probability",
    "risk_level",
    "dimension_scores_json",
}

OVERVIEW_REQUIRED_KEYS = {
    "term_buckets",
}
OVERVIEW_TERM_SUMMARY_REQUIRED_KEYS = {
    "student_count",
    "risk_distribution",
    "group_distribution",
    "major_risk_summary",
    "trend_summary",
}
MODEL_SUMMARY_REQUIRED_KEYS = {
    "cluster_method",
    "risk_model",
    "target_label",
    "auc",
    "updated_at",
}


def _missing_required_keys(payload: Mapping[str, Any], required_keys: set[str]) -> list[str]:
    return sorted(key for key in required_keys if key not in payload)


def _ensure_required_keys(payload: Mapping[str, Any], required_keys: set[str]) -> None:
    missing_keys = _missing_required_keys(payload, required_keys)
    if missing_keys:
        raise ValueError(f"missing required keys: {', '.join(missing_keys)}")


def validate_student_results_columns(frame: pd.DataFrame) -> pd.DataFrame:
    missing_columns = sorted(STUDENT_RESULTS_REQUIRED_COLUMNS - set(frame.columns))
    if missing_columns:
        raise ValueError(f"missing required columns: {', '.join(missing_columns)}")
    return frame


def load_student_results(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)
    frame = pd.read_csv(path)
    return validate_student_results_columns(frame)


def load_json_records(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(path)

    if path.suffix.lower() == ".jsonl":
        records: list[dict[str, Any]] = []
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line:
                continue
            record = json.loads(line)
            if not isinstance(record, dict):
                raise ValueError("jsonl records must be objects")
            records.append(record)
        return records

    if path.suffix.lower() == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, list):
            records = payload
        elif isinstance(payload, dict):
            records = [payload]
        else:
            raise ValueError("json payload must be an object or array")

        validated_records: list[dict[str, Any]] = []
        for record in records:
            if not isinstance(record, dict):
                raise ValueError("json records must be objects")
            validated_records.append(record)
        return validated_records

    raise ValueError(f"unsupported JSON format: {path.suffix}")


def validate_overview_payload(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    _ensure_required_keys(payload, OVERVIEW_REQUIRED_KEYS)
    term_buckets = payload.get("term_buckets")
    if not isinstance(term_buckets, Mapping):
        raise ValueError("term_buckets must be a mapping")

    for term_key, term_summary in term_buckets.items():
        if not isinstance(term_summary, Mapping):
            raise ValueError(f"term bucket {term_key!r} must be a mapping")
        _ensure_required_keys(term_summary, OVERVIEW_TERM_SUMMARY_REQUIRED_KEYS)
    return payload


def validate_model_summary_payload(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    _ensure_required_keys(payload, MODEL_SUMMARY_REQUIRED_KEYS)
    return payload


def load_runtime_single_payload(
    sqlite_path: Path,
    *,
    table_name: str,
    key_column: str = "summary_key",
    key_value: str = "current",
) -> dict[str, Any] | None:
    row = _load_runtime_payload_rows(
        sqlite_path,
        query=f"select payload_json from {table_name} where {key_column} = ?",
        parameters=(key_value,),
    )
    if not row:
        return None
    payload = row[0]
    if not isinstance(payload, dict):
        return None
    return payload


def load_runtime_payload_rows(
    sqlite_path: Path,
    *,
    table_name: str,
    order_by: str | None = None,
) -> list[dict[str, Any]]:
    query = f"select payload_json from {table_name}"
    if order_by:
        query += f" order by {order_by}"
    return _load_runtime_payload_rows(sqlite_path, query=query, parameters=())


def _load_runtime_payload_rows(
    sqlite_path: Path,
    *,
    query: str,
    parameters: tuple[object, ...],
) -> list[dict[str, Any]]:
    if not sqlite_path.exists():
        return []

    connection = sqlite3.connect(str(sqlite_path))
    try:
        raw_rows = connection.execute(query, parameters).fetchall()
    except sqlite3.DatabaseError:
        return []
    finally:
        connection.close()

    payload_rows: list[dict[str, Any]] = []
    for raw_row in raw_rows:
        if not raw_row or not raw_row[0]:
            continue
        try:
            payload = json.loads(str(raw_row[0]))
        except json.JSONDecodeError:
            return []
        if not isinstance(payload, dict):
            return []
        payload_rows.append(payload)
    return payload_rows
