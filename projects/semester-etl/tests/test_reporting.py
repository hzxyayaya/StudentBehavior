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


def test_validate_required_columns_rejects_missing_columns() -> None:
    with pytest.raises(ValueError, match="missing required columns"):
        validate_required_columns(["XH", "XN"], {"XH", "XN", "XQ"})
