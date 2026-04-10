from __future__ import annotations

import json
import math
import pickle
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import pytest

import student_behavior_model_stubs.cli as cli_module
from student_behavior_model_stubs.evaluate_risk_model import _compute_auc
from student_behavior_model_stubs.evaluate_risk_model import _compute_binary_metrics
from student_behavior_model_stubs.evaluate_risk_model import evaluate_risk_model
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
                }
            )
    pd.DataFrame(rows).to_csv(path, index=False, encoding="utf-8")


def _write_unsplit_labeled_csv(path: Path) -> None:
    pd.DataFrame(
        [
            {
                "student_id": "20240001",
                "term_key": "2024-1",
                "major_name": "软件工程",
                "risk_label": 1,
                "avg_course_score": 65.0,
                "failed_course_count": 2,
                "attendance_normal_rate": 0.72,
                "sign_event_count": 5,
                "selected_course_count": 5,
                "library_visit_count": 3,
            },
            {
                "student_id": "20240002",
                "term_key": "2024-1",
                "major_name": "软件工程",
                "risk_label": 0,
                "avg_course_score": 82.0,
                "failed_course_count": 0,
                "attendance_normal_rate": 0.95,
                "sign_event_count": 9,
                "selected_course_count": 7,
                "library_visit_count": 6,
            },
        ]
    ).to_csv(path, index=False, encoding="utf-8")


def _write_explicit_holdout_csv(path: Path) -> None:
    holdout_rows: list[dict[str, object]] = []
    probabilities = [0.9, 0.1, 0.1, 0.1, 0.1, 0.1, 0.2]
    labels = [1, 1, 1, 1, 1, 1, 0]
    for index, (probability, label) in enumerate(zip(probabilities, labels, strict=True), start=1):
        holdout_rows.append(
            {
                "student_id": f"2024T{index:04d}",
                "term_key": "2024-2",
                "major_name": "软件工程",
                "risk_label": label,
                "avg_course_score": math.log(probability / (1.0 - probability)),
                "failed_course_count": 1 if label else 0,
                "attendance_normal_rate": 0.75,
                "sign_event_count": 4,
                "selected_course_count": 5,
                "library_visit_count": 2,
                "dataset_split": "test",
            }
        )

    pd.DataFrame(holdout_rows).to_csv(path, index=False, encoding="utf-8")


def _write_manual_model(path: Path, *, trained_at: str = "2024-01-02T03:04:05Z") -> None:
    payload = {
        "model_name": "manual-risk-model",
        "target_label": "risk_label",
        "trained_at": trained_at,
        "intercept": 0.0,
        "feature_columns": ["avg_course_score"],
        "features": [
            {
                "feature": "avg_course_score",
                "median": 0.0,
                "center": 0.0,
                "scale": 1.0,
                "coefficient": 1.0,
            }
        ],
    }
    path.write_bytes(pickle.dumps(payload))


def test_evaluate_risk_model_uses_persisted_holdout_split_and_copies_feature_importance(
    tmp_path: Path,
) -> None:
    input_csv = tmp_path / "semester_features.csv"
    training_output_dir = tmp_path / "artifacts" / "model_training"
    evaluation_output_dir = tmp_path / "artifacts" / "model_evaluation"
    _write_grouped_training_csv(input_csv)

    train_risk_model(
        input_csv,
        output_dir=training_output_dir,
        trained_at=datetime(2024, 1, 2, 3, 4, 5, tzinfo=timezone.utc),
    )

    summary = evaluate_risk_model(
        input_csv,
        training_output_dir / "risk_model.pkl",
        output_dir=evaluation_output_dir,
        evaluated_at=datetime(2024, 2, 3, 4, 5, 6, tzinfo=timezone.utc),
    )

    metrics_path = evaluation_output_dir / "risk_metrics.json"
    feature_importance_path = evaluation_output_dir / "feature_importance.csv"
    metrics_payload = json.loads(metrics_path.read_text(encoding="utf-8"))

    assert metrics_path.exists()
    assert feature_importance_path.exists()
    assert summary["sample_count"] == 2
    assert summary["positive_sample_count"] == 2
    assert summary["negative_sample_count"] == 0
    assert summary["metrics_path"] == str(metrics_path)
    assert summary["feature_importance_path"] == str(feature_importance_path)
    assert metrics_payload == {
        "model_name": "deterministic-risk-scorecard-v1",
        "task_type": "binary_classification",
        "target_label": "risk_label",
        "sample_count": 2,
        "positive_sample_count": 2,
        "negative_sample_count": 0,
        "auc": None,
        "accuracy": 1.0,
        "precision": 1.0,
        "recall": 1.0,
        "f1": 1.0,
        "trained_at": "2024-01-02T03:04:05Z",
        "evaluated_at": "2024-02-03T04:05:06Z",
    }
    assert feature_importance_path.read_text(encoding="utf-8") == (
        training_output_dir / "feature_importance.csv"
    ).read_text(encoding="utf-8")


