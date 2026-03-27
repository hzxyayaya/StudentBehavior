from collections.abc import Iterable
from pathlib import Path

import pandas as pd

REQUIRED_FEATURE_COLUMNS = {
    "student_id",
    "term_key",
    "major_name",
    "risk_label",
    "avg_course_score",
    "failed_course_count",
    "attendance_normal_rate",
}


def validate_required_columns(frame: pd.DataFrame, required_columns: Iterable[str]) -> None:
    missing_columns = sorted(set(required_columns) - set(frame.columns))
    if missing_columns:
        missing_text = ", ".join(missing_columns)
        raise ValueError(f"missing required columns: {missing_text}")


def read_features(source: str | Path) -> pd.DataFrame:
    path = Path(source)
    if path.suffix.lower() != ".csv":
        raise ValueError("read_features expects a tabular export csv, not raw Excel")

    frame = pd.read_csv(path)
    validate_required_columns(frame, REQUIRED_FEATURE_COLUMNS)
    return frame
