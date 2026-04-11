from __future__ import annotations

import json
from datetime import datetime
from collections.abc import Mapping, Sequence
from pathlib import Path

import pandas as pd

from student_behavior_model_stubs.model_registry import build_default_model_registry
from student_behavior_model_stubs.llm_reporting import build_report_payload_with_fallback
from student_behavior_model_stubs.llm_reporting import load_llm_reporting_settings
from student_behavior_model_stubs.scoring import build_dimension_scores
from student_behavior_model_stubs.scoring import compute_group_segment
from student_behavior_model_stubs.scoring import compute_risk_probability
from student_behavior_model_stubs.scoring import build_risk_calibration
from student_behavior_model_stubs.templates import build_report_payload

_MODEL_SUMMARY_AUC = 0.8347
_RESULT_COLUMNS = [
    "student_id",
    "term_key",
    "student_name",
    "major_name",
    "destination_label",
    "destination_source",
    "group_segment",
    "risk_probability",
    "term_gpa",
    "failed_course_count",
    "borderline_course_count",
    "failed_course_ratio",
    "academic_risk_score",
    "academic_risk_level",
    "behavior_risk_score",
    "behavior_risk_level",
    "intervention_priority_score",
    "intervention_priority_level",
    "base_risk_score",
    "risk_adjustment_score",
    "adjusted_risk_score",
    "risk_level",
    "risk_delta",
    "risk_change_direction",
    "dimension_scores_json",
    "top_risk_factors",
    "top_risk_factors_json",
    "top_protective_factors",
    "top_protective_factors_json",
    "base_risk_explanation",
    "behavior_adjustment_explanation",
    "risk_change_explanation",
]
_RISK_LEVEL_ORDER = ("高风险", "较高风险", "一般风险", "低风险")
_RISK_PRIORITY = {level: index + 1 for index, level in enumerate(_RISK_LEVEL_ORDER)}
_DESTINATION_LABEL_PRECEDENCE = {
    "升学": 0,
    "体制内": 1,
    "出国出境": 2,
    "企业就业": 3,
    "待定其他": 4,
}
_MODEL_SUMMARY_STUB = {
    "cluster_method": "stub-eight-dimension-group-rules",
    "risk_model": "stub-eight-dimension-risk-rules",
    "target_label": "学期级八维学业风险",
    "auc": _MODEL_SUMMARY_AUC,
}


def _normalized_text(value: object) -> str | None:
    if value is None or pd.isna(value):
        return None

    text = str(value).strip()
    if not text or text.lower() == "nan":
        return None
    return text


def _student_name_map(students: pd.DataFrame | None) -> dict[str, str]:
    if students is None or "student_id" not in students.columns or "student_name" not in students.columns:
        return {}

    name_map: dict[str, str] = {}
    for row in students.itertuples(index=False):
        student_id = _normalized_text(getattr(row, "student_id", None))
        student_name = _normalized_text(getattr(row, "student_name", None))
        if student_id and student_name and student_id not in name_map:
            name_map[student_id] = student_name
    return name_map


def _dimension_scores_json(row: Mapping[str, object]) -> str:
    dimension_scores = build_dimension_scores(row)
    return json.dumps(dimension_scores, ensure_ascii=False, separators=(",", ":"))


def _json_dump(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def _json_load(value: object) -> object:
    if isinstance(value, str):
        return json.loads(value)
    return value


def _numeric_value(row: Mapping[str, object], *keys: str) -> float | None:
    for key in keys:
        value = row.get(key)
        if value is None or pd.isna(value):
            continue
        try:
            return float(value)
        except (TypeError, ValueError):
            continue
    return None


def _factor_names(factors: Sequence[Mapping[str, object]]) -> str:
    names: list[str] = []
    for item in factors:
        name = _normalized_text(item.get("feature_cn", ""))
        if name:
            names.append(name)
    return "、".join(names)


def _count_distribution(values: pd.Series) -> dict[str, int]:
    counts = values.fillna("").astype(str).value_counts(dropna=False)
    return {str(key): int(counts[key]) for key in sorted(counts.index)}


def _count_present_distribution(values: pd.Series) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        text = _normalized_text(value)
        if text is None:
            continue
        counts[text] = counts.get(text, 0) + 1
    return {key: counts[key] for key in sorted(counts, key=_destination_label_sort_key)}


def _count_risk_distribution(values: pd.Series) -> dict[str, int]:
    counts = values.fillna("").astype(str).value_counts(dropna=False)
    return {level: int(counts.get(level, 0)) for level in _RISK_LEVEL_ORDER}


def _resolve_checkout_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / ".git").exists():
            return parent
    raise RuntimeError("unable to locate checkout root")


