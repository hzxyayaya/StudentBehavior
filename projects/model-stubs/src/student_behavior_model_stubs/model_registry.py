from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ModelArtifactRegistry:
    artifact_dir: Path
    model_path: Path
    metrics_path: Path
    feature_importance_path: Path
    training_config_path: Path

    def load_metrics(self) -> dict[str, object] | None:
        if not self.metrics_path.exists():
            return None

        try:
            loaded = json.loads(self.metrics_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            return None

        if not isinstance(loaded, dict):
            return None
        return loaded


def build_default_model_registry(
    repo_root: Path,
    *,
    model_filename: str = "risk_model.pkl",
) -> ModelArtifactRegistry:
    artifact_dir = repo_root / "artifacts" / "model_training"
    return ModelArtifactRegistry(
        artifact_dir=artifact_dir,
        model_path=artifact_dir / model_filename,
        metrics_path=artifact_dir / "risk_metrics.json",
        feature_importance_path=artifact_dir / "feature_importance.csv",
        training_config_path=artifact_dir / "training_config.json",
    )
