from __future__ import annotations

import json
import pickle
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

import student_behavior_model_stubs.cli as cli_module
from student_behavior_model_stubs.train_risk_model import _assign_group_splits
from student_behavior_model_stubs.train_risk_model import train_risk_model


def _write_grouped_training_csv(path: Path) -> None:
    rows: list[dict[str, object]] = []
    student_specs = [
        ("20230001", 0, 88.0, 0, 0.97, 12, 8, 9),
        ("20230002", 0, 85.0, 0, 0.95, 11, 8, 8),
        ("20230003", 0, 79.0, 1, 0.88, 9, 7, 7),
        ("20230004", 1, 66.0, 2, 0.72, 5, 5, 4),
        ("20230005", 1, 61.0, 3, 0.61, 3, 4, 3),
        ("20230006", 1, 58.0, 4, 0.55, 2, 3, 2),
    ]
    for student_id, label, score, failures, attendance, signs, courses, visits in student_specs:
        for term_suffix, score_shift in [("2024-1", 0.0), ("2024-2", -2.0)]:
            rows.append(
                {
                    "student_id": student_id,
                    "term_key": term_suffix,
                    "major_name": "软件工程",
                    "risk_label": label,
                    "avg_course_score": score + score_shift,
                    "failed_course_count": failures,
                    "attendance_normal_rate": attendance,
                    "sign_event_count": signs,
                    "selected_course_count": courses,
                    "library_visit_count": visits,
                    "constant_metric": 1.0,
                    "mostly_missing_metric": 10.0 if student_id == "20230001" and term_suffix == "2024-1" else None,
                    "note_text": "ignore-me",
                }
            )
    pd.DataFrame(rows).to_csv(path, index=False, encoding="utf-8")


def _write_single_student_training_csv(path: Path) -> None:
    pd.DataFrame(
        [
            {
                "student_id": "20239999",
                "term_key": term_key,
                "major_name": "软件工程",
                "risk_label": risk_label,
                "avg_course_score": score,
                "failed_course_count": failed_course_count,
                "attendance_normal_rate": attendance,
                "sign_event_count": signs,
                "selected_course_count": courses,
                "library_visit_count": visits,
            }
            for term_key, risk_label, score, failed_course_count, attendance, signs, courses, visits in [
                ("2023-1", 0, 86.0, 0, 0.96, 10, 8, 8),
                ("2023-2", 0, 82.0, 0, 0.91, 9, 8, 7),
                ("2024-1", 1, 67.0, 2, 0.73, 5, 5, 4),
                ("2024-2", 1, 61.0, 3, 0.66, 4, 4, 3),
            ]
        ]
    ).to_csv(path, index=False, encoding="utf-8")


