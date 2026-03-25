from __future__ import annotations

from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone


_DROPPED_ATTENDANCE_KEYS = ("missing_student_id", "invalid_term_fields")
_DROPPED_FINAL_KEYS = ("missing_major_name",)
_SOURCE_STATUS_KEYS = ("source_file", "status", "rows_read", "notes")
_DEGRADED_SOURCE_KEYS = (
    "source_file",
    "reason",
    "excluded_row_count",
    "affected_student_count",
    "tjny_min",
    "tjny_max",
)


def _validate_reason(reason: str, allowed: tuple[str, ...]) -> None:
    if reason not in allowed:
        raise ValueError(f"unknown warning reason: {reason}")


def _is_int_value(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _validate_source_status_values(record: dict[str, object]) -> None:
    if not isinstance(record["source_file"], str):
        raise ValueError("invalid source status value: source_file")
    if not isinstance(record["status"], str):
        raise ValueError("invalid source status value: status")
    if not _is_int_value(record["rows_read"]):
        raise ValueError("invalid source status value: rows_read")
    if not isinstance(record["notes"], str):
        raise ValueError("invalid source status value: notes")


def _validate_degraded_source_values(record: dict[str, object]) -> None:
    if not isinstance(record["source_file"], str):
        raise ValueError("invalid degraded source value: source_file")
    if not isinstance(record["reason"], str):
        raise ValueError("invalid degraded source value: reason")
    if not _is_int_value(record["excluded_row_count"]):
        raise ValueError("invalid degraded source value: excluded_row_count")
    if not _is_int_value(record["affected_student_count"]):
        raise ValueError("invalid degraded source value: affected_student_count")
    if record["tjny_min"] is not None and not isinstance(record["tjny_min"], str):
        raise ValueError("invalid degraded source value: tjny_min")
    if record["tjny_max"] is not None and not isinstance(record["tjny_max"], str):
        raise ValueError("invalid degraded source value: tjny_max")


def _copy_records(
    records: list[dict[str, object]],
    required_keys: tuple[str, ...],
    error_prefix: str,
    value_validator: Callable[[dict[str, object]], None],
) -> list[dict[str, object]]:
    copied_records: list[dict[str, object]] = []
    for record in records:
        missing_keys = [key for key in required_keys if key not in record]
        if missing_keys:
            raise ValueError(f"{error_prefix}: missing {', '.join(missing_keys)}")
        value_validator(record)
        copied_records.append({key: record[key] for key in required_keys})
    return copied_records


@dataclass
class WarningCollector:
    dropped_attendance_rows: Counter[str] = field(default_factory=Counter)
    dropped_final_rows: Counter[str] = field(default_factory=Counter)
    source_file_status: list[dict[str, object]] = field(default_factory=list)
    degraded_sources: list[dict[str, object]] = field(default_factory=list)

    def bump_dropped_attendance(self, reason: str) -> None:
        _validate_reason(reason, _DROPPED_ATTENDANCE_KEYS)
        self.dropped_attendance_rows[reason] += 1

    def bump_dropped_final(self, reason: str) -> None:
        _validate_reason(reason, _DROPPED_FINAL_KEYS)
        self.dropped_final_rows[reason] += 1

    def add_source_status(self, source_file: str, status: str, rows_read: int, notes: str) -> None:
        self.source_file_status.append(
            {
                "source_file": source_file,
                "status": status,
                "rows_read": rows_read,
                "notes": notes,
            }
        )

    def add_degraded_source(
        self,
        source_file: str,
        reason: str,
        excluded_row_count: int,
        affected_student_count: int,
        tjny_min: str | None,
        tjny_max: str | None,
    ) -> None:
        record = {
            "source_file": source_file,
            "reason": reason,
            "excluded_row_count": excluded_row_count,
            "affected_student_count": affected_student_count,
            "tjny_min": tjny_min,
            "tjny_max": tjny_max,
        }
        _validate_degraded_source_values(record)
        self.degraded_sources.append(record)

    def to_payload(self, output_file: str) -> dict[str, object]:
        return {
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "output_file": output_file,
            "source_file_status": _copy_records(
                self.source_file_status,
                _SOURCE_STATUS_KEYS,
                "malformed source status",
                _validate_source_status_values,
            ),
            "dropped_attendance_rows": {
                key: int(self.dropped_attendance_rows.get(key, 0)) for key in _DROPPED_ATTENDANCE_KEYS
            },
            "dropped_final_rows": {
                key: int(self.dropped_final_rows.get(key, 0)) for key in _DROPPED_FINAL_KEYS
            },
            "degraded_sources": _copy_records(
                self.degraded_sources,
                _DEGRADED_SOURCE_KEYS,
                "malformed degraded source",
                _validate_degraded_source_values,
            ),
        }
