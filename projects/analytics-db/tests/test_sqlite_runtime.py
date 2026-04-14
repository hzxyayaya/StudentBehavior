from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pandas as pd

from student_behavior_analytics_db.sqlite_runtime import build_sqlite_runtime_db


def test_build_sqlite_runtime_db_imports_current_artifacts(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    semester_dir = repo_root / "artifacts" / "semester_features"
    model_stubs_dir = repo_root / "artifacts" / "model_stubs"
    semester_dir.mkdir(parents=True)
    model_stubs_dir.mkdir(parents=True)

    pd.DataFrame(
        [
            {"student_id": "20230001", "term_key": "2024-2", "major_name": "软件工程", "risk_label_binary": 1},
            {"student_id": "20230002", "term_key": "2024-2", "major_name": "计算机科学与技术", "risk_label_binary": 0},
        ]
    ).to_csv(semester_dir / "v1_semester_features.csv", index=False, encoding="utf-8-sig")

    pd.DataFrame(
        [
            {
                "student_id": "20230001",
                "term_key": "2024-2",
                "student_name": "Alice",
                "major_name": "软件工程",
                "group_segment": "课堂参与薄弱组",
                "risk_probability": 0.73,
                "risk_level": "较高风险",
                "dimension_scores_json": "[]",
            }
        ]
    ).to_csv(model_stubs_dir / "v1_student_results.csv", index=False, encoding="utf-8-sig")

    (model_stubs_dir / "v1_student_reports.jsonl").write_text(
        json.dumps(
            {
                "student_id": "20230001",
                "term_key": "2024-2",
                "report_text": "demo report",
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    (model_stubs_dir / "v1_model_summary.json").write_text(
        json.dumps(
            {
                "cluster_method": "stub-eight-dimension-group-rules",
                "risk_model": "deterministic-risk-scorecard-v1",
                "target_label": "risk_label_binary",
                "auc": 0.9772,
                "updated_at": "2026-04-11T17:34:46",
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (model_stubs_dir / "v1_overview_by_term.json").write_text(
        json.dumps(
            {
                "student_count": 1,
                "risk_distribution": {"high": 0, "medium": 1, "low": 0},
                "group_distribution": {"课堂参与薄弱组": 1},
                "major_risk_summary": [],
                "trend_summary": {"terms": [{"term_key": "2024-2"}]},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (model_stubs_dir / "v1_warnings.json").write_text(
        json.dumps(
            {
                "generated_at": "2026-04-14T09:00:00Z",
                "input_row_count": 2,
                "output_row_count": 1,
                "dropped_row_count": 1,
                "null_metric_summary": {},
                "notes": ["build completed"],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    summary = build_sqlite_runtime_db(repo_root=repo_root)

    sqlite_path = Path(summary["sqlite_path"])
    assert sqlite_path.exists()
    assert summary["student_term_features_count"] == 2
    assert summary["student_results_count"] == 1
    assert summary["student_reports_count"] == 1
    assert summary["model_summary_count"] == 1
    assert summary["overview_count"] == 1
    assert summary["warnings_count"] == 1

    connection = sqlite3.connect(sqlite_path)
    try:
        feature_count = connection.execute("select count(*) from runtime_student_term_features").fetchone()[0]
        result_count = connection.execute("select count(*) from runtime_student_results").fetchone()[0]
        report_count = connection.execute("select count(*) from runtime_student_reports").fetchone()[0]
        summary_count = connection.execute("select count(*) from runtime_model_summary").fetchone()[0]
        overview_count = connection.execute("select count(*) from runtime_overview").fetchone()[0]
        warnings_count = connection.execute("select count(*) from runtime_warnings").fetchone()[0]
        result_payload = connection.execute(
            "select payload_json from runtime_student_results where student_id = '20230001' and term_key = '2024-2'"
        ).fetchone()[0]
    finally:
        connection.close()

    assert feature_count == 2
    assert result_count == 1
    assert report_count == 1
    assert summary_count == 1
    assert overview_count == 1
    assert warnings_count == 1
    assert json.loads(result_payload)["group_segment"] == "课堂参与薄弱组"
