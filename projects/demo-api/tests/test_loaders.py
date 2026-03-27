import json
from pathlib import Path

import pandas as pd
import pytest

from student_behavior_demo_api.loaders import load_json_records
from student_behavior_demo_api.loaders import load_student_results
from student_behavior_demo_api.loaders import validate_model_summary_payload
from student_behavior_demo_api.loaders import validate_overview_payload
from student_behavior_demo_api.loaders import validate_student_results_columns


def test_validate_student_results_columns_rejects_missing_fields() -> None:
    frame = pd.DataFrame({"student_id": ["20230001"], "term_key": ["2023-1"]})
    with pytest.raises(ValueError, match="missing required columns"):
        validate_student_results_columns(frame)


def test_load_student_results_raises_when_file_missing(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_student_results(tmp_path / "missing.csv")


def test_validate_overview_requires_term_buckets() -> None:
    payload = {
        "term_buckets": {"2023-1": {}},
        "student_count": 10,
        "risk_distribution": {},
        "quadrant_distribution": {},
    }
    with pytest.raises(ValueError, match="missing required keys"):
        validate_overview_payload(payload)


def test_validate_overview_accepts_complete_payload() -> None:
    payload = {
        "term_buckets": {"2023-1": {}},
        "student_count": 10,
        "risk_distribution": {},
        "quadrant_distribution": {},
        "major_risk_summary": [],
        "trend_summary": [],
    }
    assert validate_overview_payload(payload) == payload


def test_validate_model_summary_requires_required_fields() -> None:
    payload = {"cluster_method": "kmeans"}
    with pytest.raises(ValueError, match="missing required keys"):
        validate_model_summary_payload(payload)


def test_load_student_results_reads_csv(tmp_path: Path) -> None:
    path = tmp_path / "student_results.csv"
    frame = pd.DataFrame(
        [
            {
                "student_id": 20230001,
                "term_key": "2023-1",
                "student_name": "Alice",
                "major_name": "CS",
                "quadrant_label": "自律共鸣型",
                "risk_probability": 0.12,
                "risk_level": "low",
                "dimension_scores_json": "{\"engagement\": 0.9}",
            }
        ]
    )
    frame.to_csv(path, index=False)

    loaded = load_student_results(path)

    pd.testing.assert_frame_equal(loaded, frame)


def test_load_json_records_reads_json(tmp_path: Path) -> None:
    path = tmp_path / "overview.json"
    payload = {
        "term_buckets": {"2023-1": {}},
        "student_count": 10,
        "risk_distribution": {},
        "quadrant_distribution": {},
        "major_risk_summary": [],
        "trend_summary": [],
    }
    path.write_text(json.dumps(payload), encoding="utf-8")

    records = load_json_records(path)

    assert records == [payload]


def test_load_json_records_reads_jsonl(tmp_path: Path) -> None:
    path = tmp_path / "reports.jsonl"
    records = [
        {"student_id": "20230001", "note": "first"},
        {"student_id": "20230002", "note": "second"},
    ]
    path.write_text("\n".join(json.dumps(record) for record in records), encoding="utf-8")

    loaded = load_json_records(path)

    assert loaded == records
