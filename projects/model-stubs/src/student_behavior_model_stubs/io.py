from collections.abc import Iterable
from pathlib import Path

import pandas as pd

REQUIRED_FEATURE_COLUMNS = {
    "student_id",
    "term_key",
    "major_name",
}

OPTIONAL_FEATURE_COLUMNS = {
    "risk_label",
    "avg_course_score",
    "failed_course_count",
    "attendance_normal_rate",
    "sign_event_count",
    "selected_course_count",
    "library_visit_count",
}

KNOWN_FEATURE_COLUMNS = REQUIRED_FEATURE_COLUMNS | OPTIONAL_FEATURE_COLUMNS


def ensure_known_columns(frame: pd.DataFrame) -> pd.DataFrame:
    for column in sorted(KNOWN_FEATURE_COLUMNS):
        if column not in frame.columns:
            frame[column] = pd.NA
    return frame
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
    return ensure_known_columns(frame)