def _build_trained_model_summary_fields() -> dict[str, object]:
    try:
        metrics = build_default_model_registry(_resolve_checkout_root()).load_metrics()
    except (RuntimeError, OSError, UnicodeDecodeError, json.JSONDecodeError):
        return {}
    if metrics is None:
        return {}

    summary: dict[str, object] = {"source": "trained"}
    text_fields = ("model_name", "target_label", "trained_at", "evaluated_at")
    summary_keys = {
        "model_name": "risk_model",
        "target_label": "target_label",
        "trained_at": "trained_at",
        "evaluated_at": "evaluated_at",
    }
    for field_name in text_fields:
        value = _normalized_text(metrics.get(field_name))
        if value is not None:
            summary[summary_keys[field_name]] = value

    for field_name in (
        "auc",
        "accuracy",
        "precision",
        "recall",
        "f1",
        "sample_count",
        "positive_sample_count",
        "negative_sample_count",
        "train_sample_count",
        "valid_sample_count",
        "test_sample_count",
        "feature_count",
    ):
        value = metrics.get(field_name)
        if value is None or pd.isna(value):
            continue
        summary[field_name] = value

    return summary


def _top_warning_factors(student_results: pd.DataFrame, limit: int = 3) -> list[dict[str, object]]:
    if student_results.empty:
        return []
    dimension_summary = sorted(
        _average_dimension_scores(student_results["dimension_scores_json"]),
        key=lambda item: (float(item["average_score"]), str(item["dimension_code"])),
    )
    return dimension_summary[:limit]


def _intervention_priority_summary(student_results: pd.DataFrame) -> list[dict[str, object]]:
    if student_results.empty:
        return [
            {"risk_level": level, "priority": priority, "student_count": 0, "share": 0.0}
            for level, priority in _RISK_PRIORITY.items()
        ]

    total = max(int(len(student_results)), 1)
    counts = _count_risk_distribution(student_results["risk_level"])
    return [
        {
            "risk_level": level,
            "priority": _RISK_PRIORITY[level],
            "student_count": counts[level],
            "share": round(counts[level] / total, 4),
        }
        for level in _RISK_LEVEL_ORDER
    ]


def _destination_label_sort_key(label: str) -> tuple[int, str]:
    return _DESTINATION_LABEL_PRECEDENCE.get(label, 99), label


def _top_distribution_item(distribution: Mapping[str, int]) -> tuple[str | None, int]:
    if not distribution:
        return None, 0
    label, count = min(distribution.items(), key=lambda item: (-item[1], *_destination_label_sort_key(item[0])))
    return label, count


def _major_destination_summary(student_results: pd.DataFrame) -> list[dict[str, object]]:
    summary: list[dict[str, object]] = []
    for major_name, major_frame in sorted(
        student_results.groupby("major_name", sort=True),
        key=lambda item: item[0],
    ):
        distribution = _count_present_distribution(major_frame["destination_label"])
        top_destination_label, top_destination_count = _top_distribution_item(distribution)
        summary.append(
            {
                "major_name": major_name,
                "student_count": int(len(major_frame)),
                "destination_student_count": int(sum(distribution.values())),
                "top_destination_label": top_destination_label,
                "top_destination_count": top_destination_count,
                "destination_distribution": distribution,
            }
        )
    return summary


