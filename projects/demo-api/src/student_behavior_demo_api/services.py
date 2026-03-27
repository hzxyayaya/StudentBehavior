from __future__ import annotations

import csv
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
        warnings_path: Path | None = None,
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
        self._repo_root = resolved_repo_root
        self._warnings_path = warnings_path
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

    def list_warnings(
        self,
        *,
        term: str,
        page: int = 1,
        page_size: int = 20,
        risk_level: str | None = None,
        quadrant_label: str | None = None,
        major_name: str | None = None,
    ) -> dict[str, Any]:
        warning_rows = _load_warning_rows(self._warnings_path or _resolve_warning_artifact_path(self._repo_root))
        filtered_rows = [
            row
            for row in warning_rows
            if row["term_key"] == term
            and (risk_level is None or row["risk_level"] == risk_level)
            and (quadrant_label is None or row["quadrant_label"] == quadrant_label)
            and (major_name is None or row["major_name"] == major_name)
        ]
        filtered_rows.sort(key=lambda row: (-row["risk_probability"], row["student_id"]))

        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        items = [
            {
                key: value
                for key, value in row.items()
                if key != "_risk_probability_sort"
            }
            for row in filtered_rows[start_index:end_index]
        ]
        return {
            "items": items,
            "page": page,
            "page_size": page_size,
            "total": len(filtered_rows),
        }


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


def _load_warning_rows(path: Path | None) -> list[dict[str, Any]]:
    if path is None:
        raise FileNotFoundError("v1_student_results.csv")

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        rows: list[dict[str, Any]] = []
        for raw_row in reader:
            if not raw_row:
                continue
            student_id = raw_row.get("student_id")
            if not isinstance(student_id, str) or not student_id:
                bom_student_id = raw_row.get("\ufeffstudent_id")
                if isinstance(bom_student_id, str) and bom_student_id:
                    raw_row["student_id"] = bom_student_id
                else:
                    raise ValueError("warnings rows must include student_id")

            risk_probability_raw = raw_row.get("risk_probability")
            if not isinstance(risk_probability_raw, str) or not risk_probability_raw:
                raise ValueError("warnings rows must include risk_probability")

            row = dict(raw_row)
            row["risk_probability"] = float(risk_probability_raw)
            rows.append(row)
        return rows


def _resolve_warning_artifact_path(repo_root: Path) -> Path:
    candidates = [
        repo_root / "artifacts" / "model_stubs" / "v1_student_results.csv",
        repo_root.parent / "v1-model-stubs" / "artifacts" / "model_stubs" / "v1_student_results.csv",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(candidates[-1])


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
