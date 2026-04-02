from collections.abc import Iterable, Mapping


_DIMENSION_TEMPLATES = [
    ("学业基础表现", "academic_base"),
    ("课堂学习投入", "class_engagement"),
    ("在线学习积极性", "online_activeness"),
    ("图书馆沉浸度", "library_immersion"),
    ("网络作息自律指数", "network_habits"),
    ("早晚生活作息规律", "daily_routine_boundary"),
    ("体质及运动状况", "physical_resilience"),
    ("综合荣誉与异动预警", "appraisal_status_alert"),
]

_PROTECTIVE_DIMENSION_TEMPLATES = [
    item for item in _DIMENSION_TEMPLATES if item[1] != "academic_base"
]

_RISK_LEVEL_ALIASES = {
    "high": "高风险",
    "medium": "一般风险",
    "low": "低风险",
}

_RISK_LEVEL_PRIORITY = {
    "高风险": 1,
    "较高风险": 2,
    "一般风险": 3,
    "低风险": 4,
}

_DIMENSION_LEVEL_LABELS = {
    "high": "高",
    "medium": "中",
    "low": "低",
}

_INTERVENTION_TEMPLATES = {
    "高风险": [
        "立即围绕学业基础、课堂投入和作息边界制定一对一跟踪方案。",
        "同步核查可能的连续挂科、缺勤和夜间作息波动，优先止损。",
        "保留体质与荣誉等稳定优势，避免风险继续扩散。",
    ],
    "较高风险": [
        "聚焦最弱的两到三项维度，按周跟踪改善幅度。",
        "把课堂、在线学习和作息管理拆成可执行的小目标。",
        "维持现有优势项稳定，防止局部波动传导到学业结果。",
    ],
    "一般风险": [
        "执行轻量提醒和过程跟踪，重点观察是否出现连续下滑。",
        "围绕最低的三项维度做小步优化，避免短期波动放大。",
        "保持优势项稳定，按学期复盘一次结构变化。",
    ],
    "低风险": [
        "维持当前节奏，继续巩固高分维度的优势表现。",
        "围绕较弱维度做轻量补强，避免阶段性回落。",
        "按学期复盘一次八维画像，持续跟踪结构性变化。",
    ],
}

_INTERVENTION_KEYS = {
    "高风险": [
        "stabilize_core_learning",
        "set_routine_boundaries",
        "protect_strengths_focus_weakest",
    ],
    "较高风险": [
        "focus_worst_dimensions",
        "break_down_learning_and_routine_goals",
        "preserve_strengths_prevent_spread",
    ],
    "一般风险": [
        "watch_lowest_dimensions",
        "break_down_learning_and_routine_goals",
        "preserve_strengths_prevent_spread",
    ],
    "低风险": [
        "maintain_current_rhythm",
        "lightweight_reinforcement",
        "term_review_tracking",
    ],
}


def _coerce_float(value: object, default: float) -> float:
    try:
        coerced = float(value)
    except (TypeError, ValueError):
        return default
    if coerced != coerced:
        return default
    return coerced


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def _normalize_risk_level(risk_level: str) -> str:
    cleaned = str(risk_level).strip()
    return _RISK_LEVEL_ALIASES.get(cleaned, cleaned)


def _dimension_items_by_name(
    dimension_scores: Iterable[Mapping[str, object]],
) -> dict[str, Mapping[str, object]]:
    items: dict[str, Mapping[str, object]] = {}
    for item in dimension_scores:
        dimension = str(item.get("dimension", "")).strip()
        if not dimension:
            continue
        items[dimension] = item
    return items


def _dimension_score_map(dimension_scores: Iterable[Mapping[str, object]]) -> dict[str, float]:
    return {
        dimension: round(_clamp(_coerce_float(item.get("score"), 0.5), 0.0, 1.0), 2)
        for dimension, item in _dimension_items_by_name(dimension_scores).items()
    }


def _format_risk_label(risk_level: str) -> str:
    return _normalize_risk_level(risk_level) or "未知风险"


def _format_metric_value(value: object) -> str:
    if isinstance(value, float):
        return f"{value:.2f}".rstrip("0").rstrip(".")
    return str(value)


def _metric_summary(dimension_item: Mapping[str, object]) -> str:
    metrics = dimension_item.get("metrics")
    if not isinstance(metrics, Iterable):
        return "当前无可展示指标"

    metric_parts: list[str] = []
    for metric in metrics:
        if not isinstance(metric, Mapping):
            continue
        label = str(metric.get("label", "")).strip()
        if not label:
            continue
        metric_parts.append(f"{label} {_format_metric_value(metric.get('value'))}")
        if len(metric_parts) >= 2:
            break
    return "、".join(metric_parts) if metric_parts else "当前无可展示指标"


