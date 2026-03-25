from __future__ import annotations

import pandas as pd

from student_behavior_etl.normalize import normalize_student_id, normalize_term_key
from student_behavior_etl.reporting import WarningCollector


def normalize_major_name(raw: object) -> str | None:
    if raw is None or pd.isna(raw):
        return None

    value = str(raw).strip()
    return value or None


def build_student_dimension(student_df: pd.DataFrame) -> pd.DataFrame:
    dimension = student_df.loc[:, ["XH", "ZYM"]].copy()
    dimension["student_id"] = dimension["XH"].map(normalize_student_id)
    dimension["major_name"] = dimension["ZYM"].map(normalize_major_name)
    dimension = dimension.loc[:, ["student_id", "major_name"]]
    dimension = dimension.dropna(subset=["student_id", "major_name"])

    conflicting = (
        dimension.groupby("student_id")["major_name"].nunique(dropna=True).loc[lambda s: s > 1]
    )
    if not conflicting.empty:
        raise ValueError("conflicting major_name for student_id")

    return dimension.drop_duplicates(subset=["student_id", "major_name"]).reset_index(drop=True)


def _normalize_attendance_frame(attendance_df: pd.DataFrame) -> pd.DataFrame:
    normalized = attendance_df.loc[:, ["XH", "XN", "XQ"]].copy()
    normalized["student_id"] = normalized["XH"].map(normalize_student_id)
    normalized["term_key"] = normalized.apply(
        lambda row: normalize_term_key(row["XN"], row["XQ"]),
        axis=1,
    )
    return normalized


def _normalize_internet_frame(internet_df: pd.DataFrame) -> pd.DataFrame:
    normalized = internet_df.loc[:, ["XSBH", "XN", "XQ", "TJNY", "SWLJSC"]].copy()
    normalized["student_id"] = normalized["XSBH"].map(normalize_student_id)
    normalized["term_key"] = normalized.apply(
        lambda row: normalize_term_key(row["XN"], row["XQ"]),
        axis=1,
    )
    return normalized


def _degrade_internet_source(collector: WarningCollector, internet_df: pd.DataFrame) -> None:
    tjny_values = internet_df["TJNY"].dropna()
    tjny_min = None if tjny_values.empty else str(tjny_values.min())
    tjny_max = None if tjny_values.empty else str(tjny_values.max())
    affected_student_count = (
        internet_df["XSBH"].map(normalize_student_id).dropna().nunique()
    )
    collector.add_degraded_source(
        source_file="上网统计.xlsx",
        reason="all internet rows missing frozen XN/XQ; TJNY inference disabled",
        excluded_row_count=int(len(internet_df)),
        affected_student_count=int(affected_student_count),
        tjny_min=tjny_min,
        tjny_max=tjny_max,
    )


def build_semester_feature_frame(
    attendance_df: pd.DataFrame,
    student_df: pd.DataFrame,
    internet_df: pd.DataFrame | None,
    collector: WarningCollector,
) -> pd.DataFrame:
    attendance = _normalize_attendance_frame(attendance_df)
    missing_student_mask = attendance["student_id"].isna()
    invalid_term_mask = attendance["term_key"].isna() & ~missing_student_mask
    if missing_student_mask.any():
        collector.dropped_attendance_rows["missing_student_id"] += int(missing_student_mask.sum())
    if invalid_term_mask.any():
        collector.dropped_attendance_rows["invalid_term_fields"] += int(invalid_term_mask.sum())

    attendance = attendance.loc[~missing_student_mask & ~invalid_term_mask].copy()

    aggregated = (
        attendance.groupby(["student_id", "term_key"], as_index=False)
        .size()
        .rename(columns={"size": "attendance_record_count"})
    )

    dimension = build_student_dimension(student_df)
    result = aggregated.merge(dimension, how="left", on="student_id")
    missing_major_mask = result["major_name"].isna()
    if missing_major_mask.any():
        collector.dropped_final_rows["missing_major_name"] += int(missing_major_mask.sum())
    result = result.loc[~missing_major_mask].copy()

    result["internet_duration_sum"] = 0.0

    if internet_df is not None and not internet_df.empty:
        internet = _normalize_internet_frame(internet_df)
        valid_internet = internet.dropna(subset=["student_id", "term_key"]).copy()
        if valid_internet.empty:
            _degrade_internet_source(collector, internet_df)
        else:
            internet_agg = (
                valid_internet.groupby(["student_id", "term_key"], as_index=False)["SWLJSC"]
                .sum()
                .rename(columns={"SWLJSC": "internet_duration_sum"})
            )
            result = result.drop(columns=["internet_duration_sum"]).merge(
                internet_agg,
                how="left",
                on=["student_id", "term_key"],
            )
            result["internet_duration_sum"] = result["internet_duration_sum"].fillna(0.0)

    result = result.loc[
        :,
        [
            "student_id",
            "term_key",
            "major_name",
            "attendance_record_count",
            "internet_duration_sum",
        ],
    ]
    return result.sort_values(["student_id", "term_key"], kind="mergesort").reset_index(drop=True)
