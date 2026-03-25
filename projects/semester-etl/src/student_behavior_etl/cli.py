from __future__ import annotations

import argparse
from pathlib import Path

from student_behavior_etl.build_semester_features import build_semester_feature_frame
from student_behavior_etl.config import DefaultPaths, build_default_paths
from student_behavior_etl.io import read_excel_required, write_warning_json
from student_behavior_etl.reporting import WarningCollector

_STUDENT_SOURCE = "学生基本信息.xlsx"
_ATTENDANCE_SOURCE = "考勤汇总.xlsx"
_INTERNET_SOURCE = "上网统计.xlsx"


def _load_source_status(collector: WarningCollector, source_file: str, rows_read: int, notes: str) -> None:
    collector.add_source_status(source_file, "used", rows_read, notes)


def run_build(paths: DefaultPaths) -> dict[str, object]:
    collector = WarningCollector()

    student_df = read_excel_required(paths.input_dir / _STUDENT_SOURCE, {"XH", "ZYM"})
    _load_source_status(collector, _STUDENT_SOURCE, len(student_df), "student dimension loaded")

    attendance_df = read_excel_required(paths.input_dir / _ATTENDANCE_SOURCE, {"XH", "XN", "XQ"})
    _load_source_status(collector, _ATTENDANCE_SOURCE, len(attendance_df), "attendance rows loaded")

    internet_df = read_excel_required(
        paths.input_dir / _INTERNET_SOURCE,
        {"XSBH", "XN", "XQ", "TJNY", "SWLJSC"},
    )

    result = build_semester_feature_frame(attendance_df, student_df, internet_df, collector)

    degraded_internet = next(
        (record for record in collector.degraded_sources if record["source_file"] == _INTERNET_SOURCE),
        None,
    )
    collector.add_source_status(
        _INTERNET_SOURCE,
        "degraded" if degraded_internet else "used",
        len(internet_df),
        degraded_internet["reason"] if degraded_internet else "internet rows aggregated by frozen XN/XQ",
    )

    paths.output_dir.mkdir(parents=True, exist_ok=True)
    result.to_csv(paths.output_csv, index=False, encoding="utf-8-sig")
    write_warning_json(paths.output_warning_json, collector.to_payload(output_file=str(paths.output_csv)))

    return {
        "sources_read": [_STUDENT_SOURCE, _ATTENDANCE_SOURCE, _INTERNET_SOURCE],
        "rows_written": int(len(result)),
        "student_count": int(result["student_id"].nunique()) if not result.empty else 0,
        "term_count": int(result["term_key"].nunique()) if not result.empty else 0,
        "dropped_attendance_rows": int(sum(collector.dropped_attendance_rows.values())),
        "internet_source_degraded": degraded_internet is not None,
        "warning_file": str(paths.output_warning_json),
    }


def _print_summary(summary: dict[str, object]) -> None:
    print(f"sources_read={', '.join(summary['sources_read'])}")
    print(f"rows_written={summary['rows_written']}")
    print(f"student_count={summary['student_count']}")
    print(f"term_count={summary['term_count']}")
    print(f"dropped_attendance_rows={summary['dropped_attendance_rows']}")
    print(f"internet_source_degraded={summary['internet_source_degraded']}")
    print(f"warning_file={summary['warning_file']}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="semester-features")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("build")

    args = parser.parse_args(argv)
    if args.command == "build":
        summary = run_build(build_default_paths(Path.cwd()))
        _print_summary(summary)
        return 0
    return 1
