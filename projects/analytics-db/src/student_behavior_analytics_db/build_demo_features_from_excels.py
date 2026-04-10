from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from typing import Callable

import pandas as pd

from .build_student_term_features import build_student_term_features
from .load_fact_assignments import load_fact_assignments
from .load_fact_attendance import load_fact_attendance
from .load_fact_discussions import load_fact_discussions
from .load_fact_enrollments import load_fact_enrollments
from .load_fact_evaluation_labels import load_fact_evaluation_labels
from .load_fact_exams import load_fact_exams
from .load_fact_grades import load_fact_grades
from .load_fact_library import load_fact_library
from .load_fact_running import load_fact_running
from .load_fact_signins import load_fact_signins
from .load_fact_tasks import load_fact_tasks
from .load_students import load_students
from .normalize_ids import normalize_student_id
from .normalize_terms import infer_term_from_month_only
from .normalize_terms import normalize_term_key

_ANALYSIS_TERMS = ("2023-2", "2024-1", "2024-2")
_KEY_COLUMNS = ["student_id", "term_key"]
_STANDARD_TERM_KEY_RE = re.compile(r"^\d{4}-[12]$")
_DEFERRED_CLASS_ATTENTION_COLUMNS = (
    "avg_head_up_rate",
    "avg_front_row_rate",
    "avg_bowing_rate",
)
_ARTIFACT_DIMENSION_RAW_COLUMNS = {
    "academic_base": "academic_base_score_raw",
    "class_engagement": "class_engagement_score_raw",
    "online_activeness": "online_activeness_score_raw",
    "library_immersion": "library_immersion_score_raw",
    "network_habits": "network_habits_score_raw",
    "daily_routine_boundary": "daily_routine_boundary_score_raw",
    "physical_resilience": "physical_resilience_score_raw",
    "appraisal_status_alert": "appraisal_status_alert_score_raw",
}


@dataclass(frozen=True)
class SourceSpec:
    filename: str
    usecols: tuple[str, ...]
    loader: Callable[[list[dict[str, object]]], pd.DataFrame]
    enabled_by_default: bool = True


_SOURCE_SPECS: dict[str, SourceSpec] = {
    "students": SourceSpec(
        filename="学生基本信息.xlsx",
        usecols=("XH", "XB", "MZMC", "ZZMMMC", "XSM", "ZYM"),
        loader=load_students,
    ),
    "grades": SourceSpec(
        filename="学生成绩.xlsx",
        usecols=("XH", "KSSJ", "KCH", "KCM", "KCCJ", "JDCJ"),
        loader=load_fact_grades,
    ),
    "attendance": SourceSpec(
        filename="考勤汇总.xlsx",
        usecols=("XN", "XQ", "RQ", "XH", "ZT", "DKSJ"),
        loader=load_fact_attendance,
    ),
    "evaluation_labels": SourceSpec(
        filename="本科生综合测评.xlsx",
        usecols=("XH", "CPXN", "CPXQ", "PDXN", "PDXQ", "ZYNJPM", "ZYNJRS"),
        loader=load_fact_evaluation_labels,
    ),
    "enrollments": SourceSpec(
        filename="学生选课信息.xlsx",
        usecols=("XH", "JXBH", "KCH", "KKXN", "KKXQ"),
        loader=load_fact_enrollments,
    ),
    "signins": SourceSpec(
        filename="学生签到记录.xlsx",
        usecols=("LOGIN_NAME", "ATTEND_TIME", "INSERT_TIME"),
        loader=load_fact_signins,
        enabled_by_default=False,
    ),
    "library": SourceSpec(
        filename="图书馆打卡记录.xlsx",
        usecols=("cardld", "visittime"),
        loader=load_fact_library,
        enabled_by_default=False,
    ),
    "assignments": SourceSpec(
        filename="学生作业提交记录.xlsx",
        usecols=(
            "CREATER_LOGIN_NAME",
            "WORK_ID",
            "WORK_TITLE",
            "COURSE_ID",
            "COURSE_NAME",
            "STATUS",
            "FULLMARKS",
            "SCORE",
            "TYPE",
            "CREATER_TIME",
            "ANSWER_TIME",
            "REVIEW_TIME",
            "UPDATE_TIME",
            "INSERT_TIME",
        ),
        loader=load_fact_assignments,
        enabled_by_default=False,
    ),
    "exams": SourceSpec(
        filename="考试提交记录.xlsx",
        usecols=(
            "CREATER_LOGIN_NAME",
            "WORK_ID",
            "WORK_TITLE",
            "COURSE_ID",
            "COURSE_NAME",
            "STATUS",
            "FULLMARKS",
            "SCORE",
            "TYPE",
            "CREATER_TIME",
            "ANSWER_TIME",
            "REVIEW_TIME",
            "UPDATE_TIME",
            "INSERT_TIME",
        ),
        loader=load_fact_exams,
        enabled_by_default=False,
    ),
    "discussions": SourceSpec(
        filename="讨论记录.xlsx",
        usecols=(
            "COURSE_ID",
            "COURSE_NAME",
            "TOPIC_ID",
            "TOPIC_TITLE",
            "CREATER_ROLE",
            "CREATER_NAME",
            "CREATER_LOGIN_NAME",
            "CREATE_TIME",
            "REPLY_USER_NAME",
            "REPLY_LOGIN_NAME",
            "REPLY_USER_ROLE",
            "REPLY_CONTENT",
            "ISDELETE",
            "INSERT_TIME",
            "TOPIC_ISDELETE",
        ),
        loader=load_fact_discussions,
        enabled_by_default=False,
    ),
    "tasks": SourceSpec(
        filename="课堂任务参与.xlsx",
        usecols=(
            "USER_ID",
            "LOGIN_NAME",
            "USER_NAME",
            "DEPARTMENT_NAME",
            "MAJOR_NAME",
            "CLASS_NAME",
            "STATE",
            "SCHOOL_YEAR",
            "COURSE_ID",
            "COURSE_NAME",
            "JWCOURSE_ID",
            "CREATE_TIME",
            "TASK_RATE",
            "UPDATE_TIME",
            "INSERT_TIME",
        ),
        loader=load_fact_tasks,
        enabled_by_default=False,
    ),
    "running": SourceSpec(
        filename="跑步打卡.xlsx",
        usecols=("PUNCH_DAY", "PUNCH_TIME", "TERM_ID", "USERNUM", "STATE"),
        loader=load_fact_running,
        enabled_by_default=False,
    ),
}


def discover_data_dir(repo_root: Path) -> Path:
    candidates = [
        path
        for path in repo_root.iterdir()
        if path.is_dir() and any(child.suffix.lower() == ".xlsx" for child in path.iterdir())
    ]
    if not candidates:
        raise FileNotFoundError("未找到包含 Excel 数据源的目录")
    preferred = next((path for path in candidates if "数据集" in path.name), None)
    return preferred or sorted(candidates)[0]


