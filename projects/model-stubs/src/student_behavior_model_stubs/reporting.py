from __future__ import annotations

from datetime import datetime, timezone
from collections.abc import Sequence

import pandas as pd

_NULL_METRIC_COLUMNS = (
    "avg_course_score",
    "failed_course_count",
    "attendance_normal_rate",
    "sign_event_count",
    "selected_course_count",
    "library_visit_count",
)


def _count_nulls(frame: pd.DataFrame, column: str) -> int:
    if column not in frame.columns:
        return 0
    return int(frame[column].isna().sum())


def _format_generated_at(now: datetime | None) -> str:
    timestamp = now if now is not None else datetime.now(timezone.utc)
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)
    return timestamp.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _build_null_metric_summary(null_metric_summary: dict[str, int] | None) -> dict[str, int]:
    summary = {column: 0 for column in _NULL_METRIC_COLUMNS}
    if null_metric_summary is None:
        return summary

    for column in _NULL_METRIC_COLUMNS:
        summary[column] = int(null_metric_summary.get(column, 0))
    return summary


def build_warnings_payload(
    *,
    input_row_count: int,
    output_row_count: int,
    dropped_row_count: int,
    null_metric_summary: dict[str, int] | None = None,
    notes: Sequence[str] | None = None,
    now: datetime | None = None,
) -> dict[str, object]:
    if input_row_count < 0:
        raise ValueError("input_row_count must be non-negative")
    if output_row_count < 0:
        raise ValueError("output_row_count must be non-negative")
    if dropped_row_count < 0:
        raise ValueError("dropped_row_count must be non-negative")

    resolved_null_metric_summary = _build_null_metric_summary(null_metric_summary)
    resolved_notes = list(notes) if notes is not None else ["build completed"]

    return {
        "generated_at": _format_generated_at(now),
        "input_row_count": int(input_row_count),
        "output_row_count": int(output_row_count),
        "dropped_row_count": int(dropped_row_count),
        "null_metric_summary": resolved_null_metric_summary,
        "notes": resolved_notes,
    }


def build_warnings_from_features(
    features: pd.DataFrame,
    *,
    output_row_count: int,
    dropped_row_count: int,
    notes: Sequence[str] | None = None,
    now: datetime | None = None,
) -> dict[str, object]:
    null_metric_summary = {
        column: _count_nulls(features, column) for column in _NULL_METRIC_COLUMNS
    }
    return build_warnings_payload(
        input_row_count=int(len(features)),
        output_row_count=output_row_count,
        dropped_row_count=dropped_row_count,
        null_metric_summary=null_metric_summary,
        notes=notes,
        now=now,
    )
