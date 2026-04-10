from __future__ import annotations

from datetime import time
from typing import Any

import pandas as pd

_FEATURE_COLUMNS = (
    "student_id",
    "term_key",
    "major_name",
    "college_name",
    "avg_course_score",
    "failed_course_count",
    "avg_gpa",
    "major_rank_pct",
    "risk_label",
    "risk_label_binary",
    "risk_label_level",
    "label_source",
    "label_rule_version",
    "attendance_record_count",
    "attendance_normal_rate",
    "selected_course_count",
    "sign_event_count",
    "assignment_submit_count",
    "exam_submit_count",
    "task_participation_rate",
    "discussion_reply_count",
    "library_visit_count",
    "library_active_days",
    "running_punch_count",
    "morning_activity_rate",
)

_PRESENT_ATTENDANCE_STATUSES = {"present", "normal", "on_time", "出勤", "正常"}
_LABEL_SOURCE = "academic_rule_v1"
_LABEL_RULE_VERSION = "2026-04-risk-v1"
_HIGH_RISK_LEVEL = "高风险"
_ELEVATED_RISK_LEVEL = "较高风险"
_GENERAL_RISK_LEVEL = "一般风险"
_LOW_RISK_LEVEL = "低风险"


def build_student_term_features(
    *,
    students: pd.DataFrame | None = None,
    terms: pd.DataFrame | None = None,
    grades: pd.DataFrame | None = None,
    attendance: pd.DataFrame | None = None,
    enrollments: pd.DataFrame | None = None,
    signins: pd.DataFrame | None = None,
    assignments: pd.DataFrame | None = None,
    exams: pd.DataFrame | None = None,
    tasks: pd.DataFrame | None = None,
    discussions: pd.DataFrame | None = None,
    library: pd.DataFrame | None = None,
    running: pd.DataFrame | None = None,
    evaluation_labels: pd.DataFrame | None = None,
) -> pd.DataFrame:
    keys = _collect_keys(
        grades,
        attendance,
        enrollments,
        signins,
        assignments,
        exams,
        tasks,
        discussions,
        library,
        running,
        evaluation_labels,
    )
    if keys.empty:
        return pd.DataFrame(columns=_FEATURE_COLUMNS)

    features = keys.copy()

    student_lookup = _prepare_lookup(students, "student_id", ["major_name", "college_name"])
    if not student_lookup.empty:
        features = features.merge(student_lookup, on="student_id", how="left")
    else:
        features["major_name"] = None
        features["college_name"] = None

    grade_metrics = _aggregate_grades(grades)
    features = _merge_metrics(features, grade_metrics)

    attendance_metrics = _aggregate_attendance(attendance)
    features = _merge_metrics(features, attendance_metrics)

    simple_counts = [
        _aggregate_count(enrollments, "selected_course_count", ["course_id", "course_code", "source_row_hash"]),
        _aggregate_count(signins, "sign_event_count", ["signed_in_at", "source_row_hash"]),
        _aggregate_count(assignments, "assignment_submit_count", ["work_id", "source_row_hash"]),
        _aggregate_count(exams, "exam_submit_count", ["work_id", "source_row_hash"]),
        _aggregate_count(discussions, "discussion_reply_count", ["source_row_hash", "topic_id", "created_at"]),
        _aggregate_count(library, "library_visit_count", ["source_row_hash", "visited_at"]),
        _aggregate_count(running, "running_punch_count", ["source_row_hash", "ran_at"]),
    ]
    for metric_frame in simple_counts:
        features = _merge_metrics(features, metric_frame)

    task_metrics = _aggregate_tasks(tasks)
    features = _merge_metrics(features, task_metrics)

    library_days_metrics = _aggregate_library_days(library)
    features = _merge_metrics(features, library_days_metrics)

    morning_metrics = _aggregate_morning_activity(running)
    features = _merge_metrics(features, morning_metrics)

    risk_metrics = _aggregate_risk_labels(evaluation_labels)
    features = _merge_metrics(features, risk_metrics)
    features = _add_explicit_risk_labels(features)

    features = _ensure_columns(features)
    return features.astype(object).where(pd.notna(features), None)