def _group_destination_association(student_results: pd.DataFrame) -> list[dict[str, object]]:
    association_rows = student_results.copy()
    association_rows["destination_label"] = association_rows["destination_label"].map(_normalized_text)
    association_rows = association_rows.dropna(subset=["destination_label"])
    if association_rows.empty:
        return []

    group_student_counts = {
        str(group_segment): int(len(group_frame))
        for group_segment, group_frame in student_results.groupby("group_segment", sort=True)
    }
    association: list[dict[str, object]] = []
    for (group_segment, destination_label), group_frame in sorted(
        association_rows.groupby(["group_segment", "destination_label"], sort=True),
        key=lambda item: (str(item[0][0]), *_destination_label_sort_key(str(item[0][1]))),
    ):
        total_students = max(group_student_counts[str(group_segment)], 1)
        association.append(
            {
                "group_segment": str(group_segment),
                "destination_label": str(destination_label),
                "student_count": int(len(group_frame)),
                "group_student_count": total_students,
                "share_within_group": round(float(len(group_frame)) / total_students, 4),
            }
        )
    return association


def _term_sort_key(term_key: str) -> tuple[int, str]:
    parts = term_key.split("-")
    if len(parts) == 2 and all(part.isdigit() for part in parts):
        return int(parts[0]), f"{int(parts[1]):04d}"
    return 10**9, term_key


def _dedupe_students_by_latest_term(student_results: pd.DataFrame) -> pd.DataFrame:
    if student_results.empty or "student_id" not in student_results.columns:
        return student_results.copy()

    ordered = student_results.copy()
    ordered["student_id"] = ordered["student_id"].fillna("").astype(str)
    ordered["term_key"] = ordered["term_key"].fillna("").astype(str)
    ordered["__term_sort_key"] = ordered["term_key"].map(_term_sort_key)
    ordered = ordered.sort_values(
        by=["student_id", "__term_sort_key"],
        ascending=[True, False],
        kind="stable",
    )
    deduped = ordered.drop_duplicates(subset=["student_id"], keep="first").reset_index(drop=True)
    return deduped.drop(columns=["__term_sort_key"])


def _dimension_is_available(item: Mapping[str, object]) -> bool:
    provenance = item.get("provenance")
    if isinstance(provenance, Mapping) and provenance.get("is_unavailable") is True:
        return False
    return True


def _group_segment_from_dimension_items(items: Sequence[Mapping[str, object]]) -> str:
    by_code = {str(item.get("dimension_code", "")): item for item in items}

    def score(code: str) -> float:
        try:
            return float(by_code[code].get("score"))
        except (KeyError, TypeError, ValueError):
            return 0.0

    def available(code: str) -> bool:
        return code in by_code and _dimension_is_available(by_code[code])

    academic = score("academic_base")
    class_engagement = score("class_engagement")
    online = score("online_activeness")
    network = score("network_habits")
    daily = score("daily_routine_boundary")
    physical = score("physical_resilience")
    appraisal = score("appraisal_status_alert")

    if (
        available("academic_base")
        and available("class_engagement")
        and available("online_activeness")
        and available("daily_routine_boundary")
        and academic >= 0.8
        and class_engagement >= 0.75
        and online >= 0.7
        and daily >= 0.65
    ):
        return "学习投入稳定组"
    if (
        available("academic_base")
        and available("physical_resilience")
        and available("appraisal_status_alert")
        and academic >= 0.7
        and physical >= 0.75
        and appraisal >= 0.7
    ):
        return "综合发展优势组"
    if (
        (available("network_habits") and network < 0.45)
        or (available("daily_routine_boundary") and daily < 0.45)
    ):
        return "作息失衡风险组"
    return "课堂参与薄弱组"


