from __future__ import annotations

import csv
import json
import math
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
        self._overview_terms = _infer_overview_terms(overview_record, self._overview_term)
        validate_overview_payload({"term_buckets": {self._overview_term: overview_record}})
        self._overview_payload = dict(overview_record)
        self._model_summary_payload = dict(
            validate_model_summary_payload(_load_single_record(resolved_model_summary_path))
        )

    def get_overview(self, term: str) -> dict[str, Any]:
        if term not in self._overview_terms:
            raise KeyError(term)
        payload = dict(self._overview_payload)
        term_rows = [
            row
            for row in _load_warning_rows(
                self._warnings_path or _resolve_warning_artifact_path(self._repo_root)
            )
            if row["term_key"] == term
        ]

        if term != self._overview_term:
            payload = _build_term_aware_overview_fallback(payload, term, term_rows)
        elif "dimension_summary" not in payload or _is_sparse_dimension_summary(payload.get("dimension_summary")):
            term_dimension_summary = _build_average_dimension_scores(term_rows)
            if term_dimension_summary:
                payload["dimension_summary"] = term_dimension_summary
        if "risk_band_distribution" not in payload:
            payload["risk_band_distribution"] = _build_risk_band_distribution(term_rows)
        if "risk_factor_summary" not in payload:
            payload["risk_factor_summary"] = _build_risk_factor_summary(term_rows)
        return payload

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
            "group_segment": current_row.get("group_segment"),
            "risk_level": current_row.get("risk_level"),
            "risk_probability": current_row.get("risk_probability"),
            "base_risk_score": _as_float(current_row.get("base_risk_score")),
            "risk_adjustment_score": _as_float(current_row.get("risk_adjustment_score")),
            "adjusted_risk_score": _as_float(current_row.get("adjusted_risk_score")),
            "risk_delta": _as_float(current_row.get("risk_delta")),
            "risk_change_direction": current_row.get("risk_change_direction"),
            "base_risk_explanation": current_row.get("base_risk_explanation"),
            "behavior_adjustment_explanation": current_row.get("behavior_adjustment_explanation"),
            "risk_change_explanation": current_row.get("risk_change_explanation"),
            "dimension_scores": _parse_json_field(
                current_row.get("dimension_scores_json"), field_name="dimension_scores_json"
            ),
            "trend": [
                {
                    "term": row.get("term_key"),
                    "risk_level": row.get("risk_level"),
                    "risk_probability": row.get("risk_probability"),
                    "adjusted_risk_score": _as_float(row.get("adjusted_risk_score")),
                    "risk_delta": _as_float(row.get("risk_delta")),
                    "risk_change_direction": row.get("risk_change_direction"),
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

        student_rows = _load_student_result_rows(self._repo_root, self._warnings_path)
        student_rows = [row for row in student_rows if row.get("student_id") == student_id]
        current_warning = next((row for row in student_rows if row.get("term_key") == term), None)
        if current_warning is None:
            raise KeyError((student_id, term))

        return {
            "top_factors": _parse_json_field(current_row.get("top_factors"), field_name="top_factors"),
            "intervention_advice": _parse_json_field(
                current_row.get("intervention_advice"), field_name="intervention_advice"
            ),
            "report_text": current_row.get("report_text"),
            "base_risk_explanation": (
                current_row.get("base_risk_explanation") or current_warning.get("base_risk_explanation")
            ),
            "behavior_adjustment_explanation": (
                current_row.get("behavior_adjustment_explanation")
                or current_warning.get("behavior_adjustment_explanation")
            ),
            "risk_change_explanation": (
                current_row.get("risk_change_explanation") or current_warning.get("risk_change_explanation")
            ),
            "intervention_plan": _parse_maybe_json_field(
                current_row.get("intervention_plan"), field_name="intervention_plan"
            ),
            "risk_level": current_warning.get("risk_level"),
            "risk_probability": current_warning.get("risk_probability"),
            "base_risk_score": _as_float(current_warning.get("base_risk_score")),
            "risk_adjustment_score": _as_float(current_warning.get("risk_adjustment_score")),
            "adjusted_risk_score": _as_float(current_warning.get("adjusted_risk_score")),
            "risk_delta": _as_float(current_warning.get("risk_delta")),
            "risk_change_direction": current_warning.get("risk_change_direction"),
            "trend": [
                {
                    "term": row.get("term_key"),
                    "risk_level": row.get("risk_level"),
                    "risk_probability": row.get("risk_probability"),
                    "base_risk_score": _as_float(row.get("base_risk_score")),
                    "risk_adjustment_score": _as_float(row.get("risk_adjustment_score")),
                    "adjusted_risk_score": _as_float(row.get("adjusted_risk_score")),
                    "risk_delta": _as_float(row.get("risk_delta")),
                    "risk_change_direction": row.get("risk_change_direction"),
                }
                for row in sorted(student_rows, key=_sort_term_key)
            ],
        }

    def get_groups(self, *, term: str) -> dict[str, Any]:
        warning_rows = _load_warning_rows(self._warnings_path or _resolve_warning_artifact_path(self._repo_root))
        term_rows = [row for row in warning_rows if row["term_key"] == term]
        if not term_rows:
            raise KeyError(term)

        report_rows = _load_student_report_rows(self._repo_root)
        report_index: dict[tuple[str, str], dict[str, Any]] = {}
        for row in report_rows:
            student_id = row.get("student_id")
            term_key = row.get("term_key")
            if student_id is None or term_key is None:
                continue
            student_id = str(student_id)
            term_key = str(term_key)
            if not student_id or not term_key:
                continue
            report_index[(student_id, term_key)] = row

        grouped_rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in term_rows:
            grouped_rows[row["group_segment"]].append(row)

        groups: list[dict[str, Any]] = []
        for group_segment, rows in grouped_rows.items():
            avg_risk_probability = round(
                sum(row["risk_probability"] for row in rows) / len(rows), 4
            )
            avg_risk_score = _average_numeric(rows, "adjusted_risk_score", fallback_field="risk_probability")
            avg_risk_level = _resolve_avg_risk_level(rows)
            risk_change_summary = _build_risk_change_summary(rows)
            avg_dimension_scores = _build_average_dimension_scores(rows)
            risk_amplifiers = _aggregate_warning_factors(rows, "top_risk_factors_json")
            protective_factors = _aggregate_warning_factors(rows, "top_protective_factors_json")
            factor_stats: dict[str, dict[str, Any]] = {}
            factor_aliases: dict[str, str] = {}
            for row in rows:
                report_row = report_index.get((row.get("student_id"), row.get("term_key")))
                factor_entries = _extract_group_factor_entries(report_row)
                for factor in factor_entries:
                    identity_key = _resolve_identity_key(
                        factor.get("_identity_key"),
                        factor.get("_identity_aliases", []),
                        factor_aliases,
                    )
                    importance = factor["importance"]
                    current = factor_stats.get(identity_key)
                    if current is None:
                        factor_stats[identity_key] = _copy_public_fields(factor)
                        factor_stats[identity_key]["count"] = 1
                        _register_identity_aliases(
                            factor_aliases,
                            factor_stats[identity_key].get("_identity_key"),
                            factor.get("_identity_aliases", []),
                            identity_key,
                        )
                        continue
                    current["count"] += 1
                    if importance > current["importance"]:
                        current["importance"] = importance
                    _merge_summary_fields(current, factor)
                    _register_identity_aliases(
                        factor_aliases,
                        current.get("_identity_key"),
                        factor.get("_identity_aliases", []),
                        identity_key,
                    )

            top_factors = sorted(
                [_copy_public_fields(item) for item in factor_stats.values()],
                key=lambda item: (-item["count"], -item["importance"], item["dimension"]),
            )
            groups.append(
                {
                    "group_segment": group_segment,
                    "student_count": len(rows),
                    "avg_risk_probability": avg_risk_probability,
                    "avg_risk_score": avg_risk_score,
                    "avg_risk_level": avg_risk_level,
                    "risk_change_summary": risk_change_summary,
                    "risk_amplifiers": risk_amplifiers,
                    "protective_factors": protective_factors,
                    "avg_dimension_scores": avg_dimension_scores,
                    "top_factors": top_factors,
                }
            )

        groups.sort(
            key=lambda item: (
                -item["avg_risk_probability"],
                item["group_segment"],
            )
        )
        return {"groups": groups}

    def list_warnings(
        self,
        *,
        term: str,
        page: int = 1,
        page_size: int = 20,
        risk_level: str | None = None,
        group_segment: str | None = None,
        major_name: str | None = None,
        risk_change_direction: str | None = None,
    ) -> dict[str, Any]:
        warning_rows = _load_warning_rows(self._warnings_path or _resolve_warning_artifact_path(self._repo_root))
        if term not in {row["term_key"] for row in warning_rows}:
            raise KeyError(term)
        allowed_levels = _resolve_allowed_risk_levels(risk_level)
        filtered_rows = [
            row
            for row in warning_rows
            if row["term_key"] == term
            and (allowed_levels is None or _normalize_risk_level(row.get("risk_level")) in allowed_levels)
            and (group_segment is None or row["group_segment"] == group_segment)
            and (major_name is None or row["major_name"] == major_name)
            and (
                risk_change_direction is None
                or row.get("risk_change_direction") == risk_change_direction
            )
        ]
        filtered_rows.sort(key=lambda row: (-row["risk_probability"], row["student_id"]))

        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        items = [
            {
                "student_id": row.get("student_id"),
                "student_name": row.get("student_name"),
                "major_name": row.get("major_name"),
                "group_segment": row.get("group_segment"),
                "risk_probability": row.get("risk_probability"),
                "base_risk_score": _as_float(row.get("base_risk_score")),
                "risk_adjustment_score": _as_float(row.get("risk_adjustment_score")),
                "adjusted_risk_score": _as_float(row.get("adjusted_risk_score")),
                "risk_level": row.get("risk_level"),
                "risk_delta": _as_float(row.get("risk_delta")),
                "risk_change_direction": row.get("risk_change_direction"),
                "top_risk_factors": [
                    _copy_public_fields(item)
                    for item in _parse_warning_factors(
                        row.get("top_risk_factors_json"),
                        field_name="top_risk_factors_json",
                    )
                ],
                "top_protective_factors": [
                    _copy_public_fields(item)
                    for item in _parse_warning_factors(
                        row.get("top_protective_factors_json"),
                        field_name="top_protective_factors_json",
                    )
                ],
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

            term_key = raw_row.get("term_key")
            if not isinstance(term_key, str) or not term_key:
                raise ValueError("warnings rows must include term_key")

            group_segment = raw_row.get("group_segment")
            if not isinstance(group_segment, str) or not group_segment:
                raise ValueError("warnings rows must include group_segment")

            if "dimension_scores_json" not in raw_row:
                raise ValueError("warnings rows must include dimension_scores_json")

            risk_probability_raw = raw_row.get("risk_probability")
            if not isinstance(risk_probability_raw, str) or not risk_probability_raw:
                raise ValueError("warnings rows must include risk_probability")

            row = dict(raw_row)
            row["risk_probability"] = float(risk_probability_raw)
            if not math.isfinite(row["risk_probability"]):
                raise ValueError("warnings rows must include finite risk_probability")
            dimension_scores_raw = row.get("dimension_scores_json")
            if isinstance(dimension_scores_raw, str) and not dimension_scores_raw.strip():
                row["dimension_scores_json"] = "[]"
            for key in (
                "base_risk_score",
                "risk_adjustment_score",
                "adjusted_risk_score",
                "risk_delta",
            ):
                if key in row:
                    row[key] = _as_float(row.get(key))
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
    if "dimension_scores_json" in frame:
        frame["dimension_scores_json"] = frame["dimension_scores_json"].fillna("").astype(str)
        blank_scores = frame["dimension_scores_json"].str.strip() == ""
        frame.loc[blank_scores, "dimension_scores_json"] = "[]"
    return frame.to_dict(orient="records")


def _parse_json_field(raw_value: Any, *, field_name: str) -> Any:
    if isinstance(raw_value, str):
        try:
            return json.loads(raw_value)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{field_name} must contain valid JSON") from exc
    return raw_value


def _parse_maybe_json_field(raw_value: Any, *, field_name: str) -> Any:
    if isinstance(raw_value, str):
        try:
            return json.loads(raw_value)
        except json.JSONDecodeError:
            return raw_value
    return raw_value


def _as_float(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str) and value.strip():
        try:
            return float(value)
        except ValueError as exc:
            raise ValueError("numeric fields must be numeric") from exc
    return None


def _parse_warning_factors(raw_value: Any, *, field_name: str) -> list[dict[str, Any]]:
    parsed = _parse_json_field(raw_value, field_name=field_name)
    if parsed is None:
        return []
    if not isinstance(parsed, list):
        raise ValueError(f"{field_name} must decode to a list")
    factors: list[dict[str, Any]] = []
    for item in parsed:
        if not isinstance(item, Mapping):
            raise ValueError(f"{field_name} items must be objects")
        factor_entry = dict(item)
        if "importance" in factor_entry:
            factor_entry["importance"] = _as_float(factor_entry.get("importance"))
        factor_entry["_identity_aliases"] = _identity_aliases(factor_entry)
        factor_entry["_identity_key"] = _preferred_identity_key(factor_entry)
        factors.append(factor_entry)
    return factors


def _extract_group_factor_entries(
    report_row: Mapping[str, Any] | None,
) -> list[dict[str, Any]]:
    if report_row is None:
        return []

    report_factors = _parse_json_field(report_row.get("top_factors"), field_name="top_factors")
    if not isinstance(report_factors, list):
        raise ValueError("top_factors must be a list")

    unique_entries: dict[str, dict[str, Any]] = {}
    alias_index: dict[str, str] = {}
    for item in report_factors:
        if isinstance(item, str):
            if item:
                factor_entry = {
                    "dimension": item,
                    "importance": 1.0,
                    "_identity_key": item,
                    "_identity_aliases": [item],
                }
                identity_key = _resolve_identity_key(
                    factor_entry["_identity_key"],
                    factor_entry["_identity_aliases"],
                    alias_index,
                )
                current = unique_entries.get(identity_key)
                if current is None:
                    unique_entries[identity_key] = factor_entry
                    _register_identity_aliases(
                        alias_index,
                        unique_entries[identity_key]["_identity_key"],
                        factor_entry["_identity_aliases"],
                        identity_key,
                    )
                else:
                    current["importance"] = max(current["importance"], 1.0)
                    _merge_summary_fields(current, factor_entry)
                    _register_identity_aliases(
                        alias_index,
                        current.get("_identity_key"),
                        factor_entry["_identity_aliases"],
                        identity_key,
                    )
            else:
                raise ValueError("top_factors items must be strings or factor objects")
            continue
        if not isinstance(item, Mapping):
            raise ValueError("top_factors items must be strings or factor objects")
        dimension = item.get("dimension") or item.get("feature_cn") or item.get("feature")
        if not isinstance(dimension, str) or not dimension:
            raise ValueError("top_factors items must be strings or factor objects")
        try:
            importance = _as_float(item.get("importance"))
        except ValueError as exc:
            raise ValueError("top_factors items must be strings or factor objects") from exc
        if importance is None or not math.isfinite(importance):
            raise ValueError("top_factors items must be strings or factor objects")
        factor_entry = {
            "dimension": dimension,
            "importance": importance,
        }
        for optional_key in ("feature", "feature_cn", "effect"):
            optional_value = item.get(optional_key)
            if isinstance(optional_value, str) and optional_value:
                factor_entry[optional_key] = optional_value
        factor_entry["_identity_aliases"] = _identity_aliases(factor_entry)
        factor_entry["_identity_key"] = _preferred_identity_key(factor_entry)
        identity_key = _resolve_identity_key(
            factor_entry["_identity_key"],
            factor_entry["_identity_aliases"],
            alias_index,
        )
        current = unique_entries.get(identity_key)
        if current is None:
            unique_entries[identity_key] = factor_entry
            _register_identity_aliases(
                alias_index,
                unique_entries[identity_key]["_identity_key"],
                factor_entry["_identity_aliases"],
                identity_key,
            )
        else:
            current["importance"] = max(current["importance"], float(importance))
            _merge_summary_fields(current, factor_entry)
            _register_identity_aliases(
                alias_index,
                current.get("_identity_key"),
                factor_entry["_identity_aliases"],
                identity_key,
            )
    return list(unique_entries.values())


def _build_average_dimension_scores(rows: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    totals: dict[str, dict[str, Any]] = {}
    alias_index: dict[str, str] = {}
    for row in rows:
        raw_scores = row.get("dimension_scores_json")
        if isinstance(raw_scores, str) and not raw_scores.strip():
            dimension_scores = []
        else:
            dimension_scores = _parse_json_field(
                raw_scores, field_name="dimension_scores_json"
            )
        if not isinstance(dimension_scores, list):
            raise ValueError("dimension_scores_json must decode to a list")
        for item in dimension_scores:
            if not isinstance(item, Mapping):
                raise ValueError("dimension_scores_json items must be objects")
            dimension = item.get("dimension")
            score = item.get("score")
            if not isinstance(dimension, str) or not dimension:
                raise ValueError("dimension_scores_json items must include dimension")
            if not isinstance(score, (int, float)):
                raise ValueError("dimension_scores_json items must include numeric score")
            summary_entry = _build_dimension_summary_entry(item, float(score))
            identity_key = _resolve_identity_key(
                summary_entry["_identity_key"],
                summary_entry["_identity_aliases"],
                alias_index,
            )
            current = totals.get(identity_key)
            if current is None:
                totals[identity_key] = summary_entry
                _register_identity_aliases(
                    alias_index,
                    summary_entry["_identity_key"],
                    summary_entry["_identity_aliases"],
                    identity_key,
                )
            else:
                current["total"] += float(score)
                current["score_count"] += 1
                _merge_summary_fields(current, summary_entry)
                _register_identity_aliases(
                    alias_index,
                    current.get("_identity_key"),
                    summary_entry["_identity_aliases"],
                    identity_key,
                )

    return [
        _finalize_dimension_summary(value)
        for value in totals.values()
    ]


def _find_trend_summary_term(payload: Mapping[str, Any], term: str) -> Mapping[str, Any] | None:
    trend_summary = payload.get("trend_summary")
    if not isinstance(trend_summary, Mapping):
        return None

    term_entries = trend_summary.get("terms")
    if not isinstance(term_entries, list):
        return None

    for term_entry in term_entries:
        if isinstance(term_entry, Mapping) and term_entry.get("term_key") == term:
            return term_entry
    return None


def _build_term_aware_overview_fallback(
    payload: Mapping[str, Any],
    term: str,
    term_rows: list[Mapping[str, Any]],
) -> dict[str, Any]:
    fallback_payload = dict(payload)
    trend_entry = _find_trend_summary_term(payload, term)

    if trend_entry is not None and isinstance(trend_entry.get("student_count"), int):
        fallback_payload["student_count"] = trend_entry["student_count"]
    else:
        fallback_payload["student_count"] = len(term_rows)

    if trend_entry is not None and isinstance(trend_entry.get("risk_distribution"), Mapping):
        fallback_payload["risk_distribution"] = dict(trend_entry["risk_distribution"])
    else:
        fallback_payload["risk_distribution"] = _build_risk_distribution(term_rows)

    fallback_payload["risk_band_distribution"] = _build_risk_band_distribution(term_rows)
    fallback_payload["group_distribution"] = _build_group_distribution(term_rows)
    fallback_payload["major_risk_summary"] = _build_major_risk_summary(term_rows)
    fallback_payload["risk_factor_summary"] = _build_risk_factor_summary(term_rows)

    term_dimension_summary = _build_average_dimension_scores(term_rows)
    fallback_payload["dimension_summary"] = term_dimension_summary

    fallback_payload["trend_summary"] = None
    fallback_payload["summary_term"] = term
    fallback_payload["summary_source"] = "term_fallback"
    fallback_payload["summary_unavailable_fields"] = ["trend_summary"]
    return fallback_payload


def _build_dimension_summary_entry(item: Mapping[str, Any], score: float) -> dict[str, Any]:
    summary_entry = {
        "dimension": item["dimension"],
        "total": score,
        "score_count": 1,
    }
    for optional_key in (
        "dimension_code",
        "feature",
        "feature_cn",
        "level",
        "label",
        "metrics",
        "explanation",
    ):
        optional_value = item.get(optional_key)
        if optional_value is not None:
            summary_entry[optional_key] = optional_value
    summary_entry["_identity_aliases"] = _identity_aliases(summary_entry)
    summary_entry["_identity_key"] = _preferred_identity_key(summary_entry)
    return summary_entry


def _is_sparse_dimension_summary(raw: Any) -> bool:
    if not isinstance(raw, list) or not raw:
        return True
    for item in raw:
        if not isinstance(item, Mapping):
            return True
        if any(item.get(key) not in (None, [], "") for key in ("level", "label", "metrics", "explanation")):
            return False
    return True


def _build_group_distribution(rows: list[Mapping[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for row in rows:
        group_segment = row.get("group_segment")
        if isinstance(group_segment, str) and group_segment:
            counts[group_segment] += 1
    return dict(counts)


def _build_major_risk_summary(rows: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    stats: dict[str, dict[str, float]] = {}
    for row in rows:
        major_name = row.get("major_name")
        risk_level = _normalize_risk_level(row.get("risk_level")) or row.get("risk_level")
        risk_probability = row.get("risk_probability")
        if not isinstance(major_name, str) or not major_name:
            continue
        if not isinstance(risk_probability, (int, float)):
            continue
        current = stats.get(major_name)
        if current is None:
            stats[major_name] = {
                "student_count": 1.0,
                "high_risk_count": 1.0 if risk_level == "高风险" else 0.0,
                "risk_probability_total": float(risk_probability),
            }
            continue
        current["student_count"] += 1.0
        current["risk_probability_total"] += float(risk_probability)
        if risk_level == "高风险":
            current["high_risk_count"] += 1.0

    summaries = [
        {
            "major_name": major_name,
            "student_count": int(values["student_count"]),
            "high_risk_count": int(values["high_risk_count"]),
            "average_risk_probability": round(
                values["risk_probability_total"] / values["student_count"], 2
            ),
        }
        for major_name, values in stats.items()
    ]
    summaries.sort(key=lambda item: item["major_name"])
    return summaries


def _build_risk_distribution(rows: list[Mapping[str, Any]]) -> dict[str, int]:
    distribution = {"high": 0, "medium": 0, "low": 0}
    for row in rows:
        normalized = _normalize_risk_level(row.get("risk_level"))
        if normalized in {"高风险", "较高风险"}:
            distribution["high"] += 1
        elif normalized == "一般风险":
            distribution["medium"] += 1
        elif normalized == "低风险":
            distribution["low"] += 1
    return distribution


def _build_risk_band_distribution(rows: list[Mapping[str, Any]]) -> dict[str, int]:
    distribution = {"高风险": 0, "较高风险": 0, "一般风险": 0, "低风险": 0}
    for row in rows:
        risk_level = row.get("risk_level")
        normalized = _normalize_risk_level(risk_level)
        if normalized in distribution:
            distribution[normalized] += 1
    return distribution


def _build_risk_factor_summary(rows: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return _aggregate_warning_factors(rows, "top_risk_factors_json")


def _average_numeric(
    rows: list[Mapping[str, Any]],
    field_name: str,
    *,
    fallback_field: str | None = None,
) -> float | None:
    values: list[float] = []
    for row in rows:
        value = _as_float(row.get(field_name))
        if value is None and fallback_field is not None:
            value = _as_float(row.get(fallback_field))
        if value is not None:
            values.append(value)
    if not values:
        return None
    return round(sum(values) / len(values), 2)


def _resolve_avg_risk_level(rows: list[Mapping[str, Any]]) -> str | None:
    avg_score = _average_numeric(rows, "adjusted_risk_score", fallback_field="risk_probability")
    if avg_score is not None:
        if avg_score <= 1:
            avg_score *= 100
        return _map_risk_level_from_score(avg_score)
    levels = [row.get("risk_level") for row in rows if isinstance(row.get("risk_level"), str)]
    if not levels:
        return None
    return max(levels, key=lambda value: (levels.count(value), _risk_level_severity(value)))


def _build_risk_change_summary(rows: list[Mapping[str, Any]]) -> dict[str, int]:
    summary = {"rising": 0, "steady": 0, "falling": 0}
    for row in rows:
        direction = row.get("risk_change_direction")
        if isinstance(direction, str) and direction in summary:
            summary[direction] += 1
    return summary


def _aggregate_warning_factors(rows: list[Mapping[str, Any]], field_name: str) -> list[dict[str, Any]]:
    factor_stats: dict[str, dict[str, Any]] = {}
    factor_aliases: dict[str, str] = {}
    for row in rows:
        factors = _parse_warning_factors(row.get(field_name), field_name=field_name)
        for factor in factors:
            identity_key = _resolve_identity_key(
                factor.get("_identity_key"),
                factor.get("_identity_aliases", []),
                factor_aliases,
            )
            current = factor_stats.get(identity_key)
            if current is None:
                factor_stats[identity_key] = _copy_public_fields(factor)
                factor_stats[identity_key]["count"] = 1
                _register_identity_aliases(
                    factor_aliases,
                    factor.get("_identity_key"),
                    factor.get("_identity_aliases", []),
                    identity_key,
                )
                continue
            current["count"] += 1
            incoming_importance = factor.get("importance")
            if isinstance(incoming_importance, (int, float)) and (
                not isinstance(current.get("importance"), (int, float))
                or float(incoming_importance) > float(current["importance"])
            ):
                current["importance"] = float(incoming_importance)
            _merge_summary_fields(current, factor)
            _register_identity_aliases(
                factor_aliases,
                factor.get("_identity_key"),
                factor.get("_identity_aliases", []),
                identity_key,
            )

    return sorted(
        [_copy_public_fields(item) for item in factor_stats.values()],
        key=lambda item: (-item.get("count", 0), -float(item.get("importance", 0) or 0)),
    )


def _normalize_risk_level(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    mapping = {
        "high": "高风险",
        "medium": "一般风险",
        "low": "低风险",
        "高风险": "高风险",
        "较高风险": "较高风险",
        "一般风险": "一般风险",
        "低风险": "低风险",
    }
    return mapping.get(value)


def _map_risk_level_from_score(score: float) -> str:
    if score >= 80:
        return "高风险"
    if score >= 65:
        return "较高风险"
    if score >= 45:
        return "一般风险"
    return "低风险"


def _risk_level_severity(level: str) -> int:
    order = ["low", "medium", "high", "低风险", "一般风险", "较高风险", "高风险"]
    if level in order:
        return order.index(level)
    return -1


def _finalize_dimension_summary(value: Mapping[str, Any]) -> dict[str, Any]:
    summary = _copy_public_fields(value)
    summary["average_score"] = round(float(value["total"]) / int(value["score_count"]), 2)
    summary["score_count"] = int(value["score_count"])
    return summary


def _resolve_allowed_risk_levels(risk_level: str | None) -> set[str] | None:
    if risk_level is None:
        return None
    normalized = _normalize_risk_level(risk_level) or risk_level
    if normalized == "高风险":
        if risk_level == "较高风险":
            return {"较高风险"}
        return {"高风险", "较高风险"}
    if normalized == "一般风险":
        return {"一般风险"}
    if normalized == "低风险":
        return {"低风险"}
    return {normalized}


def _preferred_identity_key(item: Mapping[str, Any]) -> str:
    for key in ("feature", "feature_cn", "dimension"):
        value = item.get(key)
        if isinstance(value, str) and value:
            return value
    raise ValueError("items must include a canonical identifier")


def _identity_aliases(item: Mapping[str, Any]) -> list[str]:
    aliases: list[str] = []
    for key in ("feature", "feature_cn", "dimension"):
        value = item.get(key)
        if isinstance(value, str) and value and value not in aliases:
            aliases.append(value)
    return aliases


def _resolve_identity_key(
    preferred_key: Any,
    aliases: list[str] | tuple[str, ...],
    alias_index: Mapping[str, str],
) -> str:
    if isinstance(preferred_key, str):
        existing_key = alias_index.get(preferred_key)
        if existing_key is not None:
            return existing_key
    for alias in aliases:
        existing_key = alias_index.get(alias)
        if existing_key is not None:
            return existing_key
    if isinstance(preferred_key, str) and preferred_key:
        return preferred_key
    for alias in aliases:
        if alias:
            return alias
    raise ValueError("items must include a canonical identifier")


def _register_identity_aliases(
    alias_index: dict[str, str],
    preferred_key: Any,
    aliases: list[str] | tuple[str, ...],
    identity_key: str,
) -> None:
    if isinstance(preferred_key, str) and preferred_key:
        alias_index[preferred_key] = identity_key
    for alias in aliases:
        alias_index[alias] = identity_key


def _merge_summary_fields(current: dict[str, Any], incoming: Mapping[str, Any]) -> None:
    for key, value in incoming.items():
        if key in {"importance", "total", "score_count"}:
            continue
        if key not in current and not key.startswith("_"):
            current[key] = value
    current_aliases = _identity_aliases(current)
    incoming_aliases = incoming.get("_identity_aliases", [])
    merged_aliases = current_aliases[:]
    for alias in incoming_aliases:
        if alias not in merged_aliases:
            merged_aliases.append(alias)
    current["_identity_aliases"] = merged_aliases
    if "feature" in incoming and "feature" not in current:
        current["_identity_key"] = incoming["feature"]
    else:
        current["_identity_key"] = current.get("_identity_key") or _preferred_identity_key(current)


def _copy_public_fields(item: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in item.items() if not key.startswith("_") and key != "total"}


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


def _infer_overview_terms(payload: Mapping[str, Any], fallback_term: str) -> set[str]:
    terms = {fallback_term}
    trend_summary = payload.get("trend_summary")
    if not isinstance(trend_summary, Mapping):
        return terms

    term_entries = trend_summary.get("terms")
    if not isinstance(term_entries, list):
        return terms

    for term_entry in term_entries:
        if not isinstance(term_entry, Mapping):
            continue
        term_key = term_entry.get("term_key")
        if isinstance(term_key, str) and term_key:
            terms.add(term_key)
    return terms
