import re

import pytest

from student_behavior_etl.io import validate_required_columns
from student_behavior_etl.reporting import WarningCollector


def test_warning_collector_uses_frozen_reason_keys() -> None:
    collector = WarningCollector()
    collector.bump_dropped_attendance("missing_student_id")
    collector.bump_dropped_attendance("invalid_term_fields")
    collector.bump_dropped_final("missing_major_name")
    collector.add_source_status("考勤汇总.xlsx", "used", 3, "attendance rows loaded")

    payload = collector.to_payload(output_file="out.csv")

    assert payload["dropped_attendance_rows"]["missing_student_id"] == 1
    assert payload["dropped_attendance_rows"]["invalid_term_fields"] == 1
    assert payload["dropped_final_rows"]["missing_major_name"] == 1
    assert payload["source_file_status"][0]["source_file"] == "考勤汇总.xlsx"
    assert payload["source_file_status"][0]["status"] == "used"
    assert payload["source_file_status"][0]["rows_read"] == 3
    assert payload["output_file"] == "out.csv"
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", payload["generated_at"])
    assert payload["degraded_sources"] == []


def test_warning_collector_emits_zero_for_untouched_frozen_keys() -> None:
    payload = WarningCollector().to_payload(output_file="out.csv")

    assert payload["dropped_attendance_rows"]["missing_student_id"] == 0
    assert payload["dropped_attendance_rows"]["invalid_term_fields"] == 0
    assert payload["dropped_final_rows"]["missing_major_name"] == 0


def test_warning_collector_rejects_unknown_reason_keys() -> None:
    collector = WarningCollector()

    with pytest.raises(ValueError, match="unknown warning reason"):
        collector.bump_dropped_attendance("missing_studentid")

    with pytest.raises(ValueError, match="unknown warning reason"):
        collector.bump_dropped_final("major_missing")


def test_warning_collector_serializes_degraded_sources_without_aliasing() -> None:
    collector = WarningCollector()
    collector.add_source_status("上网统计.xlsx", "degraded", 12, "missing frozen term fields")
    collector.degraded_sources.append(
        {
            "source_file": "上网统计.xlsx",
            "reason": "missing frozen term fields",
            "excluded_row_count": 12,
            "affected_student_count": 3,
            "tjny_min": "2024-01",
            "tjny_max": "2024-06",
        }
    )

    payload = collector.to_payload(output_file="out.csv")
    payload["source_file_status"][0]["status"] = "tampered"
    payload["degraded_sources"][0]["reason"] = "tampered"

    second_payload = collector.to_payload(output_file="out.csv")

    assert second_payload["source_file_status"][0]["status"] == "degraded"
    assert second_payload["degraded_sources"][0]["reason"] == "missing frozen term fields"


def test_warning_collector_rejects_malformed_degraded_source() -> None:
    collector = WarningCollector()
    collector.degraded_sources.append(
        {
            "source_file": "上网统计.xlsx",
            "reason": "missing frozen term fields",
        }
    )

    with pytest.raises(ValueError, match="malformed degraded source"):
        collector.to_payload(output_file="out.csv")


def test_warning_collector_rejects_malformed_source_status() -> None:
    collector = WarningCollector()
    collector.source_file_status.append(
        {
            "source_file": "考勤汇总.xlsx",
            "status": "used",
            "rows_read": 3,
        }
    )

    with pytest.raises(ValueError, match="malformed source status"):
        collector.to_payload(output_file="out.csv")


def test_warning_collector_rejects_invalid_payload_value_types() -> None:
    collector = WarningCollector()
    collector.add_source_status("考勤汇总.xlsx", "used", 3, "attendance rows loaded")
    collector.source_file_status[0]["rows_read"] = "3"

    with pytest.raises(ValueError, match="invalid source status value"):
        collector.to_payload(output_file="out.csv")


def test_warning_collector_rejects_invalid_degraded_source_value_types() -> None:
    collector = WarningCollector()
    collector.degraded_sources.append(
        {
            "source_file": "上网统计.xlsx",
            "reason": "missing frozen term fields",
            "excluded_row_count": "12",
            "affected_student_count": 3,
            "tjny_min": "2024-01",
            "tjny_max": "2024-06",
        }
    )

    with pytest.raises(ValueError, match="invalid degraded source value"):
        collector.to_payload(output_file="out.csv")


def test_validate_required_columns_rejects_missing_columns() -> None:
    with pytest.raises(ValueError, match="missing required columns"):
        validate_required_columns(["XH", "XN"], {"XH", "XN", "XQ"})
