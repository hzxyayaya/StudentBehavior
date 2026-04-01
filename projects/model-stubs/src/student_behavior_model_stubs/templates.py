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

_RISK_LABELS = {
    "high": "高风险",
    "medium": "中风险",
    "low": "低风险",
}

_RISK_ADVICE = {
    "high": [
        "优先围绕学业基础与课堂投入做一次针对性复盘，先稳定核心学习面。",
        "对网络作息和早晚行为设置明确边界，并连续跟踪一周变化。",
        "保留已经稳定的体质与荣誉优势，把资源投入到最弱的三项维度上。",
    ],
    "medium": [
        "先锁定最低的三项维度，按周观察是否有连续改善。",
        "把课堂、在线学习和作息管理拆成可执行的小目标。",
        "保持已有优势项稳定，避免新的波动扩散到学业表现。",
    ],
    "low": [
        "维持当前稳定节奏，继续巩固高分维度的优势表现。",
        "围绕较弱维度做轻量补强，避免阶段性回落。",
        "按学期复盘一次八维画像，持续跟踪结构性变化。",
    ],
}

_RISK_ADVICE_KEYS = {
    "high": [
        "stabilize_core_learning",
        "set_routine_boundaries",
        "protect_strengths_focus_weakest",
    ],
    "medium": [
        "watch_lowest_dimensions",
        "break_down_learning_and_routine_goals",
        "preserve_strengths_prevent_spread",
    ],
    "low": [
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
    return _RISK_LABELS.get(risk_level, "未知风险")


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


def build_top_factors(
    *,
    risk_level: str,
    group_segment: str,
    dimension_scores: Iterable[Mapping[str, object]],
) -> list[dict[str, object]]:
    del risk_level, group_segment
    items_by_name = _dimension_items_by_name(dimension_scores)
    score_map = _dimension_score_map(dimension_scores)
    factors: list[dict[str, object]] = []

    for dimension_name, feature_name in sorted(
        _DIMENSION_TEMPLATES,
        key=lambda item: (item[0] not in score_map, score_map.get(item[0], 0.0)),
    )[:3]:
        dimension_item = items_by_name.get(dimension_name)
        if dimension_name not in score_map:
            factors.append(
                {
                    "feature": feature_name,
                    "feature_cn": dimension_name,
                    "effect": "neutral",
                    "importance": 0.0,
                    "dimension_code": feature_name,
                    "label": "",
                    "explanation": "",
                    "provenance": {},
                }
            )
            continue

        score = score_map[dimension_name]
        factors.append(
            {
                "feature": feature_name,
                "feature_cn": dimension_name,
                "effect": "positive" if score < 0.5 else "negative",
                "importance": round(0.75 - score * 0.5, 2),
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
        )

    return factors


def _build_intervention_advice_items(risk_level: str) -> list[dict[str, object]]:
    advice_texts = list(_RISK_ADVICE.get(risk_level, _RISK_ADVICE["medium"]))
    advice_keys = list(_RISK_ADVICE_KEYS.get(risk_level, _RISK_ADVICE_KEYS["medium"]))
    return [
        {"key": advice_keys[index], "priority": index + 1, "text": text}
        for index, text in enumerate(advice_texts)
    ]


def _build_report_text(
    *,
    risk_level: str,
    group_segment: str,
    top_factors: list[dict[str, object]],
    dimension_scores: Iterable[Mapping[str, object]],
    intervention_advice: list[str],
) -> str:
    items_by_name = _dimension_items_by_name(dimension_scores)
    risk_label = _format_risk_label(risk_level)
    lines = [
        "## 学生群体画像",
        f"该学生当前属于「{group_segment}」，当前风险等级为 {risk_label}。",
        "",
        "## 核心风险指标解读",
    ]

    for index, factor in enumerate(top_factors, start=1):
        dimension_name = str(factor["feature_cn"])
        dimension_item = items_by_name.get(dimension_name)
        if dimension_item is None:
            suffix = "暂无有效数据，建议继续补充观察。"
            line = f"{index}. **{dimension_name}**: {suffix}"
        else:
            label = str(dimension_item.get("label", "")).strip()
            explanation = str(dimension_item.get("explanation", "")).strip()
            score = round(_clamp(_coerce_float(dimension_item.get("score"), 0.5), 0.0, 1.0), 2)
            level = str(dimension_item.get("level", "")).strip() or "unknown"
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

    lines.extend(["", "## 建设性改进建议"])
    for index, advice in enumerate(intervention_advice, start=1):
        lines.append(f"{index}. {advice}")

    return "\n".join(lines)


def build_report_payload(
    *,
    risk_level: str,
    group_segment: str,
    dimension_scores: Iterable[Mapping[str, object]],
) -> dict[str, object]:
    dimension_scores = list(dimension_scores)
    top_factors = build_top_factors(
        risk_level=risk_level,
        group_segment=group_segment,
        dimension_scores=dimension_scores,
    )
    intervention_advice_items = _build_intervention_advice_items(risk_level)
    intervention_advice = [str(item["text"]) for item in intervention_advice_items]
    report_text = _build_report_text(
        risk_level=risk_level,
        group_segment=group_segment,
        top_factors=top_factors,
        dimension_scores=dimension_scores,
        intervention_advice=intervention_advice,
    )
    return {
        "version": "v1_calibrated_report",
        "top_factors": top_factors,
        "intervention_advice": intervention_advice,
        "intervention_advice_items": intervention_advice_items,
        "report_text": report_text,
    }