def _collect_keys(*frames: pd.DataFrame | None) -> pd.DataFrame:
    collected = []
    for frame in frames:
        if frame is None or frame.empty:
            continue
        if "student_id" not in frame.columns or "term_key" not in frame.columns:
            continue
        subset = frame.loc[:, ["student_id", "term_key"]].dropna(subset=["student_id", "term_key"])
        if not subset.empty:
            collected.append(subset)

    if not collected:
        return pd.DataFrame(columns=["student_id", "term_key"])

    keys = pd.concat(collected, ignore_index=True).drop_duplicates(ignore_index=True)
    return keys


def _prepare_lookup(
    frame: pd.DataFrame | None, key_column: str, value_columns: list[str]
) -> pd.DataFrame:
    if frame is None or frame.empty or key_column not in frame.columns:
        return pd.DataFrame(columns=[key_column, *value_columns])

    available = [column for column in value_columns if column in frame.columns]
    if not available:
        return pd.DataFrame(columns=[key_column, *value_columns])

    subset = frame.loc[:, [key_column, *available]].dropna(subset=[key_column])
    if subset.empty:
        return pd.DataFrame(columns=[key_column, *value_columns])

    subset = subset.drop_duplicates(subset=[key_column], keep="first", ignore_index=True)
    return subset


def _merge_metrics(features: pd.DataFrame, metrics: pd.DataFrame) -> pd.DataFrame:
    if metrics.empty:
        return features
    merged = features.merge(metrics, on=["student_id", "term_key"], how="left")
    return merged


def _aggregate_grades(frame: pd.DataFrame | None) -> pd.DataFrame:
    if frame is None or frame.empty or "student_id" not in frame.columns or "term_key" not in frame.columns:
        return pd.DataFrame(columns=["student_id", "term_key", "avg_course_score", "failed_course_count", "avg_gpa"])

    subset = frame.loc[:, [column for column in ["student_id", "term_key", "score", "gpa", "passed"] if column in frame.columns]].copy()
    subset = subset.dropna(subset=["student_id", "term_key"])
    if subset.empty:
        return pd.DataFrame(columns=["student_id", "term_key", "avg_course_score", "failed_course_count", "avg_gpa"])

    subset["score"] = pd.to_numeric(subset.get("score"), errors="coerce")
    subset["gpa"] = pd.to_numeric(subset.get("gpa"), errors="coerce")
    if "passed" in subset.columns:
        failed_mask = subset.apply(
            lambda row: _is_false_like(row["passed"]) if pd.notna(row["passed"]) else _is_score_failed(row["score"]),
            axis=1,
        )
    else:
        failed_mask = subset["score"].map(_is_score_failed)

    aggregated = (
        subset.groupby(["student_id", "term_key"], dropna=False)
        .agg(
            avg_course_score=("score", "mean"),
            failed_course_count=("score", lambda values: 0),
            avg_gpa=("gpa", "mean"),
        )
        .reset_index()
    )
    failed_counts = (
        subset.assign(_failed=failed_mask.fillna(False))
        .groupby(["student_id", "term_key"], dropna=False)["_failed"]
        .sum()
        .reset_index(name="failed_course_count")
    )
    aggregated = aggregated.drop(columns=["failed_course_count"]).merge(
        failed_counts, on=["student_id", "term_key"], how="left"
    )
    return aggregated