def _dedupe_students_by_latest_available_dimensions(student_results: pd.DataFrame) -> pd.DataFrame:
    if student_results.empty or "student_id" not in student_results.columns:
        return student_results.copy()

    ordered = student_results.copy()
    ordered["student_id"] = ordered["student_id"].fillna("").astype(str)
    ordered["term_key"] = ordered["term_key"].fillna("").astype(str)
    ordered["__term_sort_key"] = ordered["term_key"].map(_term_sort_key)
    ordered = ordered.sort_values(
        by=["student_id", "__term_sort_key"],
        ascending=[True, False],
        kind="stable",
    )

    synthesized_rows: list[dict[str, object]] = []
    for _, student_frame in ordered.groupby("student_id", sort=False):
        base_row = student_frame.iloc[0].to_dict()
        latest_items_by_code: dict[str, dict[str, object]] = {}
        unavailable_items_by_code: dict[str, dict[str, object]] = {}
        for raw_scores in student_frame["dimension_scores_json"]:
            for item in _coerce_dimension_scores(raw_scores):
                if not isinstance(item, Mapping):
                    continue
                code = str(item.get("dimension_code", "")).strip()
                if not code:
                    continue
                if _dimension_is_available(item):
                    latest_items_by_code.setdefault(code, dict(item))
                else:
                    unavailable_items_by_code.setdefault(code, dict(item))
        merged_items: list[dict[str, object]] = []
        for code in (
            "academic_base",
            "class_engagement",
            "online_activeness",
            "library_immersion",
            "network_habits",
            "daily_routine_boundary",
            "physical_resilience",
            "appraisal_status_alert",
        ):
            item = latest_items_by_code.get(code) or unavailable_items_by_code.get(code)
            if item is not None:
                merged_items.append(item)
        if merged_items:
            base_row["dimension_scores_json"] = _json_dump(merged_items)
            base_row["group_segment"] = _group_segment_from_dimension_items(merged_items)
        synthesized_rows.append(base_row)

    result = pd.DataFrame.from_records(synthesized_rows)
    if "__term_sort_key" in result.columns:
        result = result.drop(columns=["__term_sort_key"])
    return result


def _average_dimension_scores(
    rows: Sequence[object],
) -> list[dict[str, object]]:
    totals: dict[str, dict[str, object]] = {}
    for value in rows:
        for item in _coerce_dimension_scores(value):
            provenance = item.get("provenance")
            if isinstance(provenance, Mapping) and provenance.get("is_unavailable") is True:
                continue
            dimension_code = str(item.get("dimension_code", "")).strip()
            dimension = str(item.get("dimension", "")).strip()
            try:
                score = float(item.get("score"))
            except (TypeError, ValueError):
                continue
            if pd.isna(score):
                continue
            if not dimension_code or not dimension:
                continue
            bucket = totals.setdefault(
                dimension_code,
                {
                    "dimension": dimension,
                    "dimension_code": dimension_code,
                    "score_total": 0.0,
                    "score_count": 0,
                },
            )
            bucket["score_total"] = float(bucket["score_total"]) + score
            bucket["score_count"] = int(bucket["score_count"]) + 1

    averaged: list[dict[str, object]] = []
    for bucket in totals.values():
        count = int(bucket["score_count"])
        if count == 0:
            continue
        averaged.append(
            {
                "dimension": str(bucket["dimension"]),
                "dimension_code": str(bucket["dimension_code"]),
                "average_score": round(float(bucket["score_total"]) / count, 2),
            }
        )
    return sorted(averaged, key=lambda item: str(item["dimension_code"]))