def _provenance_note(dimension_item: Mapping[str, object]) -> str | None:
    provenance = dimension_item.get("provenance")
    if not isinstance(provenance, Mapping):
        return None
    if bool(provenance.get("has_caveated_metrics")) or bool(provenance.get("has_deferred_metrics")):
        return "证据提示：当前维度包含 caveated/deferred 证据，解读时需保留口径限制。"
    return None


def _metric_value_by_name(
    dimension_item: Mapping[str, object] | None,
    metric_name: str,
) -> str:
    if not isinstance(dimension_item, Mapping):
        return "未提供"
    metrics = dimension_item.get("metrics")
    if not isinstance(metrics, Iterable):
        return "未提供"
    for metric in metrics:
        if not isinstance(metric, Mapping):
            continue
        if str(metric.get("metric", "")).strip() != metric_name:
            continue
        value = metric.get("value")
        if value is None:
            return "未提供"
        return _format_metric_value(value)
    return "未提供"


def _build_factor(
    *,
    dimension_name: str,
    feature_name: str,
    score_map: Mapping[str, float],
    items_by_name: Mapping[str, Mapping[str, object]],
    reverse: bool = False,
) -> dict[str, object]:
    dimension_item = items_by_name.get(dimension_name)
    if dimension_name not in score_map:
        return {
            "feature": feature_name,
            "feature_cn": dimension_name,
            "effect": "neutral",
            "importance": 0.0,
            "dimension_code": feature_name,
            "label": "",
            "explanation": "",
            "provenance": {},
        }

    score = score_map[dimension_name]
    if reverse:
        effect = "positive" if score >= 0.5 else "neutral"
        importance = round(max(score - 0.5, 0.0), 2)
    else:
        effect = "positive" if score < 0.5 else "negative"
        importance = round(0.75 - score * 0.5, 2)

    return {
        "feature": feature_name,
        "feature_cn": dimension_name,
        "effect": effect,
        "importance": importance,
        "dimension_code": str(dimension_item.get("dimension_code", feature_name))
        if isinstance(dimension_item, Mapping)
        else feature_name,
        "label": str(dimension_item.get("label", "")) if isinstance(dimension_item, Mapping) else "",
        "explanation": str(dimension_item.get("explanation", ""))
        if isinstance(dimension_item, Mapping)
        else "",
        "provenance": dict(dimension_item.get("provenance", {}))
        if isinstance(dimension_item, Mapping) and isinstance(dimension_item.get("provenance"), Mapping)
        else {},
    }


def build_top_factors(
    *,
    risk_level: str,
    group_segment: str,
    dimension_scores: Iterable[Mapping[str, object]],
) -> list[dict[str, object]]:
    del risk_level, group_segment
    items_by_name = _dimension_items_by_name(dimension_scores)
    score_map = _dimension_score_map(dimension_scores)
    order_map = {dimension_name: index for index, (dimension_name, _) in enumerate(_DIMENSION_TEMPLATES)}
    factors: list[dict[str, object]] = []

    for dimension_name, feature_name in sorted(
        _DIMENSION_TEMPLATES,
        key=lambda item: (item[0] not in score_map, score_map.get(item[0], 0.0), order_map[item[0]]),
    )[:3]:
        factors.append(
            _build_factor(
                dimension_name=dimension_name,
                feature_name=feature_name,
                score_map=score_map,
                items_by_name=items_by_name,
            )
        )

    return factors


def build_protective_factors(
    *,
    risk_level: str,
    group_segment: str,
    dimension_scores: Iterable[Mapping[str, object]],
) -> list[dict[str, object]]:
    del risk_level, group_segment
    items_by_name = _dimension_items_by_name(dimension_scores)
    score_map = _dimension_score_map(dimension_scores)
    order_map = {dimension_name: index for index, (dimension_name, _) in enumerate(_PROTECTIVE_DIMENSION_TEMPLATES)}
    factors: list[dict[str, object]] = []

    for dimension_name, feature_name in sorted(
        _PROTECTIVE_DIMENSION_TEMPLATES,
        key=lambda item: (
            -score_map.get(item[0], -1.0),
            item[0] not in score_map,
            order_map[item[0]],
        ),
    )[:3]:
        factor = _build_factor(
            dimension_name=dimension_name,
            feature_name=feature_name,
            score_map=score_map,
            items_by_name=items_by_name,
            reverse=True,
        )
        if factor["effect"] == "negative":
            factor["effect"] = "neutral"
            factor["importance"] = 0.0
        factors.append(factor)

    if len(factors) < 3:
        for dimension_name, feature_name in sorted(
            _PROTECTIVE_DIMENSION_TEMPLATES,
            key=lambda item: order_map[item[0]],
        ):
            if len(factors) == 3:
                break
            if any(factor["dimension_code"] == feature_name for factor in factors):
                continue
            factors.append(
                _build_factor(
                    dimension_name=dimension_name,
                    feature_name=feature_name,
                    score_map=score_map,
                    items_by_name=items_by_name,
                    reverse=True,
                )
            )

    return factors[:3]


