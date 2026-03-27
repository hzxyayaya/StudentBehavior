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


def build_warnings_payload(
    *,
    input_row_count: int,
    output_row_count: int,
    dropped_row_count: int,
    null_metric_summary: dict[str, int] | None = None,
    notes: Sequence[str] | None = None,
) -> dict[str, object]:
    if input_row_count < 0:
        raise ValueError("input_row_count must be non-negative")
    if output_row_count < 0:
        raise ValueError("output_row_count must be non-negative")
    if dropped_row_count < 0:
        raise ValueError("dropped_row_count must be non-negative")

    resolved_null_metric_summary = (
        {key: int(value) for key, value in null_metric_summary.items()}
        if null_metric_summary is not None
        else {column: 0 for column in _NULL_METRIC_COLUMNS}
    )
    resolved_notes = list(notes) if notes is not None else ["build completed"]

    return {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
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
    )
