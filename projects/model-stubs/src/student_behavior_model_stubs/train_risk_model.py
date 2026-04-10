from __future__ import annotations

import json
import math
import pickle
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from student_behavior_model_stubs.io import read_features
from student_behavior_model_stubs.model_registry import ModelArtifactRegistry
from student_behavior_model_stubs.model_registry import build_default_model_registry

_MODEL_NAME = "deterministic-risk-scorecard-v1"
_TARGET_COLUMN = "risk_label"
_FALLBACK_TARGET_COLUMNS = ("risk_label_binary",)
_SPLIT_SEQUENCE = ("train", "valid", "test")
_EXCLUDED_FEATURE_COLUMNS = {
    "student_id",
    "term_key",
    "major_name",
    "dataset_split",
    _TARGET_COLUMN,
    *_FALLBACK_TARGET_COLUMNS,
}
_MIN_STABLE_NON_NULL_RATIO = 0.6


def resolve_checkout_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / ".git").exists():
            return parent
    raise RuntimeError("unable to locate checkout root")


def _format_timestamp(value: datetime | None) -> str:
    current = value or datetime.now(timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    return current.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _build_registry(output_dir: Path | None) -> ModelArtifactRegistry:
    if output_dir is None:
        return build_default_model_registry(resolve_checkout_root())

    output_dir = Path(output_dir)
    return ModelArtifactRegistry(
        artifact_dir=output_dir,
        model_path=output_dir / "risk_model.pkl",
        metrics_path=output_dir / "risk_metrics.json",
        feature_importance_path=output_dir / "feature_importance.csv",
        training_config_path=output_dir / "training_config.json",
    )


def _resolve_target_column(features: pd.DataFrame) -> str | None:
    for column in (_TARGET_COLUMN, *_FALLBACK_TARGET_COLUMNS):
        if column not in features.columns:
            continue
        numeric_labels = pd.to_numeric(features[column], errors="coerce")
        if numeric_labels.notna().any():
            return column
    return None


def _load_labeled_features(features_csv: Path) -> tuple[pd.DataFrame, str]:
    features = read_features(features_csv).copy()
    target_column = _resolve_target_column(features)
    if target_column is None:
        raise ValueError("training requires at least one labeled row with risk_label or risk_label_binary")

    numeric_labels = pd.to_numeric(features.get(target_column), errors="coerce")
    labeled = features.loc[numeric_labels.notna()].copy()
    if labeled.empty:
        raise ValueError("training requires at least one labeled row with risk_label or risk_label_binary")

    labeled.loc[:, target_column] = (numeric_labels.loc[labeled.index] > 0).astype(int)
    return labeled.sort_values(by=["student_id", "term_key"], kind="stable").reset_index(drop=True), target_column


def _split_counts(total_count: int) -> dict[str, int]:
    if total_count <= 0:
        return {"train": 0, "valid": 0, "test": 0}
    if total_count == 1:
        return {"train": 1, "valid": 0, "test": 0}
    if total_count == 2:
        return {"train": 1, "valid": 0, "test": 1}
    if total_count == 3:
        return {"train": 1, "valid": 1, "test": 1}

    valid_count = max(1, round(total_count * 0.15))
    test_count = max(1, round(total_count * 0.15))
    if valid_count + test_count >= total_count:
        valid_count = 1
        test_count = 1
    train_count = total_count - valid_count - test_count
    return {"train": train_count, "valid": valid_count, "test": test_count}


def _normalize_student_ids(values: pd.Series) -> pd.Series:
    return values.fillna("").astype(str).str.strip().replace("", pd.NA)


def _build_row_key_frame(frame: pd.DataFrame) -> pd.DataFrame:
    key_frame = pd.DataFrame(
        {
            "student_id": frame["student_id"].fillna("").astype(str),
            "term_key": frame["term_key"].fillna("").astype(str),
        },
        index=frame.index,
    )
    key_frame["row_ordinal"] = key_frame.groupby(["student_id", "term_key"], sort=False).cumcount()
    return key_frame


def _assign_group_splits(frame: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    normalized_student_ids = _normalize_student_ids(frame["student_id"])
    student_ids = normalized_student_ids.dropna().drop_duplicates().tolist()
    if len(student_ids) < 2:
        return _assign_row_splits(frame), "row_order_fallback"

    counts = _split_counts(len(student_ids))
    assignment: dict[str, str] = {}
    cursor = 0
    for split_name in _SPLIT_SEQUENCE:
        next_cursor = cursor + counts[split_name]
        for student_id in student_ids[cursor:next_cursor]:
            assignment[student_id] = split_name
        cursor = next_cursor

    split_frame = frame.copy()
    split_frame.loc[:, "dataset_split"] = normalized_student_ids.map(assignment).fillna("test")
    return split_frame, "grouped_by_student_id"


def _assign_row_splits(frame: pd.DataFrame) -> pd.DataFrame:
    counts = _split_counts(len(frame))
    labels: list[str] = []
    for split_name in _SPLIT_SEQUENCE:
        labels.extend([split_name] * counts[split_name])
    if len(labels) < len(frame):
        labels.extend(["test"] * (len(frame) - len(labels)))

    split_frame = frame.copy()
    split_frame.loc[:, "dataset_split"] = labels[: len(frame)]
    return split_frame


def _select_stable_numeric_features(train_frame: pd.DataFrame) -> list[str]:
    stable_features: list[str] = []
    total_rows = len(train_frame)
    for column in train_frame.columns:
        lowered = column.lower()
        if column in _EXCLUDED_FEATURE_COLUMNS or lowered.startswith("risk_label"):
            continue

        numeric_values = pd.to_numeric(train_frame[column], errors="coerce")
        non_null_count = int(numeric_values.notna().sum())
        if non_null_count < 2:
            continue
        if total_rows and (non_null_count / total_rows) < _MIN_STABLE_NON_NULL_RATIO:
            continue
        if numeric_values.dropna().nunique() < 2:
            continue
        stable_features.append(column)

    if not stable_features:
        raise ValueError("training requires at least one stable numeric feature column")
    return stable_features


def _fit_scorecard(
    train_frame: pd.DataFrame,
    feature_columns: list[str],
    trained_at: str,
    *,
    target_column: str,
) -> dict[str, object]:
    labels = train_frame[target_column].astype(int)
    positive_rate = float(labels.mean()) if len(labels) else 0.5
    positive_rate = min(max(positive_rate, 0.05), 0.95)
    intercept = math.log(positive_rate / (1.0 - positive_rate))

    feature_specs: list[dict[str, float | str]] = []
    feature_count = max(len(feature_columns), 1)
    for feature_name in feature_columns:
        numeric_values = pd.to_numeric(train_frame[feature_name], errors="coerce")
        median_value = float(numeric_values.median()) if numeric_values.notna().any() else 0.0
        filled_values = numeric_values.fillna(median_value).astype(float)
        center_value = float(filled_values.mean()) if len(filled_values) else 0.0
        scale_value = float(filled_values.std(ddof=0)) if len(filled_values) else 0.0
        if not math.isfinite(scale_value) or scale_value <= 1e-9:
            scale_value = 1.0

        positive_values = filled_values[labels == 1]
        negative_values = filled_values[labels == 0]
        coefficient = 0.0
        if not positive_values.empty and not negative_values.empty:
            coefficient = float((positive_values.mean() - negative_values.mean()) / scale_value)
            coefficient = max(min(coefficient, 3.0), -3.0) / feature_count

        feature_specs.append(
            {
                "feature": feature_name,
                "median": round(median_value, 6),
                "center": round(center_value, 6),
                "scale": round(scale_value, 6),
                "coefficient": round(coefficient, 6),
            }
        )

    return {
        "model_name": _MODEL_NAME,
        "target_label": target_column,
        "trained_at": trained_at,
        "intercept": round(intercept, 6),
        "feature_columns": feature_columns,
        "features": feature_specs,
    }


def _sigmoid(score: float) -> float:
    bounded = max(min(score, 60.0), -60.0)
    return 1.0 / (1.0 + math.exp(-bounded))


def _predict_probabilities(frame: pd.DataFrame, model_payload: dict[str, object]) -> pd.Series:
    feature_specs = model_payload["features"]
    scores = pd.Series(float(model_payload["intercept"]), index=frame.index, dtype="float64")
    for feature_spec in feature_specs:
        feature_name = str(feature_spec["feature"])
        numeric_values = pd.to_numeric(frame[feature_name], errors="coerce")
        filled_values = numeric_values.fillna(float(feature_spec["median"])).astype(float)
        standardized = (filled_values - float(feature_spec["center"])) / float(feature_spec["scale"])
        scores = scores + standardized * float(feature_spec["coefficient"])
    return scores.map(lambda score: round(_sigmoid(float(score)), 6))


def _compute_accuracy(labels: pd.Series, probabilities: pd.Series) -> float | None:
    if len(labels) == 0:
        return None
    predictions = (probabilities >= 0.5).astype(int)
    return round(float((predictions == labels.astype(int)).mean()), 4)


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def train_risk_model(
    features_csv: Path,
    output_dir: Path | None = None,
    *,
    trained_at: datetime | None = None,
) -> dict[str, object]:
    registry = _build_registry(output_dir)
    labeled_features, target_column = _load_labeled_features(features_csv)
    split_features, split_strategy = _assign_group_splits(labeled_features)

    train_frame = split_features.loc[split_features["dataset_split"] == "train"].reset_index(drop=True)
    if train_frame.empty:
        raise ValueError("training split is empty")

    feature_columns = _select_stable_numeric_features(train_frame)
    trained_at_text = _format_timestamp(trained_at)
    model_payload = _fit_scorecard(
        train_frame,
        feature_columns,
        trained_at_text,
        target_column=target_column,
    )
    model_payload["evaluation_split"] = {
        "kind": "row_keys",
        "split_name": "test",
        "rows": _build_row_key_frame(
            split_features.loc[split_features["dataset_split"] == "test"]
        ).to_dict(orient="records"),
    }
    probabilities = _predict_probabilities(split_features, model_payload)

    metrics_payload = {
        "model_name": _MODEL_NAME,
        "task_type": "binary_classification",
        "target_label": target_column,
        "split_strategy": split_strategy,
        "feature_count": len(feature_columns),
        "train_sample_count": int((split_features["dataset_split"] == "train").sum()),
        "valid_sample_count": int((split_features["dataset_split"] == "valid").sum()),
        "test_sample_count": int((split_features["dataset_split"] == "test").sum()),
        "train_accuracy": _compute_accuracy(
            split_features.loc[split_features["dataset_split"] == "train", target_column],
            probabilities.loc[split_features["dataset_split"] == "train"],
        ),
        "valid_accuracy": _compute_accuracy(
            split_features.loc[split_features["dataset_split"] == "valid", target_column],
            probabilities.loc[split_features["dataset_split"] == "valid"],
        ),
        "test_accuracy": _compute_accuracy(
            split_features.loc[split_features["dataset_split"] == "test", target_column],
            probabilities.loc[split_features["dataset_split"] == "test"],
        ),
        "trained_at": trained_at_text,
    }

    training_config = {
        "model_name": _MODEL_NAME,
        "target_label": target_column,
        "feature_columns": feature_columns,
        "split_strategy": split_strategy,
        "stable_feature_min_non_null_ratio": _MIN_STABLE_NON_NULL_RATIO,
        "deterministic": True,
        "train_sample_count": metrics_payload["train_sample_count"],
        "valid_sample_count": metrics_payload["valid_sample_count"],
        "test_sample_count": metrics_payload["test_sample_count"],
        "trained_at": trained_at_text,
    }

    feature_importance = pd.DataFrame(
        [
            {
                "feature": feature_name,
                "importance": len(feature_columns) - index,
                "coefficient": next(
                    float(feature_spec["coefficient"])
                    for feature_spec in model_payload["features"]
                    if str(feature_spec["feature"]) == feature_name
                ),
            }
            for index, feature_name in enumerate(feature_columns)
        ]
    )

    registry.artifact_dir.mkdir(parents=True, exist_ok=True)
    registry.model_path.write_bytes(pickle.dumps(model_payload))
    _write_json(registry.metrics_path, metrics_payload)
    feature_importance.to_csv(registry.feature_importance_path, index=False, encoding="utf-8")
    _write_json(registry.training_config_path, training_config)

    return {
        "split_strategy": split_strategy,
        "feature_columns": feature_columns,
        "feature_count": len(feature_columns),
        "train_sample_count": metrics_payload["train_sample_count"],
        "valid_sample_count": metrics_payload["valid_sample_count"],
        "test_sample_count": metrics_payload["test_sample_count"],
        "model_path": str(registry.model_path),
        "metrics_path": str(registry.metrics_path),
        "feature_importance_path": str(registry.feature_importance_path),
        "training_config_path": str(registry.training_config_path),
    }
