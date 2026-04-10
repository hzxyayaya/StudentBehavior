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

MODEL_SUMMARY_BASE_FIELDS = (
    "cluster_method",
    "risk_model",
    "target_label",
    "auc",
    "updated_at",
)


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
        self._model_summary_payload = _normalize_model_summary_payload(
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

        should_use_term_fallback = term != self._overview_term

        if should_use_term_fallback:
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
            "term_gpa": _as_float(current_row.get("term_gpa")),
            "failed_course_count": _as_float(current_row.get("failed_course_count")),
            "borderline_course_count": _as_float(current_row.get("borderline_course_count")),
            "failed_course_ratio": _as_float(current_row.get("failed_course_ratio")),
            "academic_risk_score": _as_float(current_row.get("academic_risk_score")),
            "academic_risk_level": current_row.get("academic_risk_level"),
            "behavior_risk_score": _as_float(current_row.get("behavior_risk_score")),
            "behavior_risk_level": current_row.get("behavior_risk_level"),
            "intervention_priority_score": _as_float(current_row.get("intervention_priority_score")),
            "intervention_priority_level": current_row.get("intervention_priority_level"),
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

    def get_trajectory_analysis(self, *, term: str) -> dict[str, Any]:
        overview = self.get_overview(term)
        groups = self.get_groups(term=term)
        warnings = self.list_warnings(term=term, page=1, page_size=5)
        return {
            "term": term,
            "risk_trend_summary": _build_risk_trend_summary(
                _load_warning_rows(self._warnings_path or _resolve_warning_artifact_path(self._repo_root))
            ),
            "key_factors": overview.get("risk_factor_summary", []),
            "current_dimensions": overview.get("dimension_summary", []),
            "group_changes": groups.get("groups", []),
            "student_samples": warnings.get("items", []),
        }

    def get_development_analysis(self, *, term: str) -> dict[str, Any]:
        overview = self.get_overview(term)
        groups = self.get_groups(term=term)
        group_rows = groups.get("groups", [])
        warning_rows = _load_warning_rows(self._warnings_path or _resolve_warning_artifact_path(self._repo_root))
        term_rows = [row for row in warning_rows if row.get("term_key") == term]
        destination_analysis = _extract_destination_analysis(overview)
        return {
            "term": term,
            "major_comparison": _build_major_risk_summary(term_rows),
            "dimension_highlights": overview.get("dimension_summary", []),
            "group_direction_segments": [
                {
                    "group_segment": row.get("group_segment"),
                    "student_count": row.get("student_count"),
                    "avg_risk_score": row.get("avg_risk_score"),
                    "direction_label": _resolve_group_direction_label(row),
                    "protective_factors": row.get("protective_factors", []),
                    "top_factors": row.get("top_factors", []),
                    "avg_dimension_scores": row.get("avg_dimension_scores", []),
                }
                for row in group_rows
            ],
            "direction_chains": [
                {
                    "group_segment": row.get("group_segment"),
                    "direction_label": _resolve_group_direction_label(row),
                    "leading_protective_factor": _first_factor_name(row.get("protective_factors")),
                    "leading_dimension": _first_dimension_name(row.get("avg_dimension_scores")),
                    "avg_risk_score": row.get("avg_risk_score"),
                }
                for row in group_rows
            ],
            **destination_analysis,
        }

    def get_result_individual_profile(self, *, student_id: str, term: str) -> dict[str, Any]:
        profile = self.get_student_profile(student_id=student_id, term=term)
        return {
            "result_key": "student_individual_profile",
            "term": term,
            **profile,
        }

    def get_result_group_profile(self, *, term: str) -> dict[str, Any]:
        groups = self.get_groups(term=term)
        return {
            "result_key": "student_group_profile",
            "term": term,
            "groups": groups.get("groups", []),
        }

    def get_result_behavior_patterns(self, *, term: str) -> dict[str, Any]:
        overview = self.get_overview(term)
        groups = self.get_groups(term=term)
        destination_analysis = _extract_destination_analysis(overview)
        return {
            "result_key": "behavior_patterns",
            "term": term,
            "group_distribution": overview.get("group_distribution", {}),
            "group_patterns": [
                {
                    "group_segment": group.get("group_segment"),
                    "student_count": group.get("student_count"),
                    "avg_risk_level": group.get("avg_risk_level"),
                    "top_factors": group.get("top_factors", []),
                }
                for group in groups.get("groups", [])
            ],
            "behavior_destination_association": destination_analysis["behavior_destination_association"],
            "destination_segments": destination_analysis["destination_segments"],
        }

    def get_result_risk_probability(self, *, term: str) -> dict[str, Any]:
        overview = self.get_overview(term)
        return {
            "result_key": "risk_probability_layers",
            "term": term,
            "student_count": overview.get("student_count", 0),
            "risk_distribution": overview.get("risk_distribution", {}),
            "risk_band_distribution": overview.get("risk_band_distribution", {}),
        }

    def get_result_risk_warning_level(self, *, term: str) -> dict[str, Any]:
        overview = self.get_overview(term)
        warnings = self.list_warnings(term=term, page=1, page_size=10)
        return {
            "result_key": "risk_warning_levels",
            "term": term,
            "warning_counts": overview.get("risk_band_distribution", {}),
            "warning_items": warnings.get("items", []),
        }

    def get_result_key_factors(self, *, term: str) -> dict[str, Any]:
        overview = self.get_overview(term)
        return {
            "result_key": "key_factor_explanations",
            "term": term,
            "risk_factor_summary": overview.get("risk_factor_summary", []),
            "top_warning_factors": overview.get("top_warning_factors", []),
        }

    def get_result_intervention_advice(self, *, student_id: str, term: str) -> dict[str, Any]:
        report = self.get_student_report(student_id=student_id, term=term)
        return {
            "result_key": "intervention_advice",
            "term": term,
            "student_id": student_id,
            "intervention_advice": report.get("intervention_advice", []),
            "report_text": report.get("report_text"),
            "top_factors": report.get("top_factors", []),
        }

    def get_result_term_trend(self, *, term: str) -> dict[str, Any]:
        trajectory = self.get_trajectory_analysis(term=term)
        return {
            "result_key": "term_trend_analysis",
            "term": term,
            "risk_trend_summary": trajectory.get("risk_trend_summary", []),
        }

    def get_result_major_comparison(self, *, term: str) -> dict[str, Any]:
        development = self.get_development_analysis(term=term)
        return {
            "result_key": "major_comparison",
            "term": term,
            "major_comparison": development.get("major_comparison", []),
            "destination_distribution": development.get("destination_distribution", {}),
            "major_destination_summary": development.get("major_destination_summary", []),
            "major_destination_comparison": development.get("major_destination_comparison", []),
        }

    def get_result_model_summary(self, *, term: str) -> dict[str, Any]:
        model_summary = self.get_model_summary(term=term)
        return {
            "result_key": "model_summary",
            "term": term,
            **model_summary,
        }

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
            and (
                allowed_levels is None
                or _normalize_risk_level(
                    row.get("intervention_priority_level") or row.get("risk_level")
                )
                in allowed_levels
            )
            and (group_segment is None or row["group_segment"] == group_segment)
            and (major_name is None or row["major_name"] == major_name)
            and (
                risk_change_direction is None
                or row.get("risk_change_direction") == risk_change_direction
            )
        ]
        filtered_rows.sort(
            key=lambda row: (
                -_as_float(row.get("risk_probability"))
                if _as_float(row.get("risk_probability")) is not None
                else float("inf"),
                row["student_id"],
            )
        )

        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        items = [
            {
                "student_id": row.get("student_id"),
                "student_name": row.get("student_name"),
                "major_name": row.get("major_name"),
                "group_segment": row.get("group_segment"),
                "risk_probability": row.get("risk_probability"),
                "term_gpa": _as_float(row.get("term_gpa")),
                "failed_course_count": _as_float(row.get("failed_course_count")),
                "borderline_course_count": _as_float(row.get("borderline_course_count")),
                "failed_course_ratio": _as_float(row.get("failed_course_ratio")),
                "academic_risk_score": _as_float(row.get("academic_risk_score")),
                "academic_risk_level": row.get("academic_risk_level"),
                "behavior_risk_score": _as_float(row.get("behavior_risk_score")),
                "behavior_risk_level": row.get("behavior_risk_level"),
                "intervention_priority_score": _as_float(row.get("intervention_priority_score")),
                "intervention_priority_level": row.get("intervention_priority_level"),
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


def _normalize_model_summary_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    summary = {field_name: payload[field_name] for field_name in MODEL_SUMMARY_BASE_FIELDS}
    for field_name, value in payload.items():
        if field_name not in summary and field_name not in {"term", "result_key"}:
            summary[field_name] = value
    return summary


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


def _extract_destination_analysis(overview: Mapping[str, Any]) -> dict[str, Any]:
    destination_distribution = _first_mapping_value(
        overview,
        "destination_distribution",
    )
    major_destination_summary = _first_list_value(
        overview,
        "major_destination_summary",
        "major_destination_comparison",
    )
    group_destination_association = _first_list_value(
        overview,
        "group_destination_association",
        "group_destination_summary",
        "behavior_destination_association",
        "destination_segments",
    )
    has_destination_truth = bool(
        destination_distribution or major_destination_summary or group_destination_association
    )
    disclaimer = (
        "去向分析已接入真实毕业去向数据；无匹配数据时相关字段返回空结果"
        if has_destination_truth
        else "去向真值暂未接入"
    )
    return {
        "destination_distribution": destination_distribution,
        "major_destination_summary": major_destination_summary,
        "group_destination_association": group_destination_association,
        "destination_segments": list(group_destination_association),
        "major_destination_comparison": list(major_destination_summary),
        "behavior_destination_association": list(group_destination_association),
        "disclaimer": disclaimer,
    }


def _first_mapping_value(payload: Mapping[str, Any], *keys: str) -> dict[str, Any]:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, Mapping):
            return dict(value)
    return {}


def _first_list_value(payload: Mapping[str, Any], *keys: str) -> list[Any]:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, list):
            return list(value)
    return []


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
        "provenance",
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
        risk_level = _normalize_risk_level(
            row.get("intervention_priority_level") or row.get("risk_level")
        ) or row.get("intervention_priority_level") or row.get("risk_level")
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
                "elevated_risk_count": 1.0 if _warning_level_priority(risk_level) >= 3 else 0.0,
            }
            continue
        current["student_count"] += 1.0
        current["risk_probability_total"] += float(risk_probability)
        if risk_level == "高风险":
            current["high_risk_count"] += 1.0
        if _warning_level_priority(risk_level) >= 3:
            current["elevated_risk_count"] += 1.0

    summaries = [
        {
            "major_name": major_name,
            "student_count": int(values["student_count"]),
            "high_risk_count": int(values["high_risk_count"]),
            "elevated_risk_count": int(values["elevated_risk_count"]),
            "elevated_risk_ratio": round(values["elevated_risk_count"] / values["student_count"], 4),
            "average_risk_probability": round(
                values["risk_probability_total"] / values["student_count"], 2
            ),
        }
        for major_name, values in stats.items()
    ]
    summaries.sort(
        key=lambda item: (
            -item["elevated_risk_ratio"],
            -item["elevated_risk_count"],
            -item["average_risk_probability"],
            item["major_name"],
        )
    )
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


