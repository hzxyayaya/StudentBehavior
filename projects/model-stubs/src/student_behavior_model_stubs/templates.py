from collections.abc import Iterable, Mapping


_DIMENSION_TEMPLATES = [
    ("学业基础表现", "academic_base_score"),
    ("课堂学习投入", "class_engagement"),
    ("学习行为活跃度", "behavior_activity"),
    ("生活规律与资源使用", "routine_resource_use"),
]

_RISK_LABELS = {
    "high": "高风险",
    "medium": "中风险",
    "low": "低风险",
}

_RISK_ADVICE = {
    "high": [
        "优先安排一次一对一沟通，确认深夜在线和课堂投入偏低的原因。",
        "建议将本周学习目标拆成可执行清单，并按天跟进完成情况。",
        "同步提醒宿舍作息和电子设备使用边界，先把晚间行为稳定下来。",
    ],
    "medium": [
        "建议先聚焦课堂参与和作息稳定，按周观察变化趋势。",
        "把学习任务拆成小步执行，并保留固定的反馈节奏。",
        "继续维持已有的正向行为，同时减少波动较大的环节。",
    ],
    "low": [
        "保持当前的良好节奏，继续巩固稳定的学习与生活习惯。",
        "围绕优势维度做轻量复盘，避免出现新的波动。",
        "保持常规跟踪即可，重点关注是否出现阶段性变化。",
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


def _dimension_score_map(dimension_scores: Iterable[Mapping[str, object]]) -> dict[str, float]:
    scores: dict[str, float] = {}
    for item in dimension_scores:
        dimension = str(item.get("dimension", "")).strip()
        if not dimension:
            continue
        score = _clamp(_coerce_float(item.get("score"), 0.5), 0.0, 1.0)
        scores[dimension] = round(score, 2)
    return scores


def _format_risk_label(risk_level: str) -> str:
    return _RISK_LABELS.get(risk_level, "未知风险")


def build_top_factors(
    *,
    risk_level: str,
    quadrant_label: str,
    dimension_scores: Iterable[Mapping[str, object]],
) -> list[dict[str, object]]:
    del risk_level, quadrant_label

    score_map = _dimension_score_map(dimension_scores)
    factors: list[dict[str, object]] = []

    for dimension_name, feature_name in sorted(
        _DIMENSION_TEMPLATES,
        key=lambda item: (item[0] not in score_map, score_map.get(item[0], 0.0)),
    )[:3]:
        if dimension_name not in score_map:
            factors.append(
                {
                    "feature": feature_name,
                    "feature_cn": dimension_name,
                    "effect": "neutral",
                    "importance": 0.0,
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
            }
        )

    return factors


def _build_report_text(
    *,
    risk_level: str,
    quadrant_label: str,
    top_factors: list[dict[str, object]],
    dimension_scores: Iterable[Mapping[str, object]],
    intervention_advice: list[str],
) -> str:
    score_map = _dimension_score_map(dimension_scores)
    risk_label = _format_risk_label(risk_level)
    lines = [
        "## 学生群体画像",
        f"该学生被系统归类为「{quadrant_label}」群体，当前风险等级为 {risk_label}。",
        "",
        "## 核心风险指标解读",
    ]

    for index, factor in enumerate(top_factors, start=1):
        dimension_name = str(factor["feature_cn"])
        score = score_map.get(dimension_name)
        if score is None:
            suffix = "暂无有效数据，建议继续补充观察。"
            score_text = "暂无"
        elif score < 0.5:
            suffix = "属于需要优先关注的弱项。"
            score_text = f"{score:.2f}"
        else:
            suffix = "保持观察即可。"
            score_text = f"{score:.2f}"
        lines.append(f"{index}. **{dimension_name}**: 当前维度得分为 {score_text}，{suffix}")

    lines.extend(
        [
            "",
            "## 建设性改进建议",
        ]
    )
    for index, advice in enumerate(intervention_advice, start=1):
        lines.append(f"{index}. {advice}")

    return "\n".join(lines)


def build_report_payload(
    *,
    risk_level: str,
    quadrant_label: str,
    dimension_scores: Iterable[Mapping[str, object]],
) -> dict[str, object]:
    dimension_scores = list(dimension_scores)
    top_factors = build_top_factors(
        risk_level=risk_level,
        quadrant_label=quadrant_label,
        dimension_scores=dimension_scores,
    )
    intervention_advice = list(_RISK_ADVICE.get(risk_level, _RISK_ADVICE["medium"]))
    report_text = _build_report_text(
        risk_level=risk_level,
        quadrant_label=quadrant_label,
        top_factors=top_factors,
        dimension_scores=dimension_scores,
        intervention_advice=intervention_advice,
    )
    return {
        "top_factors": top_factors,
        "intervention_advice": intervention_advice,
        "report_text": report_text,
    }
