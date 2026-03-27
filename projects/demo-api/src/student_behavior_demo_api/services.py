from __future__ import annotations

import csv
import json
from collections import defaultdict
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from student_behavior_demo_api.loaders import load_json_records
from student_behavior_demo_api.loaders import load_student_results
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

    def get_student_profile(self, *, student_id: str, term: str) -> dict[str, Any]:
        student_rows = _load_student_result_rows(
            self._repo_root, self._warnings_path
        )
        student_rows = [row for row in student_rows if row.get("student_id") == student_id]
        if not student_rows:
            raise KeyError((student_id, term))

        current_row = next((row for row in student_rows if row.get("term_key") == term), None)
        if current_row is None:
            raise KeyError((student_id, term))

        return {
            "student_id": current_row.get("student_id"),
            "student_name": current_row.get("student_name"),
            "major_name": current_row.get("major_name"),
            "quadrant_label": current_row.get("quadrant_label"),
            "risk_level": current_row.get("risk_level"),
            "risk_probability": current_row.get("risk_probability"),
            "dimension_scores": _parse_json_field(
                current_row.get("dimension_scores_json"), field_name="dimension_scores_json"
            ),
            "trend": [
                {
                    "term": row.get("term_key"),
                    "dimension_scores": _parse_json_field(
                        row.get("dimension_scores_json"), field_name="dimension_scores_json"
                    ),
                }
                for row in sorted(student_rows, key=_sort_term_key)
            ],
        }

    def get_student_report(self, *, student_id: str, term: str) -> dict[str, Any]:
        report_rows = _load_student_report_rows(self._repo_root)
        current_row = next(
            (row for row in report_rows if row.get("student_id") == student_id and row.get("term_key") == term),
            None,
        )
        if current_row is None:
            raise KeyError((student_id, term))

        return {
            "top_factors": _parse_json_field(current_row.get("top_factors"), field_name="top_factors"),
            "intervention_advice": _parse_json_field(
                current_row.get("intervention_advice"), field_name="intervention_advice"
            ),
            "report_text": current_row.get("report_text"),
        }

    def get_quadrants(self, *, term: str) -> dict[str, Any]:
        warning_rows = _load_warning_rows(self._warnings_path or _resolve_warning_artifact_path(self._repo_root))
        term_rows = [row for row in warning_rows if row["term_key"] == term]
        if not term_rows:
            raise KeyError(term)

        report_rows = _load_student_report_rows(self._repo_root)
        report_index = {
            (row.get("student_id"), row.get("term_key")): row
            for row in report_rows
            if isinstance(row.get("student_id"), str) and isinstance(row.get("term_key"), str)
        }

        grouped_rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in term_rows:
            grouped_rows[row["quadrant_label"]].append(row)

        quadrants: list[dict[str, Any]] = []
        for quadrant_label, rows in grouped_rows.items():
            avg_risk_probability = round(
                sum(row["risk_probability"] for row in rows) / len(rows), 4
            )
            factor_stats: dict[str, dict[str, Any]] = {}
            for row in rows:
                report_row = report_index.get((row.get("student_id"), row.get("term_key")))
                factor_entries = _extract_quadrant_factor_entries(report_row)
                for factor in factor_entries:
                    dimension = factor["dimension"]
                    importance = factor["importance"]
                    current = factor_stats.get(dimension)
                    if current is None:
                        factor_stats[dimension] = {
                            "dimension": dimension,
                            "importance": importance,
                            "count": 1,
                        }
                        continue
                    current["count"] += 1
                    if importance > current["importance"]:
                        current["importance"] = importance

            top_factors = sorted(
                factor_stats.values(),
                key=lambda item: (-item["count"], -item["importance"], item["dimension"]),
            )
            quadrants.append(
                {
                    "quadrant_label": quadrant_label,
                    "student_count": len(rows),
                    "avg_risk_probability": avg_risk_probability,
                    "top_factors": top_factors,
                }
            )

        quadrants.sort(
            key=lambda item: (
                -item["avg_risk_probability"],
                item["quadrant_label"],
            )
        )
        return {"quadrants": quadrants}

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
        if term not in {row["term_key"] for row in warning_rows}:
            raise KeyError(term)
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


def _load_student_report_rows(repo_root: Path) -> list[dict[str, Any]]:
    report_path = _resolve_artifact_path(repo_root, "v1_student_reports.jsonl")
    return load_json_records(report_path)


def _load_student_result_rows(repo_root: Path, warnings_path: Path | None) -> list[dict[str, Any]]:
    results_path = _resolve_student_results_artifact_path(repo_root, warnings_path)
    frame = load_student_results(results_path)
    frame = frame.copy()
    frame["student_id"] = frame["student_id"].astype(str)
    frame["term_key"] = frame["term_key"].astype(str)
    return frame.to_dict(orient="records")


def _parse_json_field(raw_value: Any, *, field_name: str) -> Any:
    if isinstance(raw_value, str):
        try:
            return json.loads(raw_value)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{field_name} must contain valid JSON") from exc
    return raw_value


def _extract_quadrant_factor_entries(
    report_row: Mapping[str, Any] | None,
) -> list[dict[str, Any]]:
    if report_row is None:
        return []

    report_factors = _parse_json_field(report_row.get("top_factors"), field_name="top_factors")
    if not isinstance(report_factors, list):
        return []

    entries = []
    for item in report_factors:
        if not isinstance(item, Mapping):
            continue
        dimension = item.get("dimension") or item.get("feature_cn") or item.get("feature")
        if not isinstance(dimension, str) or not dimension:
            continue
        importance = item.get("importance")
        if not isinstance(importance, (int, float)):
            continue
        entries.append({"dimension": _canonicalize_dimension(dimension), "importance": float(importance)})
    return entries


def _canonicalize_dimension(dimension: str) -> str:
    return {
        "课堂参与表现": "课堂学习投入",
    }.get(dimension, dimension)


def _sort_term_key(row: Mapping[str, Any]) -> tuple[int, int, str]:
    term_key = row.get("term_key")
    if isinstance(term_key, str):
        parts = term_key.split("-")
        if len(parts) == 2 and all(part.isdigit() for part in parts):
            return (int(parts[0]), int(parts[1]), term_key)
    return (0, 0, str(term_key))


def _resolve_warning_artifact_path(repo_root: Path) -> Path:
    artifact_path = repo_root / "artifacts" / "model_stubs" / "v1_student_results.csv"
    if artifact_path.exists():
        return artifact_path
    raise FileNotFoundError(artifact_path)


def _resolve_student_results_artifact_path(repo_root: Path, warnings_path: Path | None) -> Path:
    if warnings_path is not None:
        return warnings_path
    return _resolve_warning_artifact_path(repo_root)


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