def test_train_risk_model_writes_registry_artifacts_with_grouped_student_split(tmp_path: Path) -> None:
    input_csv = tmp_path / "semester_features.csv"
    output_dir = tmp_path / "artifacts" / "model_training"
    _write_grouped_training_csv(input_csv)

    summary = train_risk_model(
        input_csv,
        output_dir=output_dir,
        trained_at=datetime(2024, 1, 2, 3, 4, 5, tzinfo=timezone.utc),
    )

    assert summary["split_strategy"] == "grouped_by_student_id"
    assert summary["feature_columns"] == [
        "avg_course_score",
        "failed_course_count",
        "attendance_normal_rate",
        "sign_event_count",
        "selected_course_count",
        "library_visit_count",
    ]
    assert summary["train_sample_count"] == 8
    assert summary["valid_sample_count"] == 2
    assert summary["test_sample_count"] == 2

    model_path = output_dir / "risk_model.pkl"
    metrics_path = output_dir / "risk_metrics.json"
    feature_importance_path = output_dir / "feature_importance.csv"
    training_config_path = output_dir / "training_config.json"

    for path in [model_path, metrics_path, feature_importance_path, training_config_path]:
        assert path.exists()

    model_payload = pickle.loads(model_path.read_bytes())
    metrics_payload = json.loads(metrics_path.read_text(encoding="utf-8"))
    training_config = json.loads(training_config_path.read_text(encoding="utf-8"))
    feature_importance = pd.read_csv(feature_importance_path)

    assert model_payload["model_name"] == "deterministic-risk-scorecard-v1"
    assert model_payload["target_label"] == "risk_label"
    assert model_payload["feature_columns"] == summary["feature_columns"]
    assert metrics_payload == {
        "model_name": "deterministic-risk-scorecard-v1",
        "task_type": "binary_classification",
        "target_label": "risk_label",
        "split_strategy": "grouped_by_student_id",
        "feature_count": 6,
        "train_sample_count": 8,
        "valid_sample_count": 2,
        "test_sample_count": 2,
        "train_accuracy": metrics_payload["train_accuracy"],
        "valid_accuracy": metrics_payload["valid_accuracy"],
        "test_accuracy": metrics_payload["test_accuracy"],
        "trained_at": "2024-01-02T03:04:05Z",
    }
    assert metrics_payload["train_accuracy"] >= 0.75
    assert training_config["feature_columns"] == summary["feature_columns"]
    assert training_config["deterministic"] is True
    assert training_config["split_strategy"] == "grouped_by_student_id"
    assert training_config["trained_at"] == "2024-01-02T03:04:05Z"
    assert list(feature_importance["feature"]) == summary["feature_columns"]
    assert feature_importance["importance"].is_monotonic_decreasing


def test_train_risk_model_falls_back_to_row_split_when_only_one_student_is_available(tmp_path: Path) -> None:
    input_csv = tmp_path / "single_student_features.csv"
    output_dir = tmp_path / "artifacts" / "model_training"
    _write_single_student_training_csv(input_csv)

    summary = train_risk_model(
        input_csv,
        output_dir=output_dir,
        trained_at=datetime(2024, 2, 3, 4, 5, 6, tzinfo=timezone.utc),
    )

    assert summary["split_strategy"] == "row_order_fallback"
    assert summary["train_sample_count"] == 2
    assert summary["valid_sample_count"] == 1
    assert summary["test_sample_count"] == 1

    training_config = json.loads((output_dir / "training_config.json").read_text(encoding="utf-8"))
    assert training_config["split_strategy"] == "row_order_fallback"


def test_assign_group_splits_keeps_trim_equivalent_student_ids_in_same_split() -> None:
    frame = pd.DataFrame(
        [
            {"student_id": "A", "term_key": "2024-1", "major_name": "软件工程", "risk_label": 0},
            {"student_id": " A ", "term_key": "2024-2", "major_name": "软件工程", "risk_label": 1},
            {"student_id": "B", "term_key": "2024-1", "major_name": "软件工程", "risk_label": 0},
            {"student_id": "C", "term_key": "2024-1", "major_name": "软件工程", "risk_label": 1},
        ]
    )

    split_frame, split_strategy = _assign_group_splits(frame)

    normalized_a_splits = set(
        split_frame.loc[
            split_frame["student_id"].astype(str).str.strip() == "A",
            "dataset_split",
        ]
    )

    assert split_strategy == "grouped_by_student_id"
    assert normalized_a_splits == {"train"}


def test_main_train_risk_model_prints_summary_lines(tmp_path: Path, capsys) -> None:
    input_csv = tmp_path / "semester_features.csv"
    output_dir = tmp_path / "artifacts" / "model_training"
    _write_grouped_training_csv(input_csv)

    exit_code = cli_module.main(["train-risk-model", str(input_csv), "--output-dir", str(output_dir)])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "split_strategy=grouped_by_student_id" in captured.out
    assert "feature_count=6" in captured.out
    assert f"model_path={output_dir / 'risk_model.pkl'}" in captured.out
    assert f"training_config_path={output_dir / 'training_config.json'}" in captured.out