def _build_priority_interventions(risk_level: str) -> list[dict[str, object]]:
    normalized_risk_level = _format_risk_label(risk_level)
    advice_texts = list(_INTERVENTION_TEMPLATES.get(normalized_risk_level, _INTERVENTION_TEMPLATES["一般风险"]))
    advice_keys = list(_INTERVENTION_KEYS.get(normalized_risk_level, _INTERVENTION_KEYS["一般风险"]))
    return [
        {"key": advice_keys[index], "priority": index + 1, "text": text}
        for index, text in enumerate(advice_texts)
    ]


def _build_report_text(
    *,
    base_risk_score: float,
    risk_adjustment_score: float,
    adjusted_risk_score: float,
    risk_delta: float,
    risk_change_direction: str,
    risk_level: str,
    group_segment: str,
    top_risk_factors: list[dict[str, object]],
    top_protective_factors: list[dict[str, object]],
    dimension_scores: Iterable[Mapping[str, object]],
    base_risk_explanation: str,
    behavior_adjustment_explanation: str,
    risk_change_explanation: str,
    intervention_plan: str,
) -> str:
    items_by_name = _dimension_items_by_name(dimension_scores)
    risk_label = _format_risk_label(risk_level)
    lines = [
        "## 学生群体画像",
        f"该学生当前属于「{group_segment}」，当前风险等级为 {risk_label}。",
        f"基础风险分 {base_risk_score:.2f}，行为调整 {risk_adjustment_score:+.2f}，最终风险分 {adjusted_risk_score:.2f}。",
        f"风险变化 {risk_delta:+.2f}，方向为 {risk_change_direction}。",
        "",
        "## 基础风险盘",
        base_risk_explanation,
        "",
        "## 行为放大与保护因素",
        behavior_adjustment_explanation,
        "",
        "## 风险变化",
        risk_change_explanation,
        "",
        "## 核心风险指标解读",
    ]

    for index, factor in enumerate(top_risk_factors, start=1):
        dimension_name = str(factor["feature_cn"])
        dimension_item = items_by_name.get(dimension_name)
        if dimension_item is None:
            suffix = "暂无有效数据，建议继续补充观察。"
            line = f"{index}. **{dimension_name}**: {suffix}"
        else:
            label = str(dimension_item.get("label", "")).strip()
            explanation = str(dimension_item.get("explanation", "")).strip()
            score = round(_clamp(_coerce_float(dimension_item.get("score"), 0.5), 0.0, 1.0), 2)
            level = _DIMENSION_LEVEL_LABELS.get(
                str(dimension_item.get("level", "")).strip(),
                str(dimension_item.get("level", "")).strip() or "未知",
            )
            metric_summary = _metric_summary(dimension_item)
            provenance_note = _provenance_note(dimension_item)
            heading = f"**{dimension_name}**"
            if label:
                heading = f"{heading}（{label}）"
            line_parts = [
                f"{index}. {heading}: 当前维度得分 {score:.2f}，水平 {level}。",
                f"   指标：{metric_summary}",
                f"   解读：{explanation or '暂无有效数据，建议继续补充观察。'}",
            ]
            if provenance_note:
                line_parts.append(f"   {provenance_note}")
            line = "\n".join(line_parts)
        lines.append(line)

    if top_protective_factors:
        lines.extend(["", "## 保护性因素"])
        for index, factor in enumerate(top_protective_factors, start=1):
            dimension_name = str(factor["feature_cn"])
            dimension_item = items_by_name.get(dimension_name)
            if dimension_item is None:
                lines.append(f"{index}. **{dimension_name}**: 暂无有效数据。")
                continue
            label = str(dimension_item.get("label", "")).strip()
            score = round(_clamp(_coerce_float(dimension_item.get("score"), 0.5), 0.0, 1.0), 2)
            heading = f"**{dimension_name}**"
            if label:
                heading = f"{heading}（{label}）"
            lines.append(f"{index}. {heading}: 当前维度得分 {score:.2f}，可作为稳定支撑。")

    lines.extend(["", "## 干预计划", intervention_plan])

    return "\n".join(lines)