def _build_risk_trend_summary(rows: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    stats: dict[str, dict[str, float]] = {}
    for row in rows:
        term_key = row.get("term_key")
        if not isinstance(term_key, str) or not term_key:
            continue
        risk_probability = row.get("risk_probability")
        if not isinstance(risk_probability, (int, float)):
            continue
        normalized_level = _normalize_risk_level(
            row.get("intervention_priority_level") or row.get("risk_level")
        )
        current = stats.get(term_key)
        if current is None:
            stats[term_key] = {
                "student_count": 1.0,
                "risk_probability_total": float(risk_probability),
                "high_risk_count": 1.0 if _normalize_risk_level(row.get("risk_level")) == "高风险" else 0.0,
            }
            stats[term_key]["elevated_risk_count"] = 1.0 if _warning_level_priority(normalized_level) >= 3 else 0.0
            continue
        current["student_count"] += 1.0
        current["risk_probability_total"] += float(risk_probability)
        if _normalize_risk_level(row.get("risk_level")) == "高风险":
            current["high_risk_count"] += 1.0
        if _warning_level_priority(normalized_level) >= 3:
            current["elevated_risk_count"] += 1.0

    rows_out = [
        {
            "term": term_key,
            "avg_risk_score": round((values["risk_probability_total"] / values["student_count"]) * 100, 1),
            "high_risk_count": int(values["high_risk_count"]),
            "elevated_risk_count": int(values["elevated_risk_count"]),
        }
        for term_key, values in stats.items()
    ]
    rows_out.sort(key=lambda item: _sort_term_key({"term_key": item["term"]}))
    return rows_out


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


def _warning_level_priority(level: Any) -> int:
    normalized = _normalize_risk_level(level)
    order = {
        "高风险": 4,
        "较高风险": 3,
        "一般风险": 2,
        "低风险": 1,
    }
    return order.get(normalized or "", 0)


def _finalize_dimension_summary(value: Mapping[str, Any]) -> dict[str, Any]:
    summary = _copy_public_fields(value)
    summary["average_score"] = round(float(value["total"]) / int(value["score_count"]), 2)
    summary["score_count"] = int(value["score_count"])
    return summary


def _resolve_allowed_risk_levels(risk_level: str | None) -> set[str] | None:
    if risk_level is None:
        return None
    normalized = _normalize_risk_level(risk_level)
    if normalized == "高风险":
        return {"高风险", "较高风险"}
    if normalized == "较高风险":
        return {"较高风险"}
    if normalized == "一般风险":
        return {"一般风险"}
    if normalized == "低风险":
        return {"低风险"}
    return {risk_level}


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
    current_is_unavailable = _summary_item_is_unavailable(current)
    incoming_is_unavailable = _summary_item_is_unavailable(incoming)

    if current_is_unavailable and not incoming_is_unavailable:
        for key in ("level", "label", "metrics", "explanation", "provenance"):
            if key in incoming:
                current[key] = incoming[key]
    elif not current_is_unavailable and incoming_is_unavailable:
        incoming = {
            key: value
            for key, value in incoming.items()
            if key not in {"level", "label", "metrics", "explanation", "provenance"}
        }

    for key, value in incoming.items():
        if key in {"importance", "total", "score_count"}:
            continue
        if key.startswith("_"):
            continue
        if key not in current:
            current[key] = value
            continue
        if current[key] in (None, "", []) and value not in (None, "", []):
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


def _summary_item_is_unavailable(item: Mapping[str, Any]) -> bool:
    provenance = item.get("provenance")
    if isinstance(provenance, Mapping) and provenance.get("is_unavailable") is True:
        return True
    return item.get("label") == "当前学期无有效数据"


def _copy_public_fields(item: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in item.items() if not key.startswith("_") and key != "total"}


def _resolve_group_direction_label(row: Mapping[str, Any]) -> str:
    protective_name = _first_factor_name(row.get("protective_factors"))
    top_dimension = _first_factor_dimension(row.get("top_factors"))
    if protective_name:
        return f"偏向 {protective_name}"
    if top_dimension:
        return f"偏向 {top_dimension}"
    return "方向特征待补充"


def _first_factor_name(raw: Any) -> str | None:
    if not isinstance(raw, list) or not raw:
        return None
    first = raw[0]
    if not isinstance(first, Mapping):
        return None
    value = first.get("feature_cn") or first.get("feature")
    return value if isinstance(value, str) and value else None


def _first_factor_dimension(raw: Any) -> str | None:
    if not isinstance(raw, list) or not raw:
        return None
    first = raw[0]
    if not isinstance(first, Mapping):
        return None
    value = first.get("dimension")
    return value if isinstance(value, str) and value else None


def _first_dimension_name(raw: Any) -> str | None:
    if not isinstance(raw, list) or not raw:
        return None
    first = raw[0]
    if not isinstance(first, Mapping):
        return None
    value = first.get("dimension")
    return value if isinstance(value, str) and value else None


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
