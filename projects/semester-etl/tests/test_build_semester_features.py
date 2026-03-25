from __future__ import annotations

import pandas as pd
import pytest

from student_behavior_etl.build_semester_features import (
    build_semester_feature_frame,
    build_student_dimension,
    normalize_major_name,
)
from student_behavior_etl.reporting import WarningCollector


def test_normalize_major_name_trims_and_drops_empty_values() -> None:
    assert normalize_major_name(None) is None
    assert normalize_major_name(pd.NA) is None
    assert normalize_major_name("   ") is None
    assert normalize_major_name("  信息安全  ") == "信息安全"


def test_builds_attendance_features_and_major_name() -> None:
    attendance = pd.DataFrame(
        [
            {"XH": "stu-2", "XN": "2023-2024", "XQ": 1},
            {"XH": "stu-1", "XN": "2023-2024", "XQ": 2},
            {"XH": "stu-1", "XN": "2023-2024", "XQ": 2},
        ]
    )
    students = pd.DataFrame(
        [
            {"XH": "stu-1", "ZYM": "信息安全"},
            {"XH": "stu-2", "ZYM": "电子信息工程"},
        ]
    )

    result = build_semester_feature_frame(
        attendance_df=attendance,
        student_df=students,
        internet_df=None,
        collector=WarningCollector(),
    )

    assert result.to_dict(orient="records") == [
        {
            "student_id": "stu-1",
            "term_key": "2023-2",
            "major_name": "信息安全",
            "attendance_record_count": 2,
            "internet_duration_sum": 0.0,
        },
        {
            "student_id": "stu-2",
            "term_key": "2023-1",
            "major_name": "电子信息工程",
            "attendance_record_count": 1,
            "internet_duration_sum": 0.0,
        },
    ]


def test_duplicate_student_major_conflict_hard_fails() -> None:
    students = pd.DataFrame(
        [
            {"XH": "stu-1", "ZYM": "信息安全"},
            {"XH": "stu-1", "ZYM": "电子信息工程"},
        ]
    )

    with pytest.raises(ValueError, match="conflicting major_name"):
        build_student_dimension(students)


def test_missing_major_name_rows_are_removed_from_dimension() -> None:
    students = pd.DataFrame(
        [
            {"XH": "stu-1", "ZYM": ""},
            {"XH": "stu-2", "ZYM": None},
            {"XH": "stu-3", "ZYM": "信息安全"},
        ]
    )

    result = build_student_dimension(students)

    assert result.to_dict(orient="records") == [
        {"student_id": "stu-3", "major_name": "信息安全"},
    ]


def test_invalid_attendance_rows_are_dropped_with_warning_counts() -> None:
    attendance = pd.DataFrame(
        [
            {"XH": "stu-1", "XN": "2023-2024", "XQ": 1},
            {"XH": " ", "XN": "2023-2024", "XQ": 1},
            {"XH": "stu-2", "XN": "2023-2024", "XQ": 9},
        ]
    )
    students = pd.DataFrame(
        [
            {"XH": "stu-1", "ZYM": "信息安全"},
            {"XH": "stu-2", "ZYM": "电子信息工程"},
        ]
    )
    collector = WarningCollector()

    result = build_semester_feature_frame(attendance, students, None, collector)

    assert len(result) == 1
    assert collector.dropped_attendance_rows["missing_student_id"] == 1
    assert collector.dropped_attendance_rows["invalid_term_fields"] == 1


def test_rows_without_major_name_are_dropped_and_counted() -> None:
    attendance = pd.DataFrame([{"XH": "stu-1", "XN": "2023-2024", "XQ": 1}])
    students = pd.DataFrame([{"XH": "stu-1", "ZYM": ""}])
    collector = WarningCollector()

    result = build_semester_feature_frame(attendance, students, None, collector)

    assert result.empty
    assert collector.dropped_final_rows["missing_major_name"] == 1


def test_internet_source_degrades_when_term_fields_are_missing() -> None:
    attendance = pd.DataFrame([{"XH": "stu-1", "XN": "2023-2024", "XQ": 1}])
    students = pd.DataFrame([{"XH": "stu-1", "ZYM": "信息安全"}])
    internet = pd.DataFrame(
        [
            {"XSBH": "stu-1", "XN": None, "XQ": None, "TJNY": "2023-03-01", "SWLJSC": 12.5},
            {"XSBH": "stu-1", "XN": None, "XQ": None, "TJNY": "2023-04-01", "SWLJSC": 2.5},
        ]
    )
    collector = WarningCollector()

    result = build_semester_feature_frame(attendance, students, internet, collector)

    assert result.loc[0, "internet_duration_sum"] == 0.0
    assert len(collector.degraded_sources) == 1
    degraded = collector.degraded_sources[0]
    assert degraded["source_file"] == "上网统计.xlsx"
    assert degraded["excluded_row_count"] == 2
    assert degraded["affected_student_count"] == 1
    assert degraded["tjny_min"] == "2023-03-01"
    assert degraded["tjny_max"] == "2023-04-01"


def test_internet_source_aggregates_when_frozen_term_fields_exist() -> None:
    attendance = pd.DataFrame([{"XH": "stu-1", "XN": "2023-2024", "XQ": 1}])
    students = pd.DataFrame([{"XH": "stu-1", "ZYM": "信息安全"}])
    internet = pd.DataFrame(
        [
            {"XSBH": "stu-1", "XN": "2023-2024", "XQ": 1, "TJNY": "2023-03-01", "SWLJSC": 12.5},
            {"XSBH": "stu-1", "XN": "2023-2024", "XQ": 1, "TJNY": "2023-04-01", "SWLJSC": 2.5},
        ]
    )
    collector = WarningCollector()

    result = build_semester_feature_frame(attendance, students, internet, collector)

    assert result.loc[0, "internet_duration_sum"] == 15.0
    assert collector.degraded_sources == []