def build_demo_features_from_excels(
    *,
    repo_root: Path,
    data_dir: Path | None = None,
    output_csv: Path | None = None,
    include_heavy_sources: bool = True,
) -> dict[str, object]:
    resolved_output_csv = output_csv or repo_root / "artifacts" / "semester_features" / "v1_semester_features.csv"
    try:
        resolved_data_dir = data_dir or discover_data_dir(repo_root)
    except FileNotFoundError:
        fallback = _build_demo_features_from_artifacts(
            repo_root=repo_root,
            output_csv=resolved_output_csv,
        )
        fallback["include_heavy_sources"] = include_heavy_sources
        return fallback

    normalized_frames = {
        name: spec.loader(_read_excel_rows(_resolve_source_file(resolved_data_dir, spec), spec.usecols))
        for name, spec in _SOURCE_SPECS.items()
        if include_heavy_sources or spec.enabled_by_default
    }
    normalized_frames.setdefault("signins", pd.DataFrame())
    normalized_frames.setdefault("library", pd.DataFrame())
    normalized_frames.setdefault("assignments", pd.DataFrame())
    normalized_frames.setdefault("exams", pd.DataFrame())
    normalized_frames.setdefault("discussions", pd.DataFrame())
    normalized_frames.setdefault("tasks", pd.DataFrame())
    normalized_frames.setdefault("running", pd.DataFrame())
    official_student_ids = _collect_official_student_ids(normalized_frames["students"])
    normalized_frames = {
        name: frame if name == "students" else _filter_frame_to_official_students(frame, official_student_ids)
        for name, frame in normalized_frames.items()
    }

    features = build_student_term_features(
        students=normalized_frames["students"],
        grades=normalized_frames["grades"],
        attendance=normalized_frames["attendance"],
        enrollments=normalized_frames["enrollments"],
        signins=normalized_frames["signins"],
        assignments=normalized_frames["assignments"],
        exams=normalized_frames["exams"],
        tasks=normalized_frames["tasks"],
        discussions=normalized_frames["discussions"],
        library=normalized_frames["library"],
        running=normalized_frames["running"],
        evaluation_labels=normalized_frames["evaluation_labels"],
    )
    extra_features = _build_extra_demo_metrics(
        resolved_data_dir,
        include_heavy_sources=include_heavy_sources,
        official_student_ids=official_student_ids,
    )
    combined = _merge_feature_frames(features, extra_features)
    filtered = combined.loc[combined["term_key"].isin(_ANALYSIS_TERMS)].copy()
    filtered = filtered.sort_values(["student_id", "term_key"], kind="stable").reset_index(drop=True)

    resolved_output_csv.parent.mkdir(parents=True, exist_ok=True)
    filtered.to_csv(resolved_output_csv, index=False, encoding="utf-8-sig")

    return {
        "data_dir": str(resolved_data_dir),
        "output_csv": str(resolved_output_csv),
        "row_count": int(len(filtered)),
        "term_counts": {
            str(term_key): int(count)
            for term_key, count in filtered["term_key"].value_counts().sort_index().items()
        },
        "source_row_counts": {
            name: int(len(frame)) for name, frame in normalized_frames.items()
        },
        "include_heavy_sources": include_heavy_sources,
    }


def _build_demo_features_from_artifacts(
    *,
    repo_root: Path,
    output_csv: Path,
) -> dict[str, object]:
    artifact_path = repo_root / "artifacts" / "model_stubs" / "v1_student_results.csv"
    if not artifact_path.exists():
        raise FileNotFoundError("未找到 Excel 数据目录，且缺少可回退的 model_stubs 产物")

    artifact_frame = pd.read_csv(artifact_path)
    if artifact_frame.empty:
        raise ValueError("model_stubs 学生结果产物为空，无法回退生成 semester_features")

    features = artifact_frame.loc[:, [column for column in artifact_frame.columns if column in {"student_id", "term_key", "student_name", "major_name"}]].copy()
    if "student_id" not in features.columns or "term_key" not in features.columns:
        raise ValueError("model_stubs 学生结果产物缺少 student_id 或 term_key")

    features["college_name"] = None
    features["avg_course_score"] = None
    features["failed_course_count"] = None
    features["avg_gpa"] = None
    features["major_rank_pct"] = None
    features["risk_label"] = artifact_frame["risk_level"] if "risk_level" in artifact_frame.columns else None
    features["attendance_record_count"] = None
    features["attendance_normal_rate"] = None
    features["selected_course_count"] = None
    features["sign_event_count"] = None
    features["assignment_submit_count"] = None
    features["exam_submit_count"] = None
    features["task_participation_rate"] = None
    features["discussion_reply_count"] = None
    features["library_visit_count"] = None
    features["library_active_days"] = None
    features["running_punch_count"] = None
    features["morning_activity_rate"] = None

    dimension_rows = artifact_frame.get("dimension_scores_json")
    if dimension_rows is None:
        dimension_rows = pd.Series([None] * len(artifact_frame))

    for dimension_code, raw_column in _ARTIFACT_DIMENSION_RAW_COLUMNS.items():
        features[raw_column] = [
            _extract_artifact_dimension_raw_score(value, dimension_code)
            for value in dimension_rows
        ]

    resolved = features.loc[features["term_key"].isin(_ANALYSIS_TERMS)].copy()
    resolved = resolved.sort_values(["student_id", "term_key"], kind="stable").reset_index(drop=True)

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    resolved.to_csv(output_csv, index=False, encoding="utf-8-sig")

    return {
        "data_dir": "artifact_fallback:model_stubs/v1_student_results.csv",
        "output_csv": str(output_csv),
        "row_count": int(len(resolved)),
        "term_counts": {
            str(term_key): int(count)
            for term_key, count in resolved["term_key"].value_counts().sort_index().items()
        },
        "source_row_counts": {
            "artifact_student_results": int(len(artifact_frame)),
        },
        "source_mode": "artifact_fallback",
    }


def _extract_artifact_dimension_raw_score(value: object, dimension_code: str) -> float | None:
    if not isinstance(value, str) or not value.strip():
        return None

    try:
        payload = json.loads(value)
    except json.JSONDecodeError:
        return None

    if not isinstance(payload, list):
        return None

    for item in payload:
        if not isinstance(item, dict):
            continue
        if str(item.get("dimension_code", "")).strip() != dimension_code:
            continue
        score = _normalize_number(item.get("score"))
        if score is None:
            return None
        return round(score * 100, 2)
    return None


