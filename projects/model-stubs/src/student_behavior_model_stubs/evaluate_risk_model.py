from __future__ import annotations

import json
import pickle
import shutil
from datetime import datetime
from pathlib import Path

import pandas as pd

from student_behavior_model_stubs.train_risk_model import _build_row_key_frame
from student_behavior_model_stubs.train_risk_model import _format_timestamp
from student_behavior_model_stubs.train_risk_model import _load_labeled_features
from student_behavior_model_stubs.train_risk_model import _predict_probabilities

_HOLDOUT_SPLIT_VALUES = {"test", "holdout", "eval", "evaluation"}


def _resolve_model_path(model_artifact: Path) -> Path:
    candidate = Path(model_artifact)
    if candidate.is_dir():
        return candidate / "risk_model.pkl"
    return candidate


def _resolve_output_dir(model_artifact: Path, output_dir: Path | None) -> Path:
    if output_dir is not None:
        return Path(output_dir)
    return _resolve_model_path(model_artifact).parent


def _load_model_payload(model_artifact: Path) -> dict[str, object]:
    model_path = _resolve_model_path(model_artifact)
    loaded = pickle.loads(model_path.read_bytes())
    if not isinstance(loaded, dict):
        raise ValueError("model artifact must contain a dictionary payload")
    return loaded


def _round_metric(value: float | None) -> float | None:
    if value is None:
        return None
    return round(float(value), 4)


def _compute_auc(labels: pd.Series, probabilities: pd.Series) -> float | None:
    label_values = labels.astype(int)
    positive_scores = probabilities.loc[label_values == 1].tolist()
    negative_scores = probabilities.loc[label_values == 0].tolist()
    if not positive_scores or not negative_scores:
        return None

    wins = 0.0
    for positive_score in positive_scores:
        for negative_score in negative_scores:
            if positive_score > negative_score:
                wins += 1.0
            elif positive_score == negative_score:
                wins += 0.5

    return _round_metric(wins / (len(positive_scores) * len(negative_scores)))


def _compute_binary_metrics(labels: pd.Series, probabilities: pd.Series) -> dict[str, float]:
    if len(labels) == 0:
        return {"accuracy": 0.0, "precision": 0.0, "recall": 0.0, "f1": 0.0}

    label_values = labels.astype(int)
    predictions = (probabilities >= 0.5).astype(int)

    true_positive = int(((predictions == 1) & (label_values == 1)).sum())
    true_negative = int(((predictions == 0) & (label_values == 0)).sum())
    false_positive = int(((predictions == 1) & (label_values == 0)).sum())
    false_negative = int(((predictions == 0) & (label_values == 1)).sum())

    accuracy = _round_metric((true_positive + true_negative) / len(label_values)) or 0.0
    precision = (
        _round_metric(true_positive / (true_positive + false_positive))
        if (true_positive + false_positive)
        else 0.0
    )
    recall = (
        _round_metric(true_positive / (true_positive + false_negative))
        if (true_positive + false_negative)
        else 0.0
    )
    f1 = _round_metric((2.0 * true_positive) / (2.0 * true_positive + false_positive + false_negative))
    if f1 is None:
        f1 = 0.0

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _select_explicit_holdout_rows(labeled_features: pd.DataFrame) -> pd.DataFrame | None:
    if "dataset_split" not in labeled_features.columns:
        return None

    split_values = labeled_features["dataset_split"].fillna("").astype(str).str.strip().str.lower()
    holdout_mask = split_values.isin(_HOLDOUT_SPLIT_VALUES)
    if not holdout_mask.any():
        raise ValueError("dataset_split column is present but contains no held-out rows")
    return labeled_features.loc[holdout_mask].reset_index(drop=True)