def _aggregate_attendance(frame: pd.DataFrame | None) -> pd.DataFrame:
    if frame is None or frame.empty or "student_id" not in frame.columns or "term_key" not in frame.columns:
        return pd.DataFrame(columns=["student_id", "term_key", "attendance_record_count", "attendance_normal_rate"])

    subset = frame.loc[
        :, [column for column in ["student_id", "term_key", "attendance_status"] if column in frame.columns]
    ].copy()
    subset = subset.dropna(subset=["student_id", "term_key"])
    if subset.empty:
        return pd.DataFrame(columns=["student_id", "term_key", "attendance_record_count", "attendance_normal_rate"])

    dedupe_columns = ["student_id", "term_key"]
    if "source_row_hash" in frame.columns:
        subset["source_row_hash"] = frame.loc[subset.index, "source_row_hash"]
        if subset["source_row_hash"].notna().any():
            dedupe_columns.append("source_row_hash")
    elif "attended_at" in frame.columns:
        subset["attended_at"] = frame.loc[subset.index, "attended_at"]
        dedupe_columns.append("attended_at")
        if "attendance_status" in subset.columns:
            dedupe_columns.append("attendance_status")
    subset = subset.drop_duplicates(subset=dedupe_columns, ignore_index=True)

    if "attendance_status" in subset.columns:
        subset["attendance_status"] = subset["attendance_status"].map(_normalize_text)
        has_status = True
    else:
        subset["attendance_status"] = None
        has_status = False
    grouped = subset.groupby(["student_id", "term_key"], dropna=False)
    totals = grouped.size().reset_index(name="attendance_record_count")
    if has_status:
        normal = grouped["attendance_status"].apply(
            lambda values: sum(_is_present_status(value) for value in values)
        ).reset_index(name="_normal_count")
        metrics = totals.merge(normal, on=["student_id", "term_key"], how="left")
        metrics["attendance_normal_rate"] = metrics.apply(
            lambda row: None if row["attendance_record_count"] == 0 else row["_normal_count"] / row["attendance_record_count"],
            axis=1,
        )
    else:
        metrics = totals.copy()
        metrics["attendance_normal_rate"] = None
    return metrics.loc[:, ["student_id", "term_key", "attendance_record_count", "attendance_normal_rate"]]


def _aggregate_count(
    frame: pd.DataFrame | None,
    metric_name: str,
    dedupe_candidates: list[str] | None = None,
) -> pd.DataFrame:
    if frame is None or frame.empty or "student_id" not in frame.columns or "term_key" not in frame.columns:
        return pd.DataFrame(columns=["student_id", "term_key", metric_name])

    selected_columns = ["student_id", "term_key"]
    if dedupe_candidates:
        selected_columns.extend([column for column in dedupe_candidates if column in frame.columns])

    subset = frame.loc[:, selected_columns].dropna(subset=["student_id", "term_key"])
    if subset.empty:
        return pd.DataFrame(columns=["student_id", "term_key", metric_name])

    dedupe_columns = [
        column
        for column in (dedupe_candidates or [])
        if column in subset.columns and subset[column].notna().any()
    ]
    if dedupe_columns:
        subset = subset.drop_duplicates(subset=["student_id", "term_key", *dedupe_columns], ignore_index=True)
    else:
        subset = subset.drop_duplicates(ignore_index=True)

    grouped = subset.groupby(["student_id", "term_key"], dropna=False).size().reset_index(name=metric_name)
    return grouped


def _aggregate_tasks(frame: pd.DataFrame | None) -> pd.DataFrame:
    if frame is None or frame.empty or "student_id" not in frame.columns or "term_key" not in frame.columns:
        return pd.DataFrame(columns=["student_id", "term_key", "task_participation_rate"])

    rate_column = "task_rate" if "task_rate" in frame.columns else "TASK_RATE" if "TASK_RATE" in frame.columns else None
    if rate_column is None:
        return pd.DataFrame(columns=["student_id", "term_key", "task_participation_rate"])

    subset = frame.loc[:, ["student_id", "term_key", rate_column]].dropna(subset=["student_id", "term_key"])
    if subset.empty:
        return pd.DataFrame(columns=["student_id", "term_key", "task_participation_rate"])

    subset[rate_column] = pd.to_numeric(subset[rate_column], errors="coerce")
    metrics = (
        subset.groupby(["student_id", "term_key"], dropna=False)[rate_column]
        .mean()
        .reset_index(name="task_participation_rate")
    )
    return metrics


