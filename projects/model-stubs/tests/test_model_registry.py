from pathlib import Path

import pytest

from student_behavior_model_stubs.model_registry import build_default_model_registry


def test_build_default_model_registry_uses_training_artifact_defaults() -> None:
    repo_root = Path(r"C:\Users\Orion\Desktop\StudentBehavior")

    registry = build_default_model_registry(repo_root)

    assert registry.artifact_dir == repo_root / "artifacts" / "model_training"
    assert registry.model_path == registry.artifact_dir / "risk_model.pkl"
    assert registry.metrics_path == registry.artifact_dir / "risk_metrics.json"
    assert registry.feature_importance_path == registry.artifact_dir / "feature_importance.csv"
    assert registry.training_config_path == registry.artifact_dir / "training_config.json"


def test_build_default_model_registry_allows_model_filename_override() -> None:
    registry = build_default_model_registry(Path("/tmp/student-behavior"), model_filename="risk_model.txt")

    assert registry.model_path == registry.artifact_dir / "risk_model.txt"
    assert registry.metrics_path == registry.artifact_dir / "risk_metrics.json"


def test_load_metrics_returns_none_when_metrics_artifact_is_missing(tmp_path: Path) -> None:
    registry = build_default_model_registry(tmp_path)

    assert registry.load_metrics() is None


def test_load_metrics_reads_metrics_json_when_present(tmp_path: Path) -> None:
    registry = build_default_model_registry(tmp_path)
    registry.metrics_path.parent.mkdir(parents=True, exist_ok=True)
    registry.metrics_path.write_text(
        '{"model_name":"xgboost-risk","auc":0.91,"folds":["train","valid"]}',
        encoding="utf-8",
    )

    assert registry.load_metrics() == {
        "model_name": "xgboost-risk",
        "auc": 0.91,
        "folds": ["train", "valid"],
    }


def test_load_metrics_returns_none_for_malformed_json(tmp_path: Path) -> None:
    registry = build_default_model_registry(tmp_path)
    registry.metrics_path.parent.mkdir(parents=True, exist_ok=True)
    registry.metrics_path.write_text('{"model_name":', encoding="utf-8")

    assert registry.load_metrics() is None


def test_load_metrics_returns_none_for_non_object_json(tmp_path: Path) -> None:
    registry = build_default_model_registry(tmp_path)
    registry.metrics_path.parent.mkdir(parents=True, exist_ok=True)
    registry.metrics_path.write_text('["train","valid"]', encoding="utf-8")

    assert registry.load_metrics() is None


def test_load_metrics_returns_none_for_invalid_utf8_bytes(tmp_path: Path) -> None:
    registry = build_default_model_registry(tmp_path)
    registry.metrics_path.parent.mkdir(parents=True, exist_ok=True)
    registry.metrics_path.write_bytes(b"\xff\xfe\xfa")

    assert registry.load_metrics() is None


def test_load_metrics_returns_none_for_unreadable_artifact(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    registry = build_default_model_registry(tmp_path)
    registry.metrics_path.parent.mkdir(parents=True, exist_ok=True)
    registry.metrics_path.write_text("{}", encoding="utf-8")

    original_read_text = Path.read_text

    def raising_read_text(self: Path, *args: object, **kwargs: object) -> str:
        if self == registry.metrics_path:
            raise OSError("artifact temporarily unavailable")
        return original_read_text(self, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", raising_read_text)

    assert registry.load_metrics() is None