def test_evaluate_risk_model_uses_explicit_dataset_split_for_non_perfect_metrics(
    tmp_path: Path,
) -> None:
    input_csv = tmp_path / "explicit_holdout_features.csv"
    output_dir = tmp_path / "artifacts" / "model_evaluation"
    model_path = tmp_path / "manual_risk_model.pkl"
    _write_explicit_holdout_csv(input_csv)
    _write_manual_model(model_path)

    summary = evaluate_risk_model(
        input_csv,
        model_path,
        output_dir=output_dir,
        evaluated_at=datetime(2024, 2, 3, 4, 5, 6, tzinfo=timezone.utc),
    )

    metrics_payload = json.loads((output_dir / "risk_metrics.json").read_text(encoding="utf-8"))

    assert summary == {
        "sample_count": 7,
        "positive_sample_count": 6,
        "negative_sample_count": 1,
        "auc": 0.1667,
        "accuracy": 0.2857,
        "precision": 1.0,
        "recall": 0.1667,
        "f1": 0.2857,
        "trained_at": "2024-01-02T03:04:05Z",
        "evaluated_at": "2024-02-03T04:05:06Z",
        "model_path": str(model_path),
        "metrics_path": str(output_dir / "risk_metrics.json"),
        "feature_importance_path": None,
    }
    assert metrics_payload["auc"] == 0.1667
    assert metrics_payload["accuracy"] == 0.2857
    assert metrics_payload["precision"] == 1.0
    assert metrics_payload["recall"] == 0.1667
    assert metrics_payload["f1"] == 0.2857


def test_evaluate_risk_model_rejects_ambiguous_unsplit_labeled_csv(tmp_path: Path) -> None:
    input_csv = tmp_path / "unsplit_labeled_features.csv"
    model_path = tmp_path / "manual_risk_model.pkl"
    _write_unsplit_labeled_csv(input_csv)
    _write_manual_model(model_path)

    with pytest.raises(
        ValueError,
        match="held-out split rows via dataset_split or persisted training split signal",
    ):
        evaluate_risk_model(input_csv, model_path, output_dir=tmp_path / "artifacts" / "model_evaluation")


def test_metric_helpers_cover_zero_denominator_branches_and_auc_none() -> None:
    zero_precision_metrics = _compute_binary_metrics(
        pd.Series([1, 0, 1], dtype="int64"),
        pd.Series([0.1, 0.2, 0.3], dtype="float64"),
    )
    no_positive_label_metrics = _compute_binary_metrics(
        pd.Series([0, 0, 0], dtype="int64"),
        pd.Series([0.7, 0.6, 0.4], dtype="float64"),
    )

    assert zero_precision_metrics == {
        "accuracy": 0.3333,
        "precision": 0.0,
        "recall": 0.0,
        "f1": 0.0,
    }
    assert no_positive_label_metrics == {
        "accuracy": 0.3333,
        "precision": 0.0,
        "recall": 0.0,
        "f1": 0.0,
    }
    assert _compute_auc(
        pd.Series([0, 0, 0], dtype="int64"),
        pd.Series([0.7, 0.6, 0.4], dtype="float64"),
    ) is None


def test_main_evaluate_risk_model_prints_summary_lines(tmp_path: Path, capsys) -> None:
    input_csv = tmp_path / "semester_features.csv"
    training_output_dir = tmp_path / "artifacts" / "model_training"
    evaluation_output_dir = tmp_path / "artifacts" / "model_evaluation"
    _write_grouped_training_csv(input_csv)

    train_risk_model(input_csv, output_dir=training_output_dir)

    exit_code = cli_module.main(
        [
            "evaluate-risk-model",
            str(input_csv),
            str(training_output_dir / "risk_model.pkl"),
            "--output-dir",
            str(evaluation_output_dir),
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "sample_count=2" in captured.out
    assert "positive_sample_count=2" in captured.out
    assert "negative_sample_count=0" in captured.out
    assert "auc=None" in captured.out
    assert "accuracy=1.0" in captured.out
    assert "precision=1.0" in captured.out
    assert "recall=1.0" in captured.out
    assert "f1=1.0" in captured.out
    assert f"feature_importance_path={evaluation_output_dir / 'feature_importance.csv'}" in captured.out
    assert f"metrics_path={evaluation_output_dir / 'risk_metrics.json'}" in captured.out
