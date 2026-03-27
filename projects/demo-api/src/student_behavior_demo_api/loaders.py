from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import pandas as pd

STUDENT_RESULTS_REQUIRED_COLUMNS = {
    "student_id",
    "term_key",
    "student_name",
    "major_name",
    "quadrant_label",
    "risk_probability",
    "risk_level",
    "dimension_scores_json",
}

OVERVIEW_REQUIRED_KEYS = {
    "term_buckets",
    "student_count",
    "risk_distribution",
    "quadrant_distribution",
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
    # Overview payloads are expected to include the key summary blocks used by the API.
    _ensure_required_keys(payload, OVERVIEW_REQUIRED_KEYS)
    return payload


def validate_model_summary_payload(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    _ensure_required_keys(payload, MODEL_SUMMARY_REQUIRED_KEYS)
    return payload
