from __future__ import annotations

import json
from collections.abc import Mapping, Sequence

import pandas as pd

from student_behavior_model_stubs.scoring import build_dimension_scores
from student_behavior_model_stubs.scoring import compute_quadrant_label
from student_behavior_model_stubs.scoring import compute_risk_probability
from student_behavior_model_stubs.scoring import map_risk_level
from student_behavior_model_stubs.templates import build_report_payload

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
    records: list[dict[str, object]] = []
    for row in student_results.to_dict(orient="records"):
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