def build_overview_by_term(student_results: pd.DataFrame) -> dict[str, object]:
    if student_results.empty:
        return {
            "student_count": 0,
            "risk_distribution": {level: 0 for level in _RISK_LEVEL_ORDER},
            "risk_band_distribution": {level: 0 for level in _RISK_LEVEL_ORDER},
            "group_distribution": {},
            "major_risk_summary": [],
            "destination_distribution": {},
            "major_destination_summary": [],
            "group_destination_association": [],
            "risk_trend_summary": {"terms": []},
            "trend_summary": {"terms": []},
            "dimension_summary": [],
            "group_score_summary": {},
            "risk_factor_summary": [],
            "top_warning_factors": [],
            "priority_interventions": [],
            "intervention_priority_summary": [],
        }

    ordered_results = student_results.copy()
    if "risk_level" in ordered_results.columns:
        risk_levels = ordered_results["risk_level"]
    elif "intervention_priority_level" in ordered_results.columns:
        risk_levels = ordered_results["intervention_priority_level"]
    else:
        risk_levels = pd.Series("", index=ordered_results.index)
    ordered_results["risk_level"] = risk_levels.fillna("").astype(str)
    ordered_results["group_segment"] = ordered_results["group_segment"].fillna("").astype(str)
    ordered_results["major_name"] = ordered_results["major_name"].fillna("").astype(str)
    ordered_results["term_key"] = ordered_results["term_key"].fillna("").astype(str)
    for column in ("destination_label", "destination_source"):
        if column in ordered_results.columns:
            ordered_results[column] = ordered_results[column].astype(object)
        else:
            ordered_results[column] = pd.Series(index=ordered_results.index, dtype=object)
    if "risk_probability" in ordered_results.columns:
        risk_probabilities = ordered_results["risk_probability"]
    elif "adjusted_risk_score" in ordered_results.columns:
        risk_probabilities = ordered_results["adjusted_risk_score"]
    else:
        risk_probabilities = pd.Series(0.0, index=ordered_results.index)
    ordered_results["risk_probability"] = pd.to_numeric(risk_probabilities, errors="coerce").fillna(0.0)
    intervention_levels = (
        ordered_results["intervention_priority_level"].fillna("").astype(str)
        if "intervention_priority_level" in ordered_results.columns
        else ordered_results["risk_level"]
    )
    display_results = _dedupe_students_by_latest_available_dimensions(ordered_results)
    display_intervention_levels = (
        display_results["intervention_priority_level"].fillna("").astype(str)
        if "intervention_priority_level" in display_results.columns
        else display_results["risk_level"]
    )

    major_risk_summary: list[dict[str, object]] = []
    major_groups = sorted(
        display_results.groupby("major_name", sort=True),
        key=lambda item: item[0],
    )
    for major_name, major_frame in major_groups:
        major_risk_summary.append(
            {
                "major_name": major_name,
                "student_count": int(len(major_frame)),
                "high_risk_count": int((major_frame["risk_level"] == "高风险").sum()),
                "average_risk_probability": round(float(major_frame["risk_probability"].mean()), 2),
            }
        )

    trend_terms: list[dict[str, object]] = []
    for term_key, term_frame in sorted(
        ordered_results.groupby("term_key", sort=True), key=lambda item: _term_sort_key(item[0])
    ):
        risk_distribution = {
            level: int((term_frame["risk_level"] == level).sum()) for level in _RISK_LEVEL_ORDER
        }
        trend_terms.append(
            {
                "term_key": term_key,
                "student_count": int(len(term_frame)),
                "average_risk_probability": round(float(term_frame["risk_probability"].mean()), 2),
                "risk_distribution": risk_distribution,
                "dimension_summary": _average_dimension_scores(term_frame["dimension_scores_json"]),
            }
        )

    group_score_summary = {
        str(group_segment): _average_dimension_scores(group_frame["dimension_scores_json"])
        for group_segment, group_frame in sorted(
            display_results.groupby("group_segment", sort=True), key=lambda item: item[0]
        )
    }
    risk_band_distribution = _count_risk_distribution(display_results["risk_level"])
    risk_trend_summary = {"terms": trend_terms}
    top_warning_factors = _top_warning_factors(display_results)
    intervention_priority_summary = _intervention_priority_summary(
        display_results.assign(risk_level=display_intervention_levels)
    )
    destination_distribution = _count_present_distribution(display_results["destination_label"])
    major_destination_summary = _major_destination_summary(display_results)
    group_destination_association = _group_destination_association(display_results)

    return {
        "student_count": int(len(display_results)),
        "risk_distribution": risk_band_distribution,
        "risk_band_distribution": risk_band_distribution,
        "group_distribution": _count_distribution(display_results["group_segment"]),
        "major_risk_summary": major_risk_summary,
        "destination_distribution": destination_distribution,
        "major_destination_summary": major_destination_summary,
        "group_destination_association": group_destination_association,
        "trend_summary": risk_trend_summary,
        "risk_trend_summary": risk_trend_summary,
        "dimension_summary": _average_dimension_scores(display_results["dimension_scores_json"]),
        "group_score_summary": group_score_summary,
        "risk_factor_summary": top_warning_factors,
        "top_warning_factors": top_warning_factors,
        "priority_interventions": intervention_priority_summary,
        "intervention_priority_summary": intervention_priority_summary,
    }