def _resolve_source_file(data_dir: Path, spec: SourceSpec) -> Path:
    path = data_dir / spec.filename
    if path.exists():
        return path
    fallback = _resolve_source_file_by_header(data_dir, spec.usecols)
    if fallback is not None:
        return fallback
    raise FileNotFoundError(f"未找到数据源文件: {spec.filename}")


def _resolve_source_file_by_header(data_dir: Path, usecols: tuple[str, ...]) -> Path | None:
    expected = set(usecols)
    for candidate in sorted(data_dir.glob("*.xlsx")):
        try:
            header_frame = pd.read_excel(candidate, nrows=0, dtype=object)
        except Exception:
            continue
        columns = {str(column) for column in header_frame.columns}
        if expected.issubset(columns):
            return candidate
    return None


def _read_excel_rows(path: Path, usecols: tuple[str, ...]) -> list[dict[str, object]]:
    frame = pd.read_excel(path, usecols=lambda column: column in usecols, dtype=object)
    records: list[dict[str, object]] = []
    for row_index, row in enumerate(frame.to_dict(orient="records"), start=2):
        cleaned = {
            key: value
            for key, value in row.items()
            if value is not None and not (isinstance(value, float) and pd.isna(value))
        }
        cleaned["source_file"] = path.name
        cleaned["source_row_hash"] = _build_row_hash(path.name, row_index, cleaned)
        records.append(cleaned)
    return records


def _build_row_hash(filename: str, row_index: int, row: dict[str, object]) -> str:
    del row_index
    normalized_items = [
        f"{key}={_normalize_hash_value(row[key])}"
        for key in sorted(row)
        if key not in {"source_file", "source_row_hash"}
    ]
    payload = "|".join((filename, *normalized_items))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _build_extra_demo_metrics(
    data_dir: Path,
    *,
    include_heavy_sources: bool,
    official_student_ids: set[str],
) -> pd.DataFrame:
    metric_frames = [
        _aggregate_grade_support_metrics(data_dir, official_student_ids=official_student_ids),
        _aggregate_attendance_support_metrics(data_dir, official_student_ids=official_student_ids),
    ]
    if include_heavy_sources:
        metric_frames.extend(
            [
                _aggregate_class_engagement_metrics(data_dir, official_student_ids=official_student_ids),
                _aggregate_online_learning_metrics(data_dir, official_student_ids=official_student_ids),
                _aggregate_library_support_metrics(data_dir, official_student_ids=official_student_ids),
                _aggregate_network_usage_metrics(data_dir, official_student_ids=official_student_ids),
                _aggregate_access_control_metrics(data_dir, official_student_ids=official_student_ids),
                _aggregate_physical_support_metrics(data_dir, official_student_ids=official_student_ids),
                _aggregate_appraisal_support_metrics(data_dir, official_student_ids=official_student_ids),
            ]
        )
    keys = _collect_metric_keys(metric_frames)

    merged = keys.copy()
    for frame in metric_frames:
        if frame.empty:
            continue
        merged = merged.merge(frame, on=_KEY_COLUMNS, how="left")

    merged = _add_deferred_metric_placeholders(merged)
    merged["network_habits_deep_night_metrics_available"] = False
    merged = _filter_frame_to_official_students(merged, official_student_ids)
    merged = _add_raw_dimension_scores(merged)
    return merged


def _merge_feature_frames(features: pd.DataFrame, extra_features: pd.DataFrame) -> pd.DataFrame:
    if features.empty:
        return extra_features.copy()
    if extra_features.empty:
        return features.copy()

    merged = features.merge(extra_features, on=_KEY_COLUMNS, how="outer", suffixes=("", "__extra"))
    for column in list(merged.columns):
        if not column.endswith("__extra"):
            continue
        base_column = column.removesuffix("__extra")
        if base_column in merged.columns:
            merged[base_column] = merged[column].combine_first(merged[base_column])
            merged = merged.drop(columns=[column])
        else:
            merged = merged.rename(columns={column: base_column})
    return merged


def _collect_metric_keys(frames: list[pd.DataFrame]) -> pd.DataFrame:
    collected: list[pd.DataFrame] = []
    for frame in frames:
        if frame.empty or not set(_KEY_COLUMNS).issubset(frame.columns):
            continue
        subset = frame.loc[:, _KEY_COLUMNS].dropna(subset=_KEY_COLUMNS)
        if not subset.empty:
            collected.append(subset)
    if not collected:
        return pd.DataFrame(columns=_KEY_COLUMNS)
    return pd.concat(collected, ignore_index=True).drop_duplicates(ignore_index=True)


def _collect_official_student_ids(students: pd.DataFrame) -> set[str]:
    if students.empty or "student_id" not in students.columns:
        return set()
    return {
        student_id
        for student_id in students["student_id"].tolist()
        if isinstance(student_id, str) and student_id
    }


def _filter_frame_to_official_students(frame: pd.DataFrame, official_student_ids: set[str]) -> pd.DataFrame:
    if frame.empty or "student_id" not in frame.columns:
        return frame
    if not official_student_ids:
        return frame.iloc[0:0].copy()
    filtered = frame.loc[frame["student_id"].isin(official_student_ids)].copy()
    return filtered.reset_index(drop=True)


def _add_deferred_metric_placeholders(frame: pd.DataFrame) -> pd.DataFrame:
    enriched = frame.copy()
    for column in _DEFERRED_CLASS_ATTENTION_COLUMNS:
        if column not in enriched.columns:
            enriched[column] = pd.NA
    enriched["class_attention_metrics_available"] = False
    return enriched


