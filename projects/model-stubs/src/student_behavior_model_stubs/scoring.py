from collections.abc import Mapping
import math

_MIN_PROBABILITY = 0.05
_MAX_PROBABILITY = 0.95
_GROUP_SEGMENTS = {
    "self_resonant": "学习投入稳定组",
    "passive_disciplined": "综合发展优势组",
    "disconnected": "作息失衡风险组",
    "emotion_driven": "课堂参与薄弱组",
}

_DIMENSION_NAMES = [
    "学业基础表现",
    "课堂学习投入",
    "学习行为活跃度",
    "生活规律与资源使用",
]


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


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def _normalize_score(value: float) -> float:
    return round(_clamp(value, 0.0, 1.0), 2)


def compute_risk_probability(row: Mapping[str, object]) -> float:
    """Compute a deterministic stub risk probability from basic student metrics."""
    failed_course_count = max(_coerce_float(row.get("failed_course_count"), 0.0), 0.0)
    avg_course_score = _clamp(_coerce_float(row.get("avg_course_score"), 70.0), 0.0, 100.0)
    attendance_normal_rate = _clamp(
        _coerce_float(row.get("attendance_normal_rate"), 0.8), 0.0, 1.0
    )

    raw_probability = (
        0.24
        + min(failed_course_count, 5.0) * 0.08
        + (100.0 - avg_course_score) * 0.0025
        + (1.0 - attendance_normal_rate) * 0.3
    )
    clamped_probability = _clamp(raw_probability, _MIN_PROBABILITY, _MAX_PROBABILITY)
    return round(clamped_probability, 2)


def map_risk_level(probability: float) -> str:
    if probability >= 0.75:
        return "high"
    if probability >= 0.45:
        return "medium"
    return "low"


def compute_group_segment(row: Mapping[str, object]) -> str:
    attendance_normal_rate = _clamp(
        _coerce_float(row.get("attendance_normal_rate"), 0.0), 0.0, 1.0
    )
    sign_event_count = max(_coerce_float(row.get("sign_event_count"), 0.0), 0.0)
    selected_course_count = max(_coerce_float(row.get("selected_course_count"), 0.0), 0.0)
    avg_course_score = _clamp(_coerce_float(row.get("avg_course_score"), 0.0), 0.0, 100.0)
    failed_course_count = max(_coerce_float(row.get("failed_course_count"), 0.0), 0.0)

    academic_score = _clamp(
        (avg_course_score / 100.0) * 0.7 + (1.0 - min(failed_course_count, 5.0) / 5.0) * 0.3,
        0.0,
        1.0,
    )
    engagement_score = _clamp(
        attendance_normal_rate * 0.55
        + min(sign_event_count / 20.0, 1.0) * 0.25
        + min(selected_course_count / 10.0, 1.0) * 0.2,
        0.0,
        1.0,
    )

    if academic_score >= 0.75 and engagement_score >= 0.75:
        return _GROUP_SEGMENTS["self_resonant"]
    if academic_score >= 0.6 and engagement_score >= 0.45:
        return _GROUP_SEGMENTS["passive_disciplined"]
    if academic_score < 0.6 and engagement_score < 0.45:
        return _GROUP_SEGMENTS["disconnected"]
    return _GROUP_SEGMENTS["emotion_driven"]


def build_dimension_scores(row: Mapping[str, object]) -> list[dict[str, object]]:
    attendance_normal_rate = _clamp(
        _coerce_float(row.get("attendance_normal_rate"), 0.0), 0.0, 1.0
    )
    sign_event_count = max(_coerce_float(row.get("sign_event_count"), 0.0), 0.0)
    selected_course_count = max(_coerce_float(row.get("selected_course_count"), 0.0), 0.0)
    avg_course_score = _clamp(_coerce_float(row.get("avg_course_score"), 0.0), 0.0, 100.0)
    failed_course_count = max(_coerce_float(row.get("failed_course_count"), 0.0), 0.0)
    library_visit_count = max(_coerce_float(row.get("library_visit_count"), 0.0), 0.0)

    scores = {
        "学业基础表现": (avg_course_score / 100.0) * 0.8
        + (1.0 - min(failed_course_count, 5.0) / 5.0) * 0.2,
        "课堂学习投入": attendance_normal_rate * 0.65
        + min(selected_course_count / 12.0, 1.0) * 0.35,
        "学习行为活跃度": min(sign_event_count / 20.0, 1.0) * 0.7
        + min(library_visit_count / 25.0, 1.0) * 0.3,
        "生活规律与资源使用": attendance_normal_rate * 0.5
        + min(library_visit_count / 25.0, 1.0) * 0.5,
    }
    return [
        {"dimension": name, "score": _normalize_score(scores[name])}
        for name in _DIMENSION_NAMES
    ]
