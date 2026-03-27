from collections.abc import Mapping

_MIN_PROBABILITY = 0.05
_MAX_PROBABILITY = 0.95


def _coerce_float(value: object, default: float) -> float:
    if value is None:
        return default

    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def compute_risk_probability(row: Mapping[str, object]) -> float:
    """Compute a deterministic stub risk probability from basic student metrics."""
    failed_course_count = max(_coerce_float(row.get("failed_course_count"), 0.0), 0.0)
    avg_course_score = _clamp(_coerce_float(row.get("avg_course_score"), 70.0), 0.0, 100.0)
    attendance_normal_rate = _clamp(
        _coerce_float(row.get("attendance_normal_rate"), 0.8), 0.0, 1.0
    )
    risk_label = max(_coerce_float(row.get("risk_label"), 0.0), 0.0)

    raw_probability = (
        0.24
        + min(failed_course_count, 5.0) * 0.08
        + (100.0 - avg_course_score) * 0.0025
        + (1.0 - attendance_normal_rate) * 0.3
        + min(risk_label, 1.0) * 0.12
    )
    clamped_probability = _clamp(raw_probability, _MIN_PROBABILITY, _MAX_PROBABILITY)
    return round(clamped_probability, 2)


def map_risk_level(probability: float) -> str:
    if probability >= 0.75:
        return "high"
    if probability >= 0.45:
        return "medium"
    return "low"
