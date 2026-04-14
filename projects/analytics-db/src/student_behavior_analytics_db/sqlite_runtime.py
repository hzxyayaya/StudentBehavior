from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

import pandas as pd


def build_sqlite_runtime_db(
    *,
    repo_root: Path,
    sqlite_path: Path | None = None,
) -> dict[str, object]:
    database_path = sqlite_path or repo_root / "data" / "demo.sqlite3"
    database_path.parent.mkdir(parents=True, exist_ok=True)

    semester_features_path = repo_root / "artifacts" / "semester_features" / "v1_semester_features.csv"
    student_results_path = repo_root / "artifacts" / "model_stubs" / "v1_student_results.csv"
    student_reports_path = repo_root / "artifacts" / "model_stubs" / "v1_student_reports.jsonl"
    model_summary_path = repo_root / "artifacts" / "model_stubs" / "v1_model_summary.json"
    overview_path = repo_root / "artifacts" / "model_stubs" / "v1_overview_by_term.json"
    warnings_path = repo_root / "artifacts" / "model_stubs" / "v1_warnings.json"

    feature_frame = pd.read_csv(semester_features_path)
    results_frame = pd.read_csv(student_results_path)
    report_rows = _load_jsonl(student_reports_path)
    model_summary = json.loads(model_summary_path.read_text(encoding="utf-8"))
    overview = json.loads(overview_path.read_text(encoding="utf-8"))
    warnings = json.loads(warnings_path.read_text(encoding="utf-8"))

    connection = sqlite3.connect(database_path)
    try:
        _create_runtime_tables(connection)
        _replace_frame_rows(
            connection,
            table_name="runtime_student_term_features",
            frame=feature_frame,
            key_columns=("student_id", "term_key"),
        )
        _replace_frame_rows(
            connection,
            table_name="runtime_student_results",
            frame=results_frame,
            key_columns=("student_id", "term_key"),
        )
        _replace_json_rows(
            connection,
            table_name="runtime_student_reports",
            rows=report_rows,
            key_columns=("student_id", "term_key"),
        )
        _replace_single_payload(
            connection,
            table_name="runtime_model_summary",
            summary_key="current",
            payload=model_summary,
        )
        _replace_single_payload(
            connection,
            table_name="runtime_overview",
            summary_key="current",
            payload=overview,
        )
        _replace_single_payload(
            connection,
            table_name="runtime_warnings",
            summary_key="current",
            payload=warnings,
        )
        connection.commit()
    finally:
        connection.close()

    return {
        "sqlite_path": str(database_path),
        "student_term_features_count": int(len(feature_frame)),
        "student_results_count": int(len(results_frame)),
        "student_reports_count": int(len(report_rows)),
        "model_summary_count": 1,
        "overview_count": 1,
        "warnings_count": 1,
    }


def _create_runtime_tables(connection: sqlite3.Connection) -> None:
    script_path = Path(__file__).resolve().parents[2] / "sql" / "005_create_demo_runtime_tables.sql"
    connection.executescript(script_path.read_text(encoding="utf-8"))


def _replace_frame_rows(
    connection: sqlite3.Connection,
    *,
    table_name: str,
    frame: pd.DataFrame,
    key_columns: tuple[str, str],
) -> None:
    connection.execute(f"delete from {table_name}")
    rows = []
    for record in frame.to_dict(orient="records"):
        rows.append(
            (
                str(record[key_columns[0]]),
                str(record[key_columns[1]]),
                json.dumps(record, ensure_ascii=False, default=_json_default),
            )
        )
    connection.executemany(
        f"insert into {table_name} ({key_columns[0]}, {key_columns[1]}, payload_json) values (?, ?, ?)",
        rows,
    )


def _replace_json_rows(
    connection: sqlite3.Connection,
    *,
    table_name: str,
    rows: list[dict[str, Any]],
    key_columns: tuple[str, str],
) -> None:
    connection.execute(f"delete from {table_name}")
    payload_rows = [
        (
            str(row[key_columns[0]]),
            str(row[key_columns[1]]),
            json.dumps(row, ensure_ascii=False, default=_json_default),
        )
        for row in rows
    ]
    connection.executemany(
        f"insert into {table_name} ({key_columns[0]}, {key_columns[1]}, payload_json) values (?, ?, ?)",
        payload_rows,
    )


def _replace_single_payload(
    connection: sqlite3.Connection,
    *,
    table_name: str,
    summary_key: str,
    payload: dict[str, Any],
) -> None:
    connection.execute(f"delete from {table_name}")
    connection.execute(
        f"insert into {table_name} (summary_key, payload_json) values (?, ?)",
        (summary_key, json.dumps(payload, ensure_ascii=False, default=_json_default)),
    )


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows


def _json_default(value: Any) -> Any:
    if pd.isna(value):
        return None
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")
