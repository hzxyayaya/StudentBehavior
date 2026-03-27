import pandas as pd
import pytest

from student_behavior_model_stubs.io import read_features, validate_required_columns


def test_validate_required_columns_rejects_missing_fields() -> None:
    frame = pd.DataFrame({"student_id": ["1"], "term_key": ["2023-1"]})
    with pytest.raises(ValueError, match="missing required columns"):
        validate_required_columns(frame, {"student_id", "term_key", "risk_label"})


def test_read_features_requires_tabular_export_not_excel_name_guessing(tmp_path) -> None:
    export_path = tmp_path / "student_results.xlsx"
    export_path.write_text(
        "\n".join(
            [
                "student_id,term_key,major_name,risk_label,avg_course_score,failed_course_count,attendance_normal_rate",
                "1,2023-1,软件工程,1,88,0,0.95",
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="tabular export"):
        read_features(export_path)


def test_optional_draft_source_columns_may_be_null(tmp_path) -> None:
    export_path = tmp_path / "student_results.csv"
    export_path.write_text(
        "\n".join(
            [
                "student_id,term_key,major_name,risk_label,avg_course_score,failed_course_count,attendance_normal_rate,major_rank_pct",
                "1,2023-1,软件工程,1,88,0,,",
            ]
        ),
        encoding="utf-8",
    )

    frame = read_features(export_path)

    assert list(frame.columns) == [
        "student_id",
        "term_key",
        "major_name",
        "risk_label",
        "avg_course_score",
        "failed_course_count",
        "attendance_normal_rate",
        "major_rank_pct",
    ]
    assert pd.isna(frame.loc[0, "attendance_normal_rate"])
    assert pd.isna(frame.loc[0, "major_rank_pct"])