def _aggregate_grade_support_metrics(data_dir: Path, *, official_student_ids: set[str]) -> pd.DataFrame:
    rows = _read_optional_excel_rows(
        data_dir,
        "学生成绩.xlsx",
        ("XH", "XSBH", "LOGIN_NAME", "USERNUM", "KSSJ", "XN", "XQ", "KKXN", "KKXQ", "KCCJ", "JDCJ", "XF"),
    )
    records: list[dict[str, object]] = []
    for row in rows:
        student_id = _pick_student_id(
            row,
            "XH",
            "XSBH",
            "LOGIN_NAME",
            "USERNUM",
            official_student_ids=official_student_ids,
        )
        term_key = _pick_term_key(
            row,
            combined_term_keys=("term_key", "XNXQ"),
            year_keys=("XN", "KKXN"),
            term_keys=("XQ", "KKXQ"),
            date_keys=("KSSJ",),
        )
        score = _normalize_number(_first_value(row, "KCCJ"))
        if student_id is None or term_key is None or score is None:
            continue
        records.append(
            {
                "student_id": student_id,
                "term_key": term_key,
                "score": score,
                "gpa": _normalize_number(_first_value(row, "JDCJ")),
                "credits": _normalize_number(_first_value(row, "XF")),
            }
        )

    if not records:
        return pd.DataFrame(
            columns=[*_KEY_COLUMNS, "failed_course_count", "borderline_course_count", "attempted_credit_sum", "failed_course_ratio"]
        )

    frame = pd.DataFrame.from_records(records)
    grouped = frame.groupby(_KEY_COLUMNS, dropna=False)
    aggregated = grouped.agg(
        avg_course_score_metric=("score", "mean"),
        avg_gpa_metric=("gpa", "mean"),
        attempted_credit_sum=("credits", "sum"),
        course_record_count=("score", "size"),
        failed_course_count=("score", lambda values: int((pd.to_numeric(values, errors="coerce") < 60).sum())),
        borderline_course_count=(
            "score",
            lambda values: int(((pd.to_numeric(values, errors="coerce") >= 60) & (pd.to_numeric(values, errors="coerce") < 70)).sum()),
        ),
    ).reset_index()
    aggregated["failed_course_ratio"] = aggregated.apply(
        lambda row: None if row["course_record_count"] == 0 else row["failed_course_count"] / row["course_record_count"],
        axis=1,
    )
    return aggregated


def _aggregate_attendance_support_metrics(data_dir: Path, *, official_student_ids: set[str]) -> pd.DataFrame:
    rows = _read_optional_excel_rows(
        data_dir,
        "考勤汇总.xlsx",
        ("XH", "XSBH", "LOGIN_NAME", "USERNUM", "XN", "XQ", "RQ", "DKSJ", "ZT"),
    )
    records: list[dict[str, object]] = []
    for row in rows:
        student_id = _pick_student_id(
            row,
            "XH",
            "XSBH",
            "LOGIN_NAME",
            "USERNUM",
            official_student_ids=official_student_ids,
        )
        term_key = _pick_term_key(row, year_keys=("XN",), term_keys=("XQ",), date_keys=("DKSJ", "RQ"))
        status = _normalize_text(_first_value(row, "ZT"))
        if student_id is None or term_key is None or status is None:
            continue
        records.append({"student_id": student_id, "term_key": term_key, "attendance_status": status})

    if not records:
        return pd.DataFrame(columns=[*_KEY_COLUMNS, "attendance_rate", "late_count", "truancy_count", "absence_count"])

    frame = pd.DataFrame.from_records(records)
    grouped = frame.groupby(_KEY_COLUMNS, dropna=False)
    aggregated = grouped.agg(
        attendance_record_count=("attendance_status", "size"),
        present_count=("attendance_status", lambda values: int(sum(_is_present_status(value) for value in values))),
        late_count=("attendance_status", lambda values: int(sum("迟" in str(value) for value in values))),
        truancy_count=("attendance_status", lambda values: int(sum("旷" in str(value) for value in values))),
        absence_count=("attendance_status", lambda values: int(sum(_is_absence_status(value) for value in values))),
    ).reset_index()
    aggregated["attendance_rate"] = aggregated.apply(
        lambda row: None if row["attendance_record_count"] == 0 else row["present_count"] / row["attendance_record_count"],
        axis=1,
    )
    return aggregated


def _aggregate_class_engagement_metrics(data_dir: Path, *, official_student_ids: set[str]) -> pd.DataFrame:
    rows = _read_optional_excel_rows(
        data_dir,
        "课堂任务参与.xlsx",
        (
            "LOGIN_NAME",
            "XH",
            "XSBH",
            "USERNUM",
            "SCHOOL_YEAR",
            "XN",
            "XQ",
            "CREATE_TIME",
            "VIDEOJOB_RATE",
            "BBS_NUM",
            "TOPIC_NUM",
            "REPLY_NUM",
        ),
    )
    records: list[dict[str, object]] = []
    for row in rows:
        student_id = _pick_student_id(
            row,
            "LOGIN_NAME",
            "XH",
            "XSBH",
            "USERNUM",
            official_student_ids=official_student_ids,
        )
        term_key = _pick_term_key(
            row,
            combined_term_keys=("term_key", "XQ"),
            year_keys=("XN", "SCHOOL_YEAR"),
            term_keys=("XQ",),
            date_keys=("CREATE_TIME",),
        )
        if student_id is None or term_key is None:
            continue
        records.append(
            {
                "student_id": student_id,
                "term_key": term_key,
                "video_completion_rate": _normalize_number(_first_value(row, "VIDEOJOB_RATE")),
                "forum_interaction_total": (
                    (_normalize_number(_first_value(row, "BBS_NUM")) or 0)
                    + (_normalize_number(_first_value(row, "TOPIC_NUM")) or 0)
                    + (_normalize_number(_first_value(row, "REPLY_NUM")) or 0)
                ),
            }
        )

    if not records:
        return pd.DataFrame(columns=[*_KEY_COLUMNS, "video_completion_rate", "forum_interaction_total"])

    frame = pd.DataFrame.from_records(records)
    return (
        frame.groupby(_KEY_COLUMNS, dropna=False)
        .agg(
            video_completion_rate=("video_completion_rate", "mean"),
            forum_interaction_total=("forum_interaction_total", "sum"),
        )
        .reset_index()
    )


