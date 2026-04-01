from collections.abc import Mapping
import math

from student_behavior_model_stubs.calibration import CALIBRATED_DIMENSIONS
from student_behavior_model_stubs.calibration import DIMENSION_LABELS
from student_behavior_model_stubs.calibration import METRIC_RULE_DECLARATIONS
from student_behavior_model_stubs.risk_calibration import build_risk_calibration as _build_risk_calibration
from student_behavior_model_stubs.risk_calibration import compute_adjusted_risk_score
from student_behavior_model_stubs.risk_calibration import compute_base_risk_score
from student_behavior_model_stubs.risk_calibration import compute_risk_adjustment_score
from student_behavior_model_stubs.risk_calibration import compute_risk_change_direction
from student_behavior_model_stubs.risk_calibration import compute_risk_delta
from student_behavior_model_stubs.risk_calibration import map_adjusted_risk_level

_MIN_PROBABILITY = 0.05
_MAX_PROBABILITY = 0.95
_RAW_SCORE_DEFAULT = 42.0

_GROUP_SEGMENTS = {
    "stable": "学习投入稳定组",
    "balanced": "综合发展优势组",
    "routine_risk": "作息失衡风险组",
    "class_risk": "课堂参与薄弱组",
}

_DIMENSION_BUSINESS_LABELS = {
    "academic_base": {"high": "学业基础稳健", "medium": "学业基础承压", "low": "学业基础预警"},
    "class_engagement": {"high": "课堂投入积极", "medium": "课堂投入一般", "low": "课堂投入薄弱"},
    "online_activeness": {"high": "在线学习活跃", "medium": "在线学习平稳", "low": "在线学习偏弱"},
    "library_immersion": {"high": "图书馆投入稳定", "medium": "图书馆投入一般", "low": "图书馆投入不足"},
    "network_habits": {"high": "网络作息自律", "medium": "网络使用可控", "low": "网络作息失衡"},
    "daily_routine_boundary": {"high": "作息边界稳定", "medium": "作息边界波动", "low": "作息边界失衡"},
    "physical_resilience": {"high": "体能状态良好", "medium": "体能状态一般", "low": "体能状态承压"},
    "appraisal_status_alert": {"high": "综合表现稳健", "medium": "综合表现波动", "low": "综合表现预警"},
}

_LEVEL_EXPLANATION_SUFFIX = {
    "high": "当前表现较稳定。",
    "medium": "当前表现存在波动，需要持续观察。",
    "low": "当前已进入优先关注区间。",
}

_DIMENSION_EXPLANATION_SUFFIX = {
    "network_habits": "当前网络使用强度需结合聚合时长观察。",
}

_MISSING_METRIC = object()

_METRIC_THRESHOLD_HINTS = {
    "term_gpa": (2.0, 4.0),
    "failed_course_count": (0.0, 4.0),
    "borderline_course_count": (0.0, 5.0),
    "failed_course_ratio": (0.0, 0.3),
    "attendance_rate": (0.75, 0.98),
    "late_count": (0.0, 8.0),
    "truancy_count": (0.0, 4.0),
    "absence_count": (0.0, 6.0),
    "video_completion_rate": (0.4, 1.0),
    "online_test_avg_score": (60.0, 90.0),
    "online_work_avg_score": (60.0, 90.0),
    "online_exam_avg_score": (60.0, 90.0),
    "platform_engagement_score": (40.0, 90.0),
    "forum_interaction_total": (0.0, 30.0),
    "library_completed_visit_count": (0.0, 30.0),
    "avg_library_stay_minutes": (20.0, 150.0),
    "weekly_library_visit_avg": (0.0, 4.0),
    "monthly_online_duration_avg": (20.0, 80.0),
    "term_online_duration_sum": (80.0, 240.0),
    "online_duration_vs_school_avg_gap": (0.0, 30.0),
    "first_daily_access_time_avg": (6.5, 9.5),
    "first_daily_access_time_std": (0.0, 2.5),
    "late_return_count": (0.0, 8.0),
    "late_return_ratio": (0.0, 0.3),
    "daily_access_time_variability": (0.0, 3.0),
    "physical_test_avg_score": (60.0, 95.0),
    "physical_test_pass_flag": (0.0, 1.0),
    "weekly_running_count_avg": (0.0, 4.0),
    "weekly_exercise_count_avg": (0.0, 5.0),
    "scholarship_amount_sum": (0.0, 5000.0),
    "scholarship_level_score": (0.0, 3.0),
    "negative_status_alert_flag": (0.0, 1.0),
    "status_change_count": (0.0, 3.0),
}


def _coerce_float(value: object, default: float) -> float:
    if value is None:
        return default
    try:
        coerced = float(value)
    except (TypeError, ValueError):
        return default
    if not math.isfinite(coerced):
        return default
    return coerced


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def _coerce_metric_value(value: object) -> float | int:
    if isinstance(value, bool):
        return int(value)
    number = _coerce_float(value, 0.0)
    rounded = round(number, 2)
    if rounded.is_integer():
        return int(rounded)
    return rounded


