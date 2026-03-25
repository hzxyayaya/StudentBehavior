from __future__ import annotations

import pandas as pd

from student_behavior_etl.normalize import normalize_student_id, normalize_term_key


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


def build_semester_feature_frame(
    attendance_df: pd.DataFrame,
    student_df: pd.DataFrame,
    internet_df: pd.DataFrame | None,
    collector: object,
) -> pd.DataFrame:
    del internet_df, collector

    attendance = _normalize_attendance_frame(attendance_df)
    attendance = attendance.dropna(subset=["student_id", "term_key"])

    aggregated = (
        attendance.groupby(["student_id", "term_key"], as_index=False)
        .size()
        .rename(columns={"size": "attendance_record_count"})
    )

    dimension = build_student_dimension(student_df)
    result = aggregated.merge(dimension, how="left", on="student_id")
    result["internet_duration_sum"] = 0.0

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