def _aggregate_online_learning_metrics(data_dir: Path, *, official_student_ids: set[str]) -> pd.DataFrame:
    task_rows = _read_optional_excel_rows(
        data_dir,
        "课堂任务参与.xlsx",
        (
            "LOGIN_NAME",
            "XH",
            "XSBH",
            "USERNUM",
            "SCHOOL_YEAR",
            "XN",
            "XQ",
            "CREATE_TIME",
            "VIDEOJOB_TIME",
            "TEST_AVGSCORE",
            "WORK_AVGSCORE",
            "EXAM_AVGSCORE",
        ),
    )
    task_records: list[dict[str, object]] = []
    for row in task_rows:
        student_id = _pick_student_id(
            row,
            "LOGIN_NAME",
            "XH",
            "XSBH",
            "USERNUM",
            official_student_ids=official_student_ids,
        )
        term_key = _pick_term_key(
            row,
            combined_term_keys=("term_key", "XQ"),
            year_keys=("XN", "SCHOOL_YEAR"),
            term_keys=("XQ",),
            date_keys=("CREATE_TIME",),
        )
        if student_id is None or term_key is None:
            continue
        task_records.append(
            {
                "student_id": student_id,
                "term_key": term_key,
                "video_watch_time": _normalize_number(_first_value(row, "VIDEOJOB_TIME")),
                "online_test_avg_score": _normalize_number(_first_value(row, "TEST_AVGSCORE")),
                "online_work_avg_score": _normalize_number(_first_value(row, "WORK_AVGSCORE")),
                "online_exam_avg_score": _normalize_number(_first_value(row, "EXAM_AVGSCORE")),
            }
        )

    if not task_records:
        return pd.DataFrame(
            columns=[
                *_KEY_COLUMNS,
                "video_watch_time_sum",
                "online_test_avg_score",
                "online_work_avg_score",
                "online_exam_avg_score",
                "platform_engagement_score",
            ]
        )

    task_metrics = (
        pd.DataFrame.from_records(task_records)
        .groupby(_KEY_COLUMNS, dropna=False)
        .agg(
            video_watch_time_sum=("video_watch_time", "sum"),
            online_test_avg_score=("online_test_avg_score", "mean"),
            online_work_avg_score=("online_work_avg_score", "mean"),
            online_exam_avg_score=("online_exam_avg_score", "mean"),
        )
        .reset_index()
    )

    platform_rows = _read_optional_excel_rows(
        data_dir,
        "线上学习（综合表现）.xlsx",
        ("LOGIN_NAME", "XH", "XSBH", "USERNUM", "BFB"),
    )
    platform_records: list[dict[str, object]] = []
    for row in platform_rows:
        student_id = _pick_student_id(
            row,
            "LOGIN_NAME",
            "XH",
            "XSBH",
            "USERNUM",
            official_student_ids=official_student_ids,
        )
        platform_score = _normalize_number(_first_value(row, "BFB"))
        if student_id is None or platform_score is None:
            continue
        platform_records.append({"student_id": student_id, "platform_engagement_score": platform_score})

    if not platform_records:
        task_metrics["platform_engagement_score"] = None
        return task_metrics

    platform_metrics = (
        pd.DataFrame.from_records(platform_records)
        .groupby("student_id", dropna=False)["platform_engagement_score"]
        .mean()
        .reset_index()
    )
    return task_metrics.merge(platform_metrics, on="student_id", how="left")


def _aggregate_library_support_metrics(data_dir: Path, *, official_student_ids: set[str]) -> pd.DataFrame:
    rows = _read_optional_excel_rows(
        data_dir,
        "图书馆打卡记录.xlsx",
        ("cardld", "cardid", "LOGIN_NAME", "USERNUM", "XH", "visittime", "direction"),
    )
    records: list[dict[str, object]] = []
    for row in rows:
        student_id = _pick_student_id(
            row,
            "cardld",
            "cardid",
            "LOGIN_NAME",
            "USERNUM",
            "XH",
            official_student_ids=official_student_ids,
        )
        visited_at = _normalize_timestamp(_first_value(row, "visittime"))
        term_key = _pick_term_key(row, date_keys=("visittime",))
        if student_id is None or term_key is None or visited_at is None:
            continue
        records.append(
            {
                "student_id": student_id,
                "term_key": term_key,
                "visited_at": visited_at,
                "direction": (_normalize_text(_first_value(row, "direction")) or "").lower(),
            }
        )

    if not records:
        return pd.DataFrame(columns=[*_KEY_COLUMNS, "library_completed_visit_count", "avg_library_stay_minutes"])

    frame = pd.DataFrame.from_records(records)
    frame["visited_at"] = pd.to_datetime(frame["visited_at"], errors="coerce")
    frame = frame.dropna(subset=["visited_at"])
    visits: list[dict[str, object]] = []
    for (student_id, term_key), group in frame.groupby(_KEY_COLUMNS, dropna=False):
        ordered = group.sort_values("visited_at", kind="stable")
        current_entry: pd.Timestamp | None = None
        stay_minutes: list[float] = []
        active_days = int(ordered["visited_at"].dt.date.nunique())
        for row in ordered.itertuples(index=False):
            direction = str(row.direction).strip().lower()
            visited_at = row.visited_at
            is_entry = direction in {"in", "1", "entry", "enter"}
            is_exit = direction in {"out", "2", "exit", "leave"}
            if is_entry:
                current_entry = visited_at
                continue
            if is_exit and current_entry is not None and visited_at >= current_entry:
                stay_minutes.append((visited_at - current_entry).total_seconds() / 60)
                current_entry = None
        visit_count = len(stay_minutes)
        if visit_count == 0:
            visit_count = active_days
        avg_stay = None if not stay_minutes else sum(stay_minutes) / len(stay_minutes)
        visits.append(
            {
                "student_id": student_id,
                "term_key": term_key,
                "library_completed_visit_count": visit_count,
                "avg_library_stay_minutes": avg_stay,
            }
        )
    return pd.DataFrame.from_records(visits)


def _aggregate_network_usage_metrics(data_dir: Path, *, official_student_ids: set[str]) -> pd.DataFrame:
    rows = _read_optional_excel_rows(
        data_dir,
        "上网统计.xlsx",
        ("XSBH", "XH", "LOGIN_NAME", "USERNUM", "TJNY", "XN", "XQ", "SWLJSC", "XXPJZ"),
    )
    records: list[dict[str, object]] = []
    for row in rows:
        student_id = _pick_student_id(
            row,
            "XSBH",
            "XH",
            "LOGIN_NAME",
            "USERNUM",
            official_student_ids=official_student_ids,
        )
        term_key = _pick_term_key(row, year_keys=("XN",), term_keys=("XQ",), date_keys=("TJNY",))
        duration_sum = _normalize_number(_first_value(row, "SWLJSC"))
        school_avg = _normalize_number(_first_value(row, "XXPJZ"))
        if student_id is None or term_key is None or duration_sum is None:
            continue
        duration_value = float(duration_sum)
        school_avg_value = None if school_avg is None else float(school_avg)
        records.append(
            {
                "student_id": student_id,
                "term_key": term_key,
                "term_online_duration_sum": duration_value,
                "duration_gap_component": None if school_avg_value is None else duration_value - school_avg_value,
            }
        )

    if not records:
        return pd.DataFrame(columns=[*_KEY_COLUMNS, "term_online_duration_sum", "monthly_online_duration_avg", "online_duration_vs_school_avg_gap"])

    frame = pd.DataFrame.from_records(records)
    return (
        frame.groupby(_KEY_COLUMNS, dropna=False)
        .agg(
            term_online_duration_sum=("term_online_duration_sum", "sum"),
            monthly_online_duration_avg=("term_online_duration_sum", "mean"),
            online_duration_vs_school_avg_gap=("duration_gap_component", "mean"),
        )
        .reset_index()
    )