def build_model_summary(*, now: datetime) -> dict[str, object]:
    if not isinstance(now, datetime):
        raise TypeError("now must be a datetime")

    trained_fields = _build_trained_model_summary_fields()
    if trained_fields and trained_fields.get("auc") is not None:
        return {
            **_MODEL_SUMMARY_STUB,
            "source": "stub",
            "updated_at": now.isoformat(timespec="seconds"),
            **trained_fields,
        }
    return {
        **_MODEL_SUMMARY_STUB,
        "source": "stub",
        "updated_at": now.isoformat(timespec="seconds"),
    }


def _resolve_student_name(
    row: Mapping[str, object],
    name_map: dict[str, str],
) -> str:
    student_id = _normalized_text(row.get("student_id"))
    if student_id is None:
        raise ValueError("student_id is required")

    for candidate in (
        name_map.get(student_id),
        _normalized_text(row.get("student_name")),
    ):
        if candidate:
            return candidate
    return student_id


def build_student_results(
    features: pd.DataFrame,
    students: pd.DataFrame | None = None,
) -> pd.DataFrame:
    name_map = _student_name_map(students)
    rows: list[dict[str, object]] = []

    for row in features.to_dict(orient="records"):
        student_id = _normalized_text(row.get("student_id"))
        term_key = _normalized_text(row.get("term_key"))
        if student_id is None or term_key is None:
            raise ValueError("student_id and term_key are required")

        risk_probability = compute_risk_probability(row)
        dimension_scores = build_dimension_scores(row)
        calibration = build_risk_calibration(row)
        report_payload = build_report_payload(
            base_risk_score=float(calibration["base_risk_score"]),
            risk_adjustment_score=float(calibration["risk_adjustment_score"]),
            adjusted_risk_score=float(calibration["adjusted_risk_score"]),
            risk_delta=float(calibration["risk_delta"]),
            risk_change_direction=str(calibration["risk_change_direction"]),
            risk_level=str(calibration["risk_level"]),
            group_segment=compute_group_segment(row),
            dimension_scores=dimension_scores,
        )
        row_result = {
            "student_id": student_id,
            "term_key": term_key,
            "student_name": _resolve_student_name(row, name_map),
            "major_name": _normalized_text(row.get("major_name")) or "",
            "destination_label": _normalized_text(row.get("destination_label")) or "",
            "destination_source": _normalized_text(row.get("destination_source")) or "",
            "group_segment": compute_group_segment(row),
            "risk_probability": risk_probability,
            "term_gpa": _numeric_value(row, "term_gpa", "avg_gpa", "avg_gpa_metric"),
            "failed_course_count": _numeric_value(row, "failed_course_count"),
            "borderline_course_count": _numeric_value(row, "borderline_course_count"),
            "failed_course_ratio": _numeric_value(row, "failed_course_ratio"),
            "academic_risk_score": calibration["academic_risk_score"],
            "academic_risk_level": calibration["academic_risk_level"],
            "behavior_risk_score": calibration["behavior_risk_score"],
            "behavior_risk_level": calibration["behavior_risk_level"],
            "intervention_priority_score": calibration["intervention_priority_score"],
            "intervention_priority_level": calibration["intervention_priority_level"],
            "base_risk_score": calibration["base_risk_score"],
            "risk_adjustment_score": calibration["risk_adjustment_score"],
            "adjusted_risk_score": calibration["adjusted_risk_score"],
            "risk_level": calibration["risk_level"],
            "risk_delta": calibration["risk_delta"],
            "risk_change_direction": calibration["risk_change_direction"],
            "dimension_scores_json": _json_dump(dimension_scores),
            "top_risk_factors": _factor_names(report_payload["top_risk_factors"]),
            "top_risk_factors_json": _json_dump(report_payload["top_risk_factors"]),
            "top_protective_factors": _factor_names(report_payload["top_protective_factors"]),
            "top_protective_factors_json": _json_dump(report_payload["top_protective_factors"]),
            "base_risk_explanation": report_payload["base_risk_explanation"],
            "behavior_adjustment_explanation": report_payload["behavior_adjustment_explanation"],
            "risk_change_explanation": report_payload["risk_change_explanation"],
        }
        rows.append(row_result)

    result_frame = pd.DataFrame(rows, columns=_RESULT_COLUMNS)
    if result_frame.empty:
        return result_frame

    return result_frame.sort_values(by=["student_id", "term_key"], kind="stable").reset_index(
        drop=True
    )