def _usable_metric_input(value: object) -> float | int | None | object:
    if value is None:
        return None
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (int, float)):
        numeric = float(value)
        if math.isfinite(numeric):
            return numeric
        return _MISSING_METRIC
    if isinstance(value, str):
        if not value.strip() or value.strip().lower() == "nan":
            return None
        return _MISSING_METRIC
    return _MISSING_METRIC


def _distribution_context(row: Mapping[str, object]) -> Mapping[str, Mapping[str, object]]:
    context = row.get("distribution_context")
    if isinstance(context, Mapping):
        return context
    return {}


def _metric_bounds(metric_name: str) -> tuple[float, float]:
    return _METRIC_THRESHOLD_HINTS.get(metric_name, (0.0, 100.0))


def _score_from_bounds(value: object, lower: float, upper: float, direction: str) -> float:
    numeric = _coerce_float(value, lower)
    if direction == "neutral":
        numeric = abs(numeric)
        direction = "negative"
    if upper <= lower:
        return 0.5
    position = _clamp((numeric - lower) / (upper - lower), 0.0, 1.0)
    score = position if direction == "positive" else 1.0 - position
    return round(_clamp(score, 0.0, 1.0), 2)


def _score_fixed_metric(metric_name: str, value: object, direction: str) -> float:
    lower, upper = _metric_bounds(metric_name)
    return _score_from_bounds(value, lower, upper, direction)


def _score_quantile_metric(
    metric_name: str,
    value: object,
    direction: str,
    distribution: Mapping[str, object] | None = None,
) -> float:
    distribution = distribution or {}
    lower = _coerce_float(distribution.get("q33"), math.nan)
    upper = _coerce_float(distribution.get("q67"), math.nan)
    if math.isnan(lower) or math.isnan(upper) or upper <= lower:
        lower, upper = _metric_bounds(metric_name)
    return _score_from_bounds(value, lower, upper, direction)


def _score_hybrid_metric(
    metric_name: str,
    value: object,
    direction: str,
    distribution: Mapping[str, object] | None = None,
) -> float:
    fixed_score = _score_fixed_metric(metric_name, value, direction)
    quantile_score = _score_quantile_metric(metric_name, value, direction, distribution)
    return round((fixed_score + quantile_score) / 2.0, 2)


def _score_metric(rule: Mapping[str, object], value: object, row: Mapping[str, object]) -> float:
    strategy = str(rule["threshold_strategy"])
    direction = str(rule["influence_direction"])
    metric_name = str(rule["metric"])
    distribution = _distribution_context(row).get(metric_name)
    if strategy == "fixed":
        return _score_fixed_metric(metric_name, value, direction)
    if strategy == "quantile":
        return _score_quantile_metric(metric_name, value, direction, distribution)
    return _score_hybrid_metric(metric_name, value, direction, distribution)


def _metric_value(row: Mapping[str, object], rule: Mapping[str, object]) -> object:
    metric_name = str(rule["metric"])
    if metric_name not in row:
        return _MISSING_METRIC
    value = _usable_metric_input(row[metric_name])
    if value is _MISSING_METRIC:
        return _MISSING_METRIC
    if value is None:
        return _MISSING_METRIC
    return value


def _build_metrics(
    dimension_code: str,
    row: Mapping[str, object],
) -> tuple[list[dict[str, object]], list[float]]:
    metrics: list[dict[str, object]] = []
    metric_scores: list[float] = []
    for rule in METRIC_RULE_DECLARATIONS[dimension_code]:
        value = _metric_value(row, rule)
        if value is _MISSING_METRIC:
            continue
        metrics.append(
            {
                "metric": rule["metric"],
                "label": rule["evidence_label"],
                "value": _coerce_metric_value(value),
                "threshold_strategy": rule["threshold_strategy"],
                "deferred_status": dict(rule["deferred_status"]),
                **({"caveat": rule["caveat"]} if "caveat" in rule else {}),
            }
        )
        metric_scores.append(_score_metric(rule, value, row))
    return metrics, metric_scores


def _score_level(score: float) -> str:
    if score >= 0.75:
        return "high"
    if score >= 0.45:
        return "medium"
    return "low"


def _format_metric_value(value: object) -> str:
    if isinstance(value, float):
        return f"{value:.2f}".rstrip("0").rstrip(".")
    return str(value)


def _aggregate_dimension_score(metric_scores: list[float]) -> float:
    if not metric_scores:
        return 0.0
    return round(sum(metric_scores) / len(metric_scores), 2)


def _primary_evidence_metrics(
    dimension_code: str,
    metrics: list[dict[str, object]],
) -> list[dict[str, object]]:
    primary_metric_names = [
        str(rule["metric"])
        for rule in METRIC_RULE_DECLARATIONS[dimension_code]
        if rule.get("evidence_role", "primary") == "primary"
    ]
    by_metric_name = {str(metric["metric"]): metric for metric in metrics}
    evidence = [
        by_metric_name[metric_name]
        for metric_name in primary_metric_names
        if metric_name in by_metric_name
    ]
    return evidence[:2]