def _aggregate_access_control_metrics(data_dir: Path, *, official_student_ids: set[str]) -> pd.DataFrame:
    rows = _read_optional_excel_rows(
        data_dir,
        "门禁数据.xlsx",
        ("IDSERTAL", "XH", "XSBH", "LOGIN_NAME", "USERNUM", "LOGINTIME", "LOGINSIGN"),
    )
    records: list[dict[str, object]] = []
    for row in rows:
        student_id = _pick_student_id(
            row,
            "IDSERTAL",
            "XH",
            "XSBH",
            "LOGIN_NAME",
            "USERNUM",
            official_student_ids=official_student_ids,
        )
        login_time = _normalize_timestamp(_first_value(row, "LOGINTIME"))
        term_key = _pick_term_key(row, date_keys=("LOGINTIME",))
        if student_id is None or term_key is None or login_time is None:
            continue
        records.append(
            {
                "student_id": student_id,
                "term_key": term_key,
                "gate_time": login_time,
                "login_sign": _normalize_number(_first_value(row, "LOGINSIGN")),
            }
        )

    if not records:
        return pd.DataFrame(
            columns=[
                *_KEY_COLUMNS,
                "late_return_count",
                "first_daily_access_time_avg",
                "first_daily_access_time_std",
                "late_return_ratio",
                "daily_access_time_variability",
            ]
        )

    frame = pd.DataFrame.from_records(records)
    frame["gate_time"] = pd.to_datetime(frame["gate_time"], errors="coerce")
    frame = frame.dropna(subset=["gate_time"])
    frame["is_late_return"] = frame.apply(lambda row: _is_late_return_event(row["gate_time"], row["login_sign"]), axis=1)
    frame["is_return_event"] = frame["login_sign"].apply(lambda value: _normalize_number(value) == 1)
    frame["access_date"] = frame["gate_time"].dt.date
    frame["gate_minutes"] = frame["gate_time"].apply(_minutes_since_midnight)

    first_daily = (
        frame.groupby([*_KEY_COLUMNS, "access_date"], dropna=False)["gate_minutes"]
        .min()
        .reset_index(name="first_daily_access_minutes")
    )
    first_daily_aggregated = (
        first_daily.groupby(_KEY_COLUMNS, dropna=False)["first_daily_access_minutes"]
        .agg(
            first_daily_access_time_avg="mean",
            first_daily_access_time_std=lambda values: float(pd.Series(values, dtype="float64").std(ddof=0)),
            daily_access_time_variability=lambda values: float(pd.Series(values, dtype="float64").max() - pd.Series(values, dtype="float64").min()),
        )
        .reset_index()
    )
    access_aggregated = (
        frame.groupby(_KEY_COLUMNS, dropna=False)
        .agg(
            late_return_count=("is_late_return", "sum"),
            return_event_count=("is_return_event", "sum"),
        )
        .reset_index()
    )
    merged = access_aggregated.merge(first_daily_aggregated, on=_KEY_COLUMNS, how="left")
    merged["late_return_ratio"] = merged.apply(
        lambda row: None if row["return_event_count"] == 0 else row["late_return_count"] / row["return_event_count"],
        axis=1,
    )
    return merged.drop(columns=["return_event_count"])


def _aggregate_physical_support_metrics(data_dir: Path, *, official_student_ids: set[str]) -> pd.DataFrame:
    test_rows = _read_optional_excel_rows(
        data_dir,
        "体测数据.xlsx",
        ("XH", "XSBH", "LOGIN_NAME", "USERNUM", "TCNF", "ZF"),
    )
    exercise_rows = _read_optional_excel_rows(
        data_dir,
        "日常锻炼.xlsx",
        ("XH", "XSBH", "LOGIN_NAME", "USERNUM", "XN", "XQ", "DKCS"),
    )
    frames: list[pd.DataFrame] = []

    test_records: list[dict[str, object]] = []
    for row in test_rows:
        student_id = _pick_student_id(
            row,
            "XH",
            "XSBH",
            "LOGIN_NAME",
            "USERNUM",
            official_student_ids=official_student_ids,
        )
        term_key = _pick_term_key(row, year_keys=("TCNF",), default_term="1")
        score = _normalize_number(_first_value(row, "ZF"))
        if student_id is None or term_key is None or score is None:
            continue
        score_value = float(score)
        test_records.append(
            {
                "student_id": student_id,
                "term_key": term_key,
                "physical_test_avg_score": score_value,
                "physical_test_pass_flag": score_value >= 60,
            }
        )
    if test_records:
        frames.append(
            pd.DataFrame.from_records(test_records)
            .groupby(_KEY_COLUMNS, dropna=False)
            .agg(
                physical_test_avg_score=("physical_test_avg_score", "mean"),
                physical_test_pass_flag=("physical_test_pass_flag", "max"),
            )
            .reset_index()
        )

    exercise_records: list[dict[str, object]] = []
    for row in exercise_rows:
        student_id = _pick_student_id(
            row,
            "XH",
            "XSBH",
            "LOGIN_NAME",
            "USERNUM",
            official_student_ids=official_student_ids,
        )
        term_key = _pick_term_key(row, combined_term_keys=("XQ",), year_keys=("XN",), term_keys=("XQ",))
        count = _normalize_number(_first_value(row, "DKCS"))
        if student_id is None or term_key is None or count is None:
            continue
        exercise_records.append({"student_id": student_id, "term_key": term_key, "exercise_count": float(count)})
    if exercise_records:
        frames.append(
            pd.DataFrame.from_records(exercise_records)
            .groupby(_KEY_COLUMNS, dropna=False)["exercise_count"]
            .mean()
            .reset_index(name="weekly_exercise_count_avg")
        )

    keys = _collect_metric_keys(frames)
    if keys.empty:
        return pd.DataFrame(columns=[*_KEY_COLUMNS, "physical_test_avg_score", "physical_test_pass_flag", "weekly_exercise_count_avg"])
    merged = keys.copy()
    for frame in frames:
        merged = merged.merge(frame, on=_KEY_COLUMNS, how="left")
    return merged


