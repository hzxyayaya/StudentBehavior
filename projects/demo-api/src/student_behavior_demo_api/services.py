from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from student_behavior_demo_api.loaders import load_json_records
from student_behavior_demo_api.loaders import validate_model_summary_payload
from student_behavior_demo_api.loaders import validate_overview_payload


class DemoApiStore:
    def __init__(
        self,
        overview_path: Path | None = None,
        model_summary_path: Path | None = None,
        overview_term: str | None = None,
        repo_root: Path | None = None,
    ) -> None:
        resolved_repo_root = repo_root or Path(__file__).resolve().parents[4]
        resolved_overview_path = overview_path or _resolve_artifact_path(
            resolved_repo_root, "v1_overview_by_term.json"
        )
        resolved_model_summary_path = model_summary_path or _resolve_artifact_path(
            resolved_repo_root, "v1_model_summary.json"
        )
        overview_record = _load_single_record(resolved_overview_path)
        self._overview_term = overview_term or _infer_overview_term(overview_record)
        validate_overview_payload({"term_buckets": {self._overview_term: overview_record}})
        self._overview_payload = dict(overview_record)
        self._model_summary_payload = dict(
            validate_model_summary_payload(_load_single_record(resolved_model_summary_path))
        )

    def get_overview(self, term: str) -> dict[str, Any]:
        if term != self._overview_term:
            raise KeyError(term)
        return dict(self._overview_payload)

    def get_model_summary(self, term: str | None = None) -> dict[str, Any]:
        return dict(self._model_summary_payload)


def _resolve_artifact_path(repo_root: Path, artifact_name: str) -> Path:
    artifact_path = repo_root / "artifacts" / "model_stubs" / artifact_name
    if artifact_path.exists():
        return artifact_path
    raise FileNotFoundError(artifact_path)


def _load_single_record(path: Path) -> Mapping[str, Any]:
    records = load_json_records(path)
    if len(records) != 1:
        raise ValueError(f"expected exactly one record in {path}")
    return records[0]


def _infer_overview_term(payload: Mapping[str, Any]) -> str:
    trend_summary = payload.get("trend_summary")
    if not isinstance(trend_summary, Mapping):
        raise ValueError("trend_summary must be a mapping")

    terms = trend_summary.get("terms")
    if not isinstance(terms, list) or not terms:
        raise ValueError("trend_summary.terms must be a non-empty list")

    latest_term = terms[-1]
    if not isinstance(latest_term, Mapping):
        raise ValueError("trend_summary.terms entries must be mappings")

    term_key = latest_term.get("term_key")
    if not isinstance(term_key, str) or not term_key:
        raise ValueError("trend_summary.terms entries must include term_key")
    return term_key