def _coerce_dimension_scores(value: object) -> list[dict[str, object]]:
    if isinstance(value, str):
        loaded = json.loads(value)
    elif isinstance(value, Sequence):
        loaded = list(value)
    else:
        loaded = []

    if not isinstance(loaded, list):
        raise ValueError("dimension_scores_json must decode to a list")
    return loaded


def build_student_reports(student_results: pd.DataFrame) -> list[dict[str, object]]:
    if student_results.empty:
        return []

    llm_settings = load_llm_reporting_settings()
    ordered_results = student_results.sort_values(
        by=["student_id", "term_key"], kind="stable"
    ).reset_index(drop=True)

    records: list[dict[str, object]] = []
    for row in ordered_results.to_dict(orient="records"):
        dimension_scores = _coerce_dimension_scores(row["dimension_scores_json"])
        payload = build_report_payload(
            base_risk_score=float(row["base_risk_score"]),
            risk_adjustment_score=float(row["risk_adjustment_score"]),
            adjusted_risk_score=float(row["adjusted_risk_score"]),
            risk_delta=float(row["risk_delta"]),
            risk_change_direction=str(row["risk_change_direction"]),
            risk_level=str(row["risk_level"]),
            group_segment=str(row["group_segment"]),
            dimension_scores=dimension_scores,
        )
        payload = build_report_payload_with_fallback(
            template_payload=payload,
            llm_settings=llm_settings,
        )
        priority_interventions = payload["priority_interventions"]
        records.append(
            {
                "student_id": row["student_id"],
                "term_key": row["term_key"],
                "version": payload["version"],
                "risk_level": payload["risk_level"],
                "base_risk_score": payload["base_risk_score"],
                "risk_adjustment_score": payload["risk_adjustment_score"],
                "adjusted_risk_score": payload["adjusted_risk_score"],
                "risk_delta": payload["risk_delta"],
                "risk_change_direction": payload["risk_change_direction"],
                "top_risk_factors": payload["top_risk_factors"],
                "top_protective_factors": payload["top_protective_factors"],
                "top_factors": payload["top_risk_factors"],
                "intervention_priority": payload["intervention_priority"],
                "priority_interventions": priority_interventions,
                "intervention_advice": [item["text"] for item in priority_interventions],
                "intervention_advice_items": priority_interventions,
                "intervention_plan": payload["intervention_plan"],
                "base_risk_explanation": payload["base_risk_explanation"],
                "behavior_adjustment_explanation": payload["behavior_adjustment_explanation"],
                "risk_change_explanation": payload["risk_change_explanation"],
                "report_text": payload["report_text"],
                "report_source": payload["report_source"],
                "prompt_version": payload["prompt_version"],
                "report_generation": payload["report_generation"],
            }
        )

    return records