def _aggregate_appraisal_support_metrics(data_dir: Path, *, official_student_ids: set[str]) -> pd.DataFrame:
    scholarship_rows = _read_optional_excel_rows(
        data_dir,
        "奖学金获奖.xlsx",
        ("XSBH", "XH", "LOGIN_NAME", "USERNUM", "PDXN", "PDDJ", "FFJE"),
    )
    status_rows = _read_optional_excel_rows(
        data_dir,
        "学籍异动.xlsx",
        ("XH", "XSBH", "LOGIN_NAME", "USERNUM", "YDRQ", "YDLBDM", "YDYYDM", "SFZX"),
    )
    frames: list[pd.DataFrame] = []

    scholarship_records: list[dict[str, object]] = []
    for row in scholarship_rows:
        student_id = _pick_student_id(
            row,
            "XSBH",
            "XH",
            "LOGIN_NAME",
            "USERNUM",
            official_student_ids=official_student_ids,
        )
        term_key = _pick_term_key(row, year_keys=("PDXN",), default_term="1")
        amount = _normalize_number(_first_value(row, "FFJE"))
        if student_id is None or term_key is None or amount is None:
            continue
        scholarship_records.append(
            {
                "student_id": student_id,
                "term_key": term_key,
                "scholarship_amount_sum": float(amount),
                "scholarship_level_score": _scholarship_level_score(_first_value(row, "PDDJ")),
            }
        )
    if scholarship_records:
        frames.append(
            pd.DataFrame.from_records(scholarship_records)
            .groupby(_KEY_COLUMNS, dropna=False)
            .agg(
                scholarship_amount_sum=("scholarship_amount_sum", "sum"),
                scholarship_level_score=("scholarship_level_score", "max"),
            )
            .reset_index()
        )

    status_records: list[dict[str, object]] = []
    for row in status_rows:
        student_id = _pick_student_id(
            row,
            "XH",
            "XSBH",
            "LOGIN_NAME",
            "USERNUM",
            official_student_ids=official_student_ids,
        )
        term_key = _pick_term_key(row, date_keys=("YDRQ",))
        if student_id is None or term_key is None:
            continue
        status_records.append(
            {
                "student_id": student_id,
                "term_key": term_key,
                "negative_status_alert_flag": _is_negative_status_change(
                    _first_value(row, "YDLBDM"),
                    _first_value(row, "YDYYDM"),
                    _first_value(row, "SFZX"),
                ),
                "status_change_count": 1,
            }
        )
    if status_records:
        frames.append(
            pd.DataFrame.from_records(status_records)
            .groupby(_KEY_COLUMNS, dropna=False)
            .agg(
                negative_status_alert_flag=("negative_status_alert_flag", "max"),
                status_change_count=("status_change_count", "sum"),
            )
            .reset_index()
        )

    keys = _collect_metric_keys(frames)
    if keys.empty:
        return pd.DataFrame(
            columns=[
                *_KEY_COLUMNS,
                "scholarship_amount_sum",
                "scholarship_level_score",
                "negative_status_alert_flag",
                "status_change_count",
            ]
        )
    merged = keys.copy()
    for frame in frames:
        merged = merged.merge(frame, on=_KEY_COLUMNS, how="left")
    return merged


def _add_raw_dimension_scores(frame: pd.DataFrame) -> pd.DataFrame:
    enriched = frame.copy()
    enriched["academic_base_score_raw"] = enriched.apply(
        lambda row: _mean_available(
            _normalize_number(row.get("avg_course_score_metric")),
            _inverse_ratio_score(row.get("failed_course_ratio")),
            _scale_to_100(row.get("avg_gpa_metric"), 4),
        ),
        axis=1,
    )
    enriched["class_engagement_score_raw"] = enriched.apply(
        lambda row: _mean_available(
            _ratio_score(row.get("attendance_rate")),
            _penalty_score(row.get("late_count"), penalty=20),
            _penalty_score(row.get("truancy_count"), penalty=30),
            _penalty_score(row.get("absence_count"), penalty=20),
        ),
        axis=1,
    )
    enriched["online_activeness_score_raw"] = enriched.apply(
        lambda row: _mean_available(
            _ratio_score(row.get("video_completion_rate")),
            _capped_score(row.get("video_watch_time_sum"), scale=1 / 3),
            _normalize_number(row.get("online_test_avg_score")),
            _normalize_number(row.get("online_work_avg_score")),
            _normalize_number(row.get("online_exam_avg_score")),
            _normalize_number(row.get("platform_engagement_score")),
        ),
        axis=1,
    )
    enriched["library_immersion_score_raw"] = enriched.apply(
        lambda row: _mean_available(
            _capped_score(row.get("library_completed_visit_count"), scale=20),
            _capped_score(row.get("avg_library_stay_minutes"), scale=1 / 3),
        ),
        axis=1,
    )
    enriched["network_habits_score_raw"] = enriched.apply(
        lambda row: _mean_available(
            _capped_score(row.get("monthly_online_duration_avg"), scale=1 / 3),
            _gap_score(row.get("online_duration_vs_school_avg_gap")),
        ),
        axis=1,
    )
    enriched["daily_routine_boundary_score_raw"] = enriched.apply(
        lambda row: _mean_available(
            _time_window_score(row.get("first_daily_access_time_avg"), target=420, tolerance=180),
            _inverse_capped_score(row.get("first_daily_access_time_std"), scale=1),
            _inverse_ratio_score(row.get("late_return_ratio")),
            _inverse_capped_score(row.get("daily_access_time_variability"), scale=1),
        ),
        axis=1,
    )
    enriched["physical_resilience_score_raw"] = enriched.apply(
        lambda row: _mean_available(
            _normalize_number(row.get("physical_test_avg_score")),
            _capped_score(row.get("weekly_exercise_count_avg"), scale=10),
            100 if row.get("physical_test_pass_flag") is True else 0 if row.get("physical_test_pass_flag") is False else None,
        ),
        axis=1,
    )
    enriched["appraisal_status_alert_score_raw"] = enriched.apply(
        lambda row: _mean_available(
            0 if row.get("negative_status_alert_flag") is True else 100 if row.get("negative_status_alert_flag") is False else None,
            _capped_score(row.get("scholarship_amount_sum"), scale=1 / 50),
        ),
        axis=1,
    )
    return enriched


def _read_optional_excel_rows(data_dir: Path, filename: str, usecols: tuple[str, ...]) -> list[dict[str, object]]:
    path = data_dir / filename
    if not path.exists():
        return []
    return _read_excel_rows(path, usecols)


def _pick_student_id(
    row: dict[str, object],
    *keys: str,
    official_student_ids: set[str] | None = None,
) -> str | None:
    for key in keys:
        student_id = normalize_student_id(row.get(key))
        if student_id is None:
            continue
        if official_student_ids is None or student_id in official_student_ids:
            return student_id
    return None


def _pick_term_key(
    row: dict[str, object],
    *,
    combined_term_keys: tuple[str, ...] = (),
    year_keys: tuple[str, ...] = (),
    term_keys: tuple[str, ...] = (),
    date_keys: tuple[str, ...] = (),
    default_term: str | None = None,
) -> str | None:
    for key in combined_term_keys:
        term_key = _normalize_term_key_value(row.get(key))
        if term_key is not None:
            return term_key

    raw_year = _first_value(row, *year_keys)
    raw_term = _first_value(row, *term_keys)
    if raw_year is not None and raw_term is not None:
        term_key = normalize_term_key(raw_year, raw_term)
        if term_key is not None:
            return term_key
    if raw_year is not None and default_term is not None:
        term_key = normalize_term_key(_normalize_school_year_value(raw_year), default_term)
        if term_key is not None:
            return term_key

    for key in date_keys:
        term_key = infer_term_from_month_only(row.get(key))
        if term_key is not None:
            return term_key
    return None


