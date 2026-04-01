from __future__ import annotations

import math
from collections.abc import Mapping, Sequence

_MIN_SCORE = 0.0
_MAX_SCORE = 100.0
_NON_ACADEMIC_NEUTRAL = 0.5
_NON_ACADEMIC_MULTIPLIER = 40.0

_RISK_LEVEL_LABELS = (
    (80.0, "高风险"),
    (65.0, "较高风险"),
    (45.0, "一般风险"),
)


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def _coerce_float(value: object, default: float) -> float:
    if value is None:
        return default
    try:
        coerced = float(value)
    except (TypeError, ValueError):
        return default
    if math.isnan(coerced):
        return default
    return coerced


def _gpa_health_score(row: Mapping[str, object]) -> float:
    gpa = _coerce_float(row.get("term_gpa"), math.nan)
    if not math.isnan(gpa):
        return _clamp((gpa - 1.5) / 2.5, 0.0, 1.0)

    academic_base_score = _coerce_float(row.get("academic_base_score_raw"), math.nan)
    if not math.isnan(academic_base_score):
        return _clamp(academic_base_score / 100.0, 0.0, 1.0)

    return 0.5


def compute_base_risk_score(row: Mapping[str, object]) -> float:
    """Compute the academic-only risk foundation on a 0-100 scale."""

    gpa_health = _gpa_health_score(row)
    failed_course_count = _clamp(_coerce_float(row.get("failed_course_count"), 0.0), 0.0, 5.0)
    borderline_course_count = _clamp(
        _coerce_float(row.get("borderline_course_count"), 0.0),
        0.0,
        5.0,
    )
    failed_course_ratio = _clamp(_coerce_float(row.get("failed_course_ratio"), 0.0), 0.0, 0.3)

    base_score = (
        (1.0 - gpa_health) * 45.0
        + (failed_course_count / 5.0) * 25.0
        + (borderline_course_count / 5.0) * 15.0
        + (failed_course_ratio / 0.3) * 15.0
    )
    return round(_clamp(base_score, _MIN_SCORE, _MAX_SCORE), 2)


def _dimension_score(item: Mapping[str, object]) -> float | None:
    if "score" not in item:
        return None
    score = _coerce_float(item.get("score"), math.nan)
    if math.isnan(score):
        return None
    return _clamp(score, 0.0, 1.0)


def compute_risk_adjustment_score(dimension_scores: Sequence[Mapping[str, object]]) -> float:
    """Convert non-academic dimension scores into a signed adjustment."""

    non_academic_scores: list[float] = []
    for item in dimension_scores:
        dimension_code = str(item.get("dimension_code", ""))
        if dimension_code == "academic_base":
            continue
        score = _dimension_score(item)
        if score is not None:
            non_academic_scores.append(score)

    if not non_academic_scores:
        return 0.0

    average_score = sum(non_academic_scores) / len(non_academic_scores)
    adjustment = (_NON_ACADEMIC_NEUTRAL - average_score) * _NON_ACADEMIC_MULTIPLIER
    return round(adjustment, 2)


def compute_adjusted_risk_score(base_risk_score: float, risk_adjustment_score: float) -> float:
    return round(_clamp(base_risk_score + risk_adjustment_score, _MIN_SCORE, _MAX_SCORE), 2)


def map_adjusted_risk_level(adjusted_risk_score: float) -> str:
    for threshold, label in _RISK_LEVEL_LABELS:
        if adjusted_risk_score >= threshold:
            return label
    return "低风险"


def compute_risk_delta(
    adjusted_risk_score: float,
    previous_adjusted_risk_score: float,
) -> float:
    return round(adjusted_risk_score - previous_adjusted_risk_score, 2)


def compute_risk_change_direction(risk_delta: float) -> str:
    if risk_delta > 0.5:
        return "rising"
    if risk_delta < -0.5:
        return "falling"
    return "steady"


def _previous_adjusted_risk_score(row: Mapping[str, object]) -> float | None:
    for key in (
        "previous_adjusted_risk_score",
        "previous_risk_score",
        "prior_adjusted_risk_score",
        "last_adjusted_risk_score",
    ):
        value = _coerce_float(row.get(key), math.nan)
        if not math.isnan(value):
            return value
    return None


def build_risk_calibration(
    row: Mapping[str, object],
    dimension_scores: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    base_risk_score = compute_base_risk_score(row)
    risk_adjustment_score = compute_risk_adjustment_score(dimension_scores)
    adjusted_risk_score = compute_adjusted_risk_score(base_risk_score, risk_adjustment_score)
    previous_adjusted_risk_score = _previous_adjusted_risk_score(row)
    if previous_adjusted_risk_score is None:
        risk_delta = 0.0
        risk_change_direction = "steady"
    else:
        risk_delta = compute_risk_delta(adjusted_risk_score, previous_adjusted_risk_score)
        risk_change_direction = compute_risk_change_direction(risk_delta)

    return {
        "base_risk_score": base_risk_score,
        "risk_adjustment_score": risk_adjustment_score,
        "adjusted_risk_score": adjusted_risk_score,
        "risk_level": map_adjusted_risk_level(adjusted_risk_score),
        "risk_delta": risk_delta,
        "risk_change_direction": risk_change_direction,
    }