def _aggregate_library_days(frame: pd.DataFrame | None) -> pd.DataFrame:
    if frame is None or frame.empty or "student_id" not in frame.columns or "term_key" not in frame.columns:
        return pd.DataFrame(columns=["student_id", "term_key", "library_active_days"])

    visit_date_column = "visit_date" if "visit_date" in frame.columns else None
    if visit_date_column is None and "visited_at" in frame.columns:
        visit_date_column = "visited_at"
    if visit_date_column is None:
        return pd.DataFrame(columns=["student_id", "term_key", "library_active_days"])

    subset = frame.loc[:, ["student_id", "term_key", visit_date_column]].dropna(subset=["student_id", "term_key"])
    if subset.empty:
        return pd.DataFrame(columns=["student_id", "term_key", "library_active_days"])

    if visit_date_column == "visited_at":
        subset[visit_date_column] = pd.to_datetime(subset[visit_date_column], errors="coerce").dt.date

    metrics = (
        subset.groupby(["student_id", "term_key"], dropna=False)[visit_date_column]
        .nunique(dropna=True)
        .reset_index(name="library_active_days")
    )
    return metrics


def _aggregate_morning_activity(frame: pd.DataFrame | None) -> pd.DataFrame:
    if frame is None or frame.empty or "student_id" not in frame.columns or "term_key" not in frame.columns:
        return pd.DataFrame(columns=["student_id", "term_key", "morning_activity_rate"])

    if "ran_at" not in frame.columns:
        return pd.DataFrame(columns=["student_id", "term_key", "morning_activity_rate"])

    subset = frame.loc[:, ["student_id", "term_key", "ran_at"]].dropna(subset=["student_id", "term_key"])
    if subset.empty:
        return pd.DataFrame(columns=["student_id", "term_key", "morning_activity_rate"])

    dedupe_columns = ["student_id", "term_key", "ran_at"]
    if "source_row_hash" in frame.columns:
        subset["source_row_hash"] = frame.loc[subset.index, "source_row_hash"]
        if subset["source_row_hash"].notna().any():
            dedupe_columns = ["student_id", "term_key", "source_row_hash"]
    subset = subset.drop_duplicates(subset=dedupe_columns, ignore_index=True)

    subset["ran_at"] = pd.to_datetime(subset["ran_at"], errors="coerce")
    subset = subset.dropna(subset=["ran_at"])
    if subset.empty:
        return pd.DataFrame(columns=["student_id", "term_key", "morning_activity_rate"])

    subset["_is_morning"] = subset["ran_at"].dt.time.map(lambda value: value < time(7, 0))
    grouped = subset.groupby(["student_id", "term_key"], dropna=False)
    metrics = grouped["_is_morning"].mean().reset_index(name="morning_activity_rate")
    return metrics


def _aggregate_risk_labels(frame: pd.DataFrame | None) -> pd.DataFrame:
    if frame is None or frame.empty or "student_id" not in frame.columns or "term_key" not in frame.columns:
        return pd.DataFrame(columns=["student_id", "term_key", "risk_label"])

    if "risk_label" not in frame.columns:
        return pd.DataFrame(columns=["student_id", "term_key", "risk_label"])

    subset = frame.loc[:, ["student_id", "term_key", "risk_label"]].dropna(subset=["student_id", "term_key"])
    if subset.empty:
        return pd.DataFrame(columns=["student_id", "term_key", "risk_label"])

    subset["risk_label"] = pd.to_numeric(subset["risk_label"], errors="coerce")
    metrics = (
        subset.groupby(["student_id", "term_key"], dropna=False)["risk_label"]
        .max()
        .reset_index()
    )
    return metrics