def _normalize_term_key_value(raw: object) -> str | None:
    if raw is None or isinstance(raw, bool):
        return None
    text = str(raw).strip()
    if not text:
        return None
    if _STANDARD_TERM_KEY_RE.fullmatch(text):
        return text
    return normalize_term_key(text, None)


def _normalize_school_year_value(raw: object) -> str | None:
    if raw is None or isinstance(raw, bool):
        return None
    text = str(raw).strip()
    if not text:
        return None
    if re.fullmatch(r"\d{4}", text):
        return f"{text}-{int(text) + 1}"
    return text


def _first_value(row: dict[str, object], *keys: str) -> object | None:
    for key in keys:
        if key not in row:
            continue
        value = row.get(key)
        if value is None or isinstance(value, bool):
            continue
        if isinstance(value, float) and pd.isna(value):
            continue
        if isinstance(value, str):
            text = value.strip()
            if text:
                return text
            continue
        return value
    return None


def _normalize_text(raw: object) -> str | None:
    if raw is None or isinstance(raw, bool):
        return None
    if isinstance(raw, float) and pd.isna(raw):
        return None
    text = str(raw).strip()
    return text or None


def _normalize_hash_value(raw: object) -> str:
    if raw is None:
        return ""
    if isinstance(raw, bool):
        return "true" if raw else "false"
    if isinstance(raw, float):
        if pd.isna(raw):
            return ""
        return format(raw, ".15g")
    if hasattr(raw, "isoformat"):
        try:
            return raw.isoformat()
        except TypeError:
            pass
    return str(raw).strip()


def _normalize_number(raw: object) -> float | int | None:
    if raw is None or isinstance(raw, bool):
        return None
    if isinstance(raw, float) and pd.isna(raw):
        return None
    if isinstance(raw, (int, float)):
        return int(raw) if isinstance(raw, float) and raw.is_integer() else raw
    text = str(raw).strip()
    if not text:
        return None
    try:
        number = float(text)
    except ValueError:
        return None
    return int(number) if number.is_integer() else number


def _normalize_timestamp(raw: object) -> str | None:
    if raw is None or isinstance(raw, bool):
        return None
    if isinstance(raw, float) and pd.isna(raw):
        return None
    try:
        parsed = pd.to_datetime(raw, errors="coerce")
    except (TypeError, ValueError, OverflowError):
        return None
    if pd.isna(parsed):
        return None
    return pd.Timestamp(parsed).strftime("%Y-%m-%d %H:%M:%S")


def _is_present_status(raw: object) -> bool:
    text = _normalize_text(raw)
    if text is None:
        return False
    return text in {"正常", "present", "Present", "normal", "Normal"}


def _is_absence_status(raw: object) -> bool:
    text = _normalize_text(raw)
    if text is None:
        return False
    lowered = text.lower()
    return any(keyword in text for keyword in ("缺", "假", "未到")) or any(
        keyword in lowered for keyword in ("absence", "absent", "leave")
    )


def _is_late_return_event(gate_time: pd.Timestamp, login_sign: object) -> bool:
    if pd.isna(gate_time):
        return False
    sign_value = _normalize_number(login_sign)
    if sign_value is None or int(sign_value) != 1:
        return False
    return gate_time.hour >= 22 or gate_time.hour < 6


def _minutes_since_midnight(gate_time: pd.Timestamp) -> float:
    return (gate_time.hour * 60) + gate_time.minute + (gate_time.second / 60)


def _scholarship_level_score(raw_level: object) -> int | None:
    text = _normalize_text(raw_level)
    if text is None:
        return None
    if "特等" in text:
        return 4
    if "一等" in text:
        return 3
    if "二等" in text:
        return 2
    if "三等" in text:
        return 1
    return None


def _is_negative_status_change(raw_category: object, raw_reason: object, raw_in_school: object) -> bool:
    category = _normalize_text(raw_category) or ""
    reason = (_normalize_text(raw_reason) or "").lower()
    in_school = (_normalize_text(raw_in_school) or "").lower()
    negative_keywords = ("休学", "退学", "离校", "开除", "注销", "取消学籍", "保留学籍")
    negative_reason_keywords = ("withdraw", "dropout", "suspend", "expel", "not_in_school", "out_of_school")
    non_school_values = {"不在校", "否", "false", "0", "离校", "未在校"}
    return (
        in_school in non_school_values
        or any(keyword in category for keyword in negative_keywords)
        or any(keyword in reason for keyword in negative_reason_keywords)
    )


def _mean_available(*values: object) -> float | None:
    normalized = [float(value) for value in values if value is not None and not (isinstance(value, float) and pd.isna(value))]
    if not normalized:
        return None
    return sum(normalized) / len(normalized)


def _ratio_score(raw_ratio: object) -> float | None:
    ratio = _normalize_number(raw_ratio)
    if ratio is None:
        return None
    return max(0.0, min(float(ratio) * 100, 100.0))


def _inverse_ratio_score(raw_ratio: object) -> float | None:
    ratio = _normalize_number(raw_ratio)
    if ratio is None:
        return None
    return max(0.0, min((1 - float(ratio)) * 100, 100.0))


def _capped_score(raw_value: object, *, scale: float) -> float | None:
    value = _normalize_number(raw_value)
    if value is None:
        return None
    return max(0.0, min(float(value) * scale, 100.0))


def _inverse_capped_score(raw_value: object, *, scale: float) -> float | None:
    value = _normalize_number(raw_value)
    if value is None:
        return None
    return max(0.0, min(100.0 - (float(value) * scale), 100.0))


def _gap_score(raw_gap: object) -> float | None:
    gap = _normalize_number(raw_gap)
    if gap is None:
        return None
    return max(0.0, min(50 + float(gap), 100.0))


def _penalty_score(raw_count: object, *, penalty: float) -> float | None:
    count = _normalize_number(raw_count)
    if count is None:
        return None
    return max(0.0, min(100 - float(count) * penalty, 100.0))


def _scale_to_100(raw_value: object, maximum: float) -> float | None:
    value = _normalize_number(raw_value)
    if value is None:
        return None
    if maximum <= 0:
        return None
    return max(0.0, min(float(value) / maximum * 100, 100.0))


def _time_window_score(raw_value: object, *, target: float, tolerance: float) -> float | None:
    value = _normalize_number(raw_value)
    if value is None or tolerance <= 0:
        return None
    return max(0.0, min(100.0 - (abs(float(value) - target) / tolerance * 100), 100.0))