def _select_persisted_holdout_rows(
    labeled_features: pd.DataFrame,
    model_payload: dict[str, object],
) -> pd.DataFrame | None:
    split_payload = model_payload.get("evaluation_split")
    if not isinstance(split_payload, dict):
        return None

    row_keys = split_payload.get("rows")
    if not isinstance(row_keys, list) or not row_keys:
        return None

    holdout_keys = pd.DataFrame(row_keys)
    required_columns = {"student_id", "term_key", "row_ordinal"}
    if not required_columns.issubset(holdout_keys.columns):
        return None

    labeled_keys = _build_row_key_frame(labeled_features)
    labeled_index = pd.MultiIndex.from_frame(labeled_keys[["student_id", "term_key", "row_ordinal"]])
    holdout_index = pd.MultiIndex.from_frame(
        holdout_keys[["student_id", "term_key", "row_ordinal"]]
    ).unique()
    holdout_mask = labeled_index.isin(holdout_index)
    if int(holdout_mask.sum()) != len(holdout_index):
        raise ValueError("persisted training split signal did not match all held-out rows")
    return labeled_features.loc[holdout_mask].reset_index(drop=True)


def _select_evaluation_rows(
    labeled_features: pd.DataFrame,
    model_payload: dict[str, object],
) -> pd.DataFrame:
    explicit_holdout = _select_explicit_holdout_rows(labeled_features)
    if explicit_holdout is not None:
        return explicit_holdout

    persisted_holdout = _select_persisted_holdout_rows(labeled_features, model_payload)
    if persisted_holdout is not None:
        return persisted_holdout

    raise ValueError(
        "evaluation requires held-out split rows via dataset_split or persisted training split signal"
    )


def _copy_feature_importance(model_artifact: Path, output_dir: Path) -> str | None:
    source_path = _resolve_model_path(model_artifact).parent / "feature_importance.csv"
    if not source_path.exists():
        return None

    destination_path = output_dir / "feature_importance.csv"
    if source_path.resolve() != destination_path.resolve():
        shutil.copyfile(source_path, destination_path)
    return str(destination_path)


def evaluate_risk_model(
    features_csv: Path,
    model_artifact: Path,
    output_dir: Path | None = None,
    *,
    evaluated_at: datetime | None = None,
) -> dict[str, object]:
    model_payload = _load_model_payload(model_artifact)
    labeled_features, target_column = _load_labeled_features(features_csv)
    evaluation_features = _select_evaluation_rows(labeled_features, model_payload)
    probabilities = _predict_probabilities(evaluation_features, model_payload)

    resolved_target_column = str(model_payload.get("target_label") or target_column)
    if resolved_target_column not in evaluation_features.columns:
        raise ValueError(f"evaluation target label column '{resolved_target_column}' is missing")

    label_series = evaluation_features[resolved_target_column].astype(int)
    sample_count = int(len(evaluation_features))
    positive_sample_count = int((label_series == 1).sum())
    negative_sample_count = sample_count - positive_sample_count
    metrics = _compute_binary_metrics(label_series, probabilities)
    metrics_payload = {
        "model_name": model_payload.get("model_name"),
        "task_type": "binary_classification",
        "target_label": resolved_target_column,
        "sample_count": sample_count,
        "positive_sample_count": positive_sample_count,
        "negative_sample_count": negative_sample_count,
        "auc": _compute_auc(label_series, probabilities),
        "accuracy": metrics["accuracy"],
        "precision": metrics["precision"],
        "recall": metrics["recall"],
        "f1": metrics["f1"],
        "trained_at": model_payload.get("trained_at"),
        "evaluated_at": _format_timestamp(evaluated_at),
    }

    resolved_output_dir = _resolve_output_dir(model_artifact, output_dir)
    metrics_path = resolved_output_dir / "risk_metrics.json"
    resolved_output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(metrics_path, metrics_payload)
    feature_importance_path = _copy_feature_importance(model_artifact, resolved_output_dir)

    return {
        "sample_count": sample_count,
        "positive_sample_count": positive_sample_count,
        "negative_sample_count": negative_sample_count,
        "auc": metrics_payload["auc"],
        "accuracy": metrics_payload["accuracy"],
        "precision": metrics_payload["precision"],
        "recall": metrics_payload["recall"],
        "f1": metrics_payload["f1"],
        "trained_at": metrics_payload["trained_at"],
        "evaluated_at": metrics_payload["evaluated_at"],
        "model_path": str(_resolve_model_path(model_artifact)),
        "metrics_path": str(metrics_path),
        "feature_importance_path": feature_importance_path,
    }
