from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone


_DROPPED_ATTENDANCE_KEYS = ("missing_student_id", "invalid_term_fields")
_DROPPED_FINAL_KEYS = ("missing_major_name",)


@dataclass
class WarningCollector:
    dropped_attendance_rows: Counter[str] = field(default_factory=Counter)
    dropped_final_rows: Counter[str] = field(default_factory=Counter)
    source_file_status: list[dict[str, object]] = field(default_factory=list)
    degraded_sources: list[dict[str, object]] = field(default_factory=list)

    def bump_dropped_attendance(self, reason: str) -> None:
        self.dropped_attendance_rows[reason] += 1

    def bump_dropped_final(self, reason: str) -> None:
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

    def to_payload(self, output_file: str) -> dict[str, object]:
        return {
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "output_file": output_file,
            "source_file_status": list(self.source_file_status),
            "dropped_attendance_rows": {
                key: int(self.dropped_attendance_rows.get(key, 0)) for key in _DROPPED_ATTENDANCE_KEYS
            },
            "dropped_final_rows": {
                key: int(self.dropped_final_rows.get(key, 0)) for key in _DROPPED_FINAL_KEYS
            },
            "degraded_sources": list(self.degraded_sources),
        }
