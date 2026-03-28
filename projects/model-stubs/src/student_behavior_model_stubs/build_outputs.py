from __future__ import annotations

import json
from datetime import datetime
from collections.abc import Mapping, Sequence

import pandas as pd

from student_behavior_model_stubs.scoring import build_dimension_scores
from student_behavior_model_stubs.scoring import compute_quadrant_label
from student_behavior_model_stubs.scoring import compute_risk_probability
from student_behavior_model_stubs.scoring import map_risk_level
from student_behavior_model_stubs.templates import build_report_payload

_MODEL_SUMMARY_AUC = 0.8347
_RESULT_COLUMNS = [
    "student_id",
    "term_key",
    "student_name",
    "major_name",
    "quadrant_label",
    "risk_probability",
    "risk_level",
    "dimension_scores_json",
]
_RISK_LEVEL_ORDER = ("high", "medium", "low")


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


def _count_distribution(values: pd.Series) -> dict[str, int]:
    counts = values.fillna("").astype(str).value_counts(dropna=False)
    return {str(key): int(counts[key]) for key in sorted(counts.index)}


def _count_risk_distribution(values: pd.Series) -> dict[str, int]:
    counts = values.fillna("").astype(str).value_counts(dropna=False)
    return {level: int(counts.get(level, 0)) for level in _RISK_LEVEL_ORDER}


def _term_sort_key(term_key: str) -> tuple[int, str]:
    parts = term_key.split("-")
    if len(parts) == 2 and all(part.isdigit() for part in parts):
        return int(parts[0]), f"{int(parts[1]):04d}"
    return 10**9, term_key


def build_overview_by_term(student_results: pd.DataFrame) -> dict[str, object]:
    if student_results.empty:
        return {
            "student_count": 0,
            "risk_distribution": {level: 0 for level in _RISK_LEVEL_ORDER},
            "quadrant_distribution": {},
            "major_risk_summary": [],
            "trend_summary": {"terms": []},
        }

    ordered_results = student_results.copy()
    ordered_results["risk_level"] = ordered_results["risk_level"].fillna("").astype(str)
    ordered_results["quadrant_label"] = ordered_results["quadrant_label"].fillna("").astype(str)
    ordered_results["major_name"] = ordered_results["major_name"].fillna("").astype(str)
    ordered_results["term_key"] = ordered_results["term_key"].fillna("").astype(str)
    ordered_results["risk_probability"] = pd.to_numeric(
        ordered_results["risk_probability"], errors="coerce"
    ).fillna(0.0)

    major_risk_summary: list[dict[str, object]] = []
    major_groups = sorted(
        ordered_results.groupby("major_name", sort=True),
        key=lambda item: item[0],
    )
    for major_name, major_frame in major_groups:
        major_risk_summary.append(
            {
                "major_name": major_name,
                "student_count": int(len(major_frame)),
                "high_risk_count": int((major_frame["risk_level"] == "high").sum()),
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
            }
        )

    return {
        "student_count": int(len(ordered_results)),
        "risk_distribution": _count_risk_distribution(ordered_results["risk_level"]),
        "quadrant_distribution": _count_distribution(ordered_results["quadrant_label"]),
        "major_risk_summary": major_risk_summary,
        "trend_summary": {"terms": trend_terms},
    }


def build_model_summary(*, now: datetime) -> dict[str, object]:
    if not isinstance(now, datetime):
        raise TypeError("now must be a datetime")

    return {
        "cluster_method": "stub-quadrant-rules",
        "risk_model": "stub-risk-rules",
        "target_label": "综合测评低等级风险",
        "auc": _MODEL_SUMMARY_AUC,
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
        row_result = {
            "student_id": student_id,
            "term_key": term_key,
            "student_name": _resolve_student_name(row, name_map),
            "major_name": _normalized_text(row.get("major_name")) or "",
            "quadrant_label": compute_quadrant_label(row),
            "risk_probability": risk_probability,
            "risk_level": map_risk_level(risk_probability),
            "dimension_scores_json": _dimension_scores_json(row),
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

    ordered_results = student_results.sort_values(
        by=["student_id", "term_key"], kind="stable"
    ).reset_index(drop=True)

    records: list[dict[str, object]] = []
    for row in ordered_results.to_dict(orient="records"):
        payload = build_report_payload(
            risk_level=str(row["risk_level"]),
            quadrant_label=str(row["quadrant_label"]),
            dimension_scores=_coerce_dimension_scores(row["dimension_scores_json"]),
        )
        records.append(
            {
                "student_id": row["student_id"],
                "term_key": row["term_key"],
                "top_factors": payload["top_factors"],
                "intervention_advice": payload["intervention_advice"],
                "report_text": payload["report_text"],
            }
        )

    return records
