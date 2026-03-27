from pathlib import Path

import pandas as pd
import pytest

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
        "student_count": 10,
        "risk_distribution": {},
        "quadrant_distribution": {},
        "major_risk_summary": [],
        "trend_summary": [],
    }
    with pytest.raises(ValueError, match="missing required keys"):
        validate_overview_payload(payload)


def test_validate_model_summary_requires_required_fields() -> None:
    payload = {"cluster_method": "kmeans"}
    with pytest.raises(ValueError, match="missing required keys"):
        validate_model_summary_payload(payload)
