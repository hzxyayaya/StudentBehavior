from __future__ import annotations

from pathlib import Path

import pandas as pd

from student_behavior_analytics_db.build_demo_features_from_excels import (
    _add_raw_dimension_scores,
    _aggregate_access_control_metrics,
    _aggregate_appraisal_support_metrics,
    _aggregate_network_usage_metrics,
    _aggregate_physical_support_metrics,
    _aggregate_library_support_metrics,
    _first_value,
    _normalize_number,
    _pick_student_id,
    _read_excel_rows,
)


def _term_rank(term_key: object) -> int:
    text = str(term_key).strip()
    if not text or "-" not in text:
        return -1
    year, _, term = text.partition("-")
    if not (year.isdigit() and term.isdigit()):
        return -1
    return int(year) * 10 + int(term)


def _carry_forward_to_feature_terms(features: pd.DataFrame, extra_frame: pd.DataFrame) -> pd.DataFrame:
    if extra_frame.empty:
        return extra_frame
    metric_columns = [column for column in extra_frame.columns if column not in {"student_id", "term_key"}]
    key_frame = features.loc[:, ["student_id", "term_key"]].drop_duplicates().copy()
    key_frame["term_rank"] = key_frame["term_key"].map(_term_rank)
    source = extra_frame.copy()
    source["term_rank"] = source["term_key"].map(_term_rank)

    carried_parts: list[pd.DataFrame] = []
    for student_id, student_keys in key_frame.groupby("student_id", dropna=False):
        student_source = source.loc[source["student_id"] == student_id].sort_values("term_rank", kind="stable")
        if student_source.empty:
            continue
        latest_row = student_source.iloc[-1]
        for key_row in student_keys.sort_values("term_rank", kind="stable").itertuples(index=False):
            eligible = student_source.loc[student_source["term_rank"] <= key_row.term_rank]
            chosen = eligible.iloc[-1] if not eligible.empty else latest_row
            payload = {"student_id": key_row.student_id, "term_key": key_row.term_key}
            for column in metric_columns:
                payload[column] = chosen[column]
            carried_parts.append(pd.DataFrame([payload]))
    if not carried_parts:
        return extra_frame
    return pd.concat(carried_parts, ignore_index=True)


def _capped_score(value: object, scale: float) -> float | None:
    number = _normalize_number(value)
    if number is None:
        return None
    return max(0.0, min(100.0, float(number) * scale))


def _resolve_by_name_or_header(data_dir: Path, filename: str, usecols: tuple[str, ...]) -> Path:
    path = data_dir / filename
    if path.exists():
        return path
    expected = set(usecols)
    for candidate in sorted(data_dir.glob("*.xlsx")):
        try:
            header_frame = pd.read_excel(candidate, nrows=0, dtype=object)
        except Exception:
            continue
        if expected.issubset({str(column) for column in header_frame.columns}):
            return candidate
    raise FileNotFoundError(filename)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    data_dir = repo_root / "origin_data" / "数据集及类型"
    features_path = repo_root / "artifacts" / "semester_features" / "v1_semester_features.csv"

    features = pd.read_csv(features_path)
    official_student_ids = set(features["student_id"].dropna().astype(str).unique())
    overwrite_metric_columns = {
        "library_completed_visit_count",
        "avg_library_stay_minutes",
        "term_online_duration_sum",
        "monthly_online_duration_avg",
        "online_duration_vs_school_avg_gap",
        "late_return_count",
        "first_daily_access_time_avg",
        "first_daily_access_time_std",
        "late_return_ratio",
        "daily_access_time_variability",
        "physical_test_avg_score",
        "physical_test_pass_flag",
        "weekly_exercise_count_avg",
        "scholarship_amount_sum",
        "scholarship_level_score",
        "negative_status_alert_flag",
        "status_change_count",
    }

    online_path = _resolve_by_name_or_header(
        data_dir,
        "线上学习（综合表现）.xlsx",
        ("LOGIN_NAME", "XH", "XSBH", "USERNUM", "BFB"),
    )
    online_rows = _read_excel_rows(online_path, ("LOGIN_NAME", "XH", "XSBH", "USERNUM", "BFB"))
    online_records: list[dict[str, object]] = []
    for row in online_rows:
        student_id = _pick_student_id(
            row,
            "LOGIN_NAME",
            "XH",
            "XSBH",
            "USERNUM",
            official_student_ids=official_student_ids,
        )
        score = _normalize_number(_first_value(row, "BFB"))
        if student_id is None or score is None:
            continue
        online_records.append({"student_id": student_id, "platform_engagement_score": float(score)})
    if online_records:
        online_frame = (
            pd.DataFrame.from_records(online_records)
            .groupby("student_id", dropna=False)["platform_engagement_score"]
            .mean()
            .reset_index()
        )
        features = features.merge(online_frame, on="student_id", how="left", suffixes=("", "__online"))
        if "platform_engagement_score__online" in features.columns:
            existing = (
                features["platform_engagement_score"]
                if "platform_engagement_score" in features.columns
                else pd.Series([None] * len(features))
            )
            features["platform_engagement_score"] = existing.combine_first(
                features["platform_engagement_score__online"]
            )
            features = features.drop(columns=["platform_engagement_score__online"])

    for extra_frame in [
        _carry_forward_to_feature_terms(
            features,
            _aggregate_network_usage_metrics(data_dir, official_student_ids=official_student_ids),
        ),
        _carry_forward_to_feature_terms(
            features,
            _aggregate_access_control_metrics(data_dir, official_student_ids=official_student_ids),
        ),
        _carry_forward_to_feature_terms(
            features,
            _aggregate_library_support_metrics(data_dir, official_student_ids=official_student_ids),
        ),
        _carry_forward_to_feature_terms(
            features,
            _aggregate_physical_support_metrics(data_dir, official_student_ids=official_student_ids),
        ),
        _carry_forward_to_feature_terms(
            features,
            _aggregate_appraisal_support_metrics(data_dir, official_student_ids=official_student_ids),
        ),
    ]:
        if extra_frame.empty:
            continue
        features = features.merge(extra_frame, on=["student_id", "term_key"], how="left", suffixes=("", "__extra"))
        for column in list(features.columns):
            if not column.endswith("__extra"):
                continue
            base_column = column.removesuffix("__extra")
            if base_column in features.columns:
                if base_column in overwrite_metric_columns:
                    features[base_column] = features[column].combine_first(features[base_column])
                else:
                    features[base_column] = features[base_column].combine_first(features[column])
                features = features.drop(columns=[column])
            else:
                features = features.rename(columns={column: base_column})

    features = _add_raw_dimension_scores(features)
    class_fallback = features["sign_event_count"].apply(lambda value: _capped_score(value, scale=10))
    features["class_engagement_score_raw"] = features["class_engagement_score_raw"].combine_first(class_fallback)
    features = features.sort_values(["student_id", "term_key"], kind="stable").reset_index(drop=True)
    features.to_csv(features_path, index=False, encoding="utf-8-sig")

    raw_columns = [
        "academic_base_score_raw",
        "class_engagement_score_raw",
        "online_activeness_score_raw",
        "library_immersion_score_raw",
        "network_habits_score_raw",
        "daily_routine_boundary_score_raw",
        "physical_resilience_score_raw",
        "appraisal_status_alert_score_raw",
    ]
    print({"rows": len(features), "cols": len(features.columns)})
    print(features[raw_columns].notna().sum().to_dict())


if __name__ == "__main__":
    main()