def _build_explanation(
    dimension_code: str,
    level: str,
    label: str,
    metrics: list[dict[str, object]],
) -> str:
    evidence_metrics = _primary_evidence_metrics(dimension_code, metrics)
    metric_text = "、".join(
        f"{metric['label']} {_format_metric_value(metric['value'])}" for metric in evidence_metrics
    )
    if not metric_text:
        metric_text = "当前可用指标有限"
    suffix = _DIMENSION_EXPLANATION_SUFFIX.get(
        dimension_code,
        _LEVEL_EXPLANATION_SUFFIX[level],
    )
    explanation = f"{DIMENSION_LABELS[dimension_code]}处于{label}，主要依据是{metric_text}，{suffix}"
    caveats = []
    for metric in metrics:
        caveat = metric.get("caveat")
        if isinstance(caveat, str) and caveat not in caveats:
            caveats.append(caveat)
    if caveats and all(caveat not in explanation for caveat in caveats):
        explanation = f"{explanation} 说明：{'；'.join(caveats)}"
    return explanation


def _dimension_provenance(metrics: list[dict[str, object]]) -> dict[str, object]:
    threshold_strategies: list[str] = []
    has_deferred_metrics = False
    has_caveated_metrics = False
    for metric in metrics:
        threshold_strategy = str(metric["threshold_strategy"])
        if threshold_strategy not in threshold_strategies:
            threshold_strategies.append(threshold_strategy)
        deferred_status = metric.get("deferred_status")
        if isinstance(deferred_status, Mapping):
            if str(deferred_status.get("state", "none")) != "none":
                has_deferred_metrics = True
            if str(deferred_status.get("state", "none")) == "caveated":
                has_caveated_metrics = True
        if "caveat" in metric:
            has_caveated_metrics = True
    return {
        "has_caveated_metrics": has_caveated_metrics,
        "has_deferred_metrics": has_deferred_metrics,
        "threshold_strategies": threshold_strategies,
    }


def _dimension_score_map(row: Mapping[str, object]) -> dict[str, float]:
    return {str(item["dimension_code"]): float(item["score"]) for item in build_dimension_scores(row)}


def compute_risk_probability(row: Mapping[str, object]) -> float:
    academic = _coerce_float(row.get("academic_base_score_raw"), _RAW_SCORE_DEFAULT)
    class_engagement = _coerce_float(row.get("class_engagement_score_raw"), _RAW_SCORE_DEFAULT)
    online = _coerce_float(row.get("online_activeness_score_raw"), _RAW_SCORE_DEFAULT)
    daily = _coerce_float(row.get("daily_routine_boundary_score_raw"), _RAW_SCORE_DEFAULT)
    failed_course_count = max(_coerce_float(row.get("failed_course_count"), 0.0), 0.0)

    core_average = (academic + class_engagement + online + daily) / 4.0
    raw_probability = 0.23 + (100.0 - core_average) * 0.005 + min(failed_course_count, 5.0) * 0.05
    clamped_probability = _clamp(raw_probability, _MIN_PROBABILITY, _MAX_PROBABILITY)
    return round(clamped_probability, 2)


def map_risk_level(probability: float) -> str:
    if probability >= 0.75:
        return "high"
    if probability >= 0.45:
        return "medium"
    return "low"


def compute_group_segment(row: Mapping[str, object]) -> str:
    scores = _dimension_score_map(row)
    academic = scores["academic_base"]
    class_engagement = scores["class_engagement"]
    online = scores["online_activeness"]
    network = scores["network_habits"]
    daily = scores["daily_routine_boundary"]
    physical = scores["physical_resilience"]
    appraisal = scores["appraisal_status_alert"]

    if academic >= 0.8 and class_engagement >= 0.75 and online >= 0.7 and daily >= 0.65:
        return _GROUP_SEGMENTS["stable"]
    if academic >= 0.7 and physical >= 0.75 and appraisal >= 0.7:
        return _GROUP_SEGMENTS["balanced"]
    if network < 0.45 or daily < 0.45:
        return _GROUP_SEGMENTS["routine_risk"]
    return _GROUP_SEGMENTS["class_risk"]


def build_dimension_scores(row: Mapping[str, object]) -> list[dict[str, object]]:
    dimension_scores: list[dict[str, object]] = []
    for dimension_code in CALIBRATED_DIMENSIONS:
        metrics, metric_scores = _build_metrics(dimension_code, row)
        score = _aggregate_dimension_score(metric_scores)
        level = _score_level(score)
        label = _DIMENSION_BUSINESS_LABELS[dimension_code][level]
        dimension_scores.append(
            {
                "dimension": DIMENSION_LABELS[dimension_code],
                "dimension_code": dimension_code,
                "score": score,
                "level": level,
                "label": label,
                "metrics": metrics,
                "explanation": _build_explanation(dimension_code, level, label, metrics),
                "provenance": _dimension_provenance(metrics),
            }
        )
    return dimension_scores


def build_risk_calibration(row: Mapping[str, object]) -> dict[str, object]:
    return _build_risk_calibration(row, build_dimension_scores(row))