def build_report_payload(
    *,
    base_risk_score: float,
    risk_adjustment_score: float,
    adjusted_risk_score: float,
    risk_delta: float,
    risk_change_direction: str,
    risk_level: str,
    group_segment: str,
    dimension_scores: Iterable[Mapping[str, object]],
) -> dict[str, object]:
    dimension_scores = list(dimension_scores)
    risk_level = _format_risk_label(risk_level)
    dimension_items_by_name = _dimension_items_by_name(dimension_scores)
    top_risk_factors = build_top_factors(
        risk_level=risk_level,
        group_segment=group_segment,
        dimension_scores=dimension_scores,
    )
    top_protective_factors = build_protective_factors(
        risk_level=risk_level,
        group_segment=group_segment,
        dimension_scores=dimension_scores,
    )
    priority_interventions = _build_priority_interventions(risk_level)
    intervention_plan = "\n".join(
        [f"{risk_level}干预计划："]
        + [f"{item['priority']}. {item['text']}" for item in priority_interventions]
    )
    intervention_priority = _RISK_LEVEL_PRIORITY.get(risk_level, 3)
    academic_item = dimension_items_by_name.get("学业基础表现")
    gpa_value = _metric_value_by_name(academic_item, "term_gpa")
    failed_count = _metric_value_by_name(academic_item, "failed_course_count")
    borderline_count = _metric_value_by_name(academic_item, "borderline_course_count")
    failed_ratio = _metric_value_by_name(academic_item, "failed_course_ratio")
    academic_signal_text = (
        f"学期GPA {gpa_value}、挂科门数 {failed_count}、边缘课程数 {borderline_count}、挂科占比 {failed_ratio}"
    )
    risk_driver_text = "、".join(
        str(item["feature_cn"])
        for item in top_risk_factors
        if str(item.get("feature_cn", "")).strip()
    )
    protective_signal_text = "、".join(
        str(item["feature_cn"])
        for item in top_protective_factors
        if str(item.get("feature_cn", "")).strip()
    )
    base_risk_explanation = (
        f"基础风险盘由学业结果形成，当前参考 {academic_signal_text}。"
        f" 基础风险分 {base_risk_score:.2f}，属于 {risk_level}。"
        f" 这里不混入作息、在线学习或体质等行为修正。"
    )
    behavior_adjustment_explanation = (
        f"行为调整为 {risk_adjustment_score:+.2f}，将基础风险修正到 {adjusted_risk_score:.2f}。"
        f" 主要放大因素是 {risk_driver_text}；"
        f" 保护性因素是 {protective_signal_text}。"
    )
    risk_change_explanation = (
        f"风险变化为 {risk_delta:+.2f}，方向为 {risk_change_direction}。"
        f" 这表示当前学期相较上一学期的风险态势正在{'上升' if risk_change_direction == 'rising' else '下降' if risk_change_direction == 'falling' else '保持稳定'}。"
        f" 变化更可能和 {risk_driver_text} 的波动有关，并受到 {protective_signal_text} 的支撑。"
    )
    report_text = _build_report_text(
        base_risk_score=base_risk_score,
        risk_adjustment_score=risk_adjustment_score,
        adjusted_risk_score=adjusted_risk_score,
        risk_delta=risk_delta,
        risk_change_direction=risk_change_direction,
        risk_level=risk_level,
        group_segment=group_segment,
        top_risk_factors=top_risk_factors,
        top_protective_factors=top_protective_factors,
        dimension_scores=dimension_scores,
        base_risk_explanation=base_risk_explanation,
        behavior_adjustment_explanation=behavior_adjustment_explanation,
        risk_change_explanation=risk_change_explanation,
        intervention_plan=intervention_plan,
    )
    return {
        "version": "v1_calibrated_report",
        "risk_level": risk_level,
        "base_risk_score": base_risk_score,
        "risk_adjustment_score": risk_adjustment_score,
        "adjusted_risk_score": adjusted_risk_score,
        "risk_delta": risk_delta,
        "risk_change_direction": risk_change_direction,
        "intervention_priority": intervention_priority,
        "top_risk_factors": top_risk_factors,
        "top_protective_factors": top_protective_factors,
        "top_factors": top_risk_factors,
        "priority_interventions": priority_interventions,
        "intervention_advice": [str(item["text"]) for item in priority_interventions],
        "intervention_advice_items": priority_interventions,
        "intervention_plan": intervention_plan,
        "base_risk_explanation": base_risk_explanation,
        "behavior_adjustment_explanation": behavior_adjustment_explanation,
        "risk_change_explanation": risk_change_explanation,
        "report_text": report_text,
    }