def _ensure_columns(frame: pd.DataFrame) -> pd.DataFrame:
    for column in _FEATURE_COLUMNS:
        if column not in frame.columns:
            frame[column] = None
    return frame.loc[:, _FEATURE_COLUMNS]


def _add_explicit_risk_labels(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return frame

    labels = frame.apply(_derive_explicit_risk_labels, axis=1, result_type="expand")
    labels.columns = ["risk_label_binary", "risk_label_level", "label_source", "label_rule_version"]
    enriched = frame.copy()
    for column in labels.columns:
        enriched[column] = labels[column]
    return enriched


def _derive_explicit_risk_labels(row: pd.Series) -> tuple[int | None, str | None, str | None, str | None]:
    failed_course_count = _coerce_number(row.get("failed_course_count"))
    avg_gpa = _coerce_number(row.get("avg_gpa"))
    avg_course_score = _coerce_number(row.get("avg_course_score"))
    evaluation_risk_label = _coerce_number(row.get("risk_label"))

    if all(
        value is None
        for value in (failed_course_count, avg_gpa, avg_course_score, evaluation_risk_label)
    ):
        return None, None, None, None

    risk_level = _derive_risk_level(
        failed_course_count=failed_course_count,
        avg_gpa=avg_gpa,
        avg_course_score=avg_course_score,
        evaluation_risk_label=evaluation_risk_label,
    )
    risk_label_binary = 1 if risk_level in {_HIGH_RISK_LEVEL, _ELEVATED_RISK_LEVEL} else 0
    return risk_label_binary, risk_level, _LABEL_SOURCE, _LABEL_RULE_VERSION


def _derive_risk_level(
    *,
    failed_course_count: float | None,
    avg_gpa: float | None,
    avg_course_score: float | None,
    evaluation_risk_label: float | None,
) -> str:
    if (failed_course_count is not None and failed_course_count >= 2) or (
        avg_gpa is not None and avg_gpa < 1.5
    ):
        return _HIGH_RISK_LEVEL

    if (evaluation_risk_label is not None and evaluation_risk_label >= 1) or (
        avg_gpa is not None and avg_gpa < 2.0
    ):
        return _ELEVATED_RISK_LEVEL

    if (
        (failed_course_count is not None and failed_course_count >= 1)
        or (avg_course_score is not None and avg_course_score < 75)
        or (avg_gpa is not None and avg_gpa < 2.5)
    ):
        return _GENERAL_RISK_LEVEL

    return _LOW_RISK_LEVEL


def _coerce_number(raw: Any) -> float | None:
    if raw is None or pd.isna(raw):
        return None
    if isinstance(raw, bool):
        return 1.0 if raw else 0.0
    if isinstance(raw, (int, float)):
        return float(raw)
    try:
        return float(str(raw).strip())
    except (TypeError, ValueError):
        return None


def _is_false_like(raw: Any) -> bool:
    if raw is None:
        return False
    if isinstance(raw, bool):
        return raw is False
    if isinstance(raw, (int, float)):
        return raw == 0
    text = str(raw).strip().lower()
    return text in {"0", "false", "no", "n", "否"}


def _is_score_failed(raw: Any) -> bool:
    if raw is None or pd.isna(raw):
        return False
    try:
        return float(raw) < 60
    except (TypeError, ValueError):
        return False


def _is_present_status(raw: Any) -> bool:
    if raw is None:
        return False
    if isinstance(raw, bool):
        return raw
    text = _normalize_text(raw)
    if text is None:
        return False
    return text.lower() in _PRESENT_ATTENDANCE_STATUSES


def _normalize_text(raw: Any) -> str | None:
    if raw is None or isinstance(raw, bool):
        return None
    if isinstance(raw, float) and pd.isna(raw):
        return None
    text = str(raw).strip()
    return text or None
