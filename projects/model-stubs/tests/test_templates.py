from collections.abc import Iterator

from student_behavior_model_stubs.templates import build_report_payload
from student_behavior_model_stubs.templates import build_top_factors


def _dimension_scores() -> list[dict[str, object]]:
    return [
        {
            "dimension": "学业基础表现",
            "dimension_code": "academic_base",
            "score": 0.18,
            "level": "low",
            "label": "学业基础预警",
            "metrics": [{"metric": "term_gpa", "label": "学期GPA", "value": 2.1}],
            "explanation": "学业基础表现处于学业基础预警，主要依据是学期GPA 2.1。",
            "provenance": {"has_caveated_metrics": False},
        },
        {
            "dimension": "课堂学习投入",
            "dimension_code": "class_engagement",
            "score": 0.32,
            "level": "low",
            "label": "课堂投入薄弱",
            "metrics": [{"metric": "attendance_rate", "label": "出勤率", "value": 0.76}],
            "explanation": "课堂学习投入处于课堂投入薄弱，主要依据是出勤率 0.76。",
            "provenance": {"has_caveated_metrics": True},
        },
        {
            "dimension": "在线学习积极性",
            "dimension_code": "online_activeness",
            "score": 0.41,
            "level": "low",
            "label": "在线学习偏弱",
            "metrics": [{"metric": "video_completion_rate", "label": "视频完成率", "value": 0.52}],
            "explanation": "在线学习积极性处于在线学习偏弱，主要依据是视频完成率 0.52。",
            "provenance": {"has_caveated_metrics": False},
        },
        {
            "dimension": "图书馆沉浸度",
            "dimension_code": "library_immersion",
            "score": 0.57,
            "level": "medium",
            "label": "图书馆投入一般",
            "metrics": [{"metric": "weekly_library_visit_avg", "label": "周均进馆次数", "value": 1.4}],
            "explanation": "图书馆沉浸度处于图书馆投入一般，主要依据是周均进馆次数 1.4。",
            "provenance": {"has_caveated_metrics": False},
        },
        {
            "dimension": "网络作息自律指数",
            "dimension_code": "network_habits",
            "score": 0.21,
            "level": "low",
            "label": "网络作息失衡",
            "metrics": [{"metric": "monthly_online_duration_avg", "label": "月均上网时长", "value": 42}],
            "explanation": "网络作息自律指数处于网络作息失衡，主要依据是月均上网时长 42。 说明：不声称深夜指标，不使用 0:00-6:00 明细；仅允许聚合上网强度。",
            "provenance": {"has_caveated_metrics": True},
        },
        {
            "dimension": "早晚生活作息规律",
            "dimension_code": "daily_routine_boundary",
            "score": 0.26,
            "level": "low",
            "label": "作息边界失衡",
            "metrics": [{"metric": "late_return_ratio", "label": "晚归占比", "value": 0.28}],
            "explanation": "早晚生活作息规律处于作息边界失衡，主要依据是晚归占比 0.28。",
            "provenance": {"has_caveated_metrics": False},
        },
        {
            "dimension": "体质及运动状况",
            "dimension_code": "physical_resilience",
            "score": 0.81,
            "level": "high",
            "label": "体能状态良好",
            "metrics": [{"metric": "physical_test_avg_score", "label": "体测均分", "value": 88}],
            "explanation": "体质及运动状况处于体能状态良好，主要依据是体测均分 88。",
            "provenance": {"has_caveated_metrics": False},
        },
        {
            "dimension": "综合荣誉与异动预警",
            "dimension_code": "appraisal_status_alert",
            "score": 0.74,
            "level": "medium",
            "label": "综合表现波动",
            "metrics": [{"metric": "status_change_count", "label": "异动次数", "value": 1}],
            "explanation": "综合荣誉与异动预警处于综合表现波动，主要依据是异动次数 1。",
            "provenance": {"has_caveated_metrics": False},
        },
    ]


def test_build_top_factors_matches_api_contract_shape() -> None:
    factors = build_top_factors(
        risk_level="high",
        group_segment="作息失衡风险组",
        dimension_scores=_dimension_scores(),
    )

    assert [factor["feature"] for factor in factors] == [
        "academic_base",
        "network_habits",
        "daily_routine_boundary",
    ]
    assert {"feature", "feature_cn", "effect", "importance", "dimension_code", "label", "explanation", "provenance"} <= set(factors[0])
    assert factors[0]["dimension_code"] == "academic_base"
    assert factors[0]["label"] == "学业基础预警"
    assert "学期GPA 2.1" in factors[0]["explanation"]
    assert factors[1]["dimension_code"] == "network_habits"
    assert factors[1]["provenance"] == {"has_caveated_metrics": True}


def test_build_report_payload_returns_readable_stub_content() -> None:
    payload = build_report_payload(
        base_risk_score=86.0,
        risk_adjustment_score=-12.0,
        adjusted_risk_score=74.0,
        risk_delta=8.5,
        risk_change_direction="rising",
        risk_level="较高风险",
        group_segment="作息失衡风险组",
        dimension_scores=_dimension_scores(),
    )

    assert payload["version"] == "v1_calibrated_report"
    assert payload["report_source"] == "template"
    assert payload["prompt_version"] == "template-report-v1"
    assert payload["report_generation"] == {
        "source": "template",
        "prompt_version": "template-report-v1",
        "fallback_reason": None,
        "provider": None,
        "model": None,
        "requested_source": "template",
        "requested_prompt_version": "template-report-v1",
    }
    assert [factor["dimension_code"] for factor in payload["top_risk_factors"]] == [
        "academic_base",
        "network_habits",
        "daily_routine_boundary",
    ]
    assert [factor["dimension_code"] for factor in payload["top_protective_factors"]] == [
        "physical_resilience",
        "appraisal_status_alert",
        "library_immersion",
    ]
    assert all(factor["effect"] != "negative" for factor in payload["top_protective_factors"])
    assert payload["intervention_priority"] == 2
    assert "学期GPA" in payload["base_risk_explanation"]
    assert "行为调整" in payload["behavior_adjustment_explanation"]
    assert "风险变化" in payload["risk_change_explanation"]
    assert any(token in payload["risk_change_explanation"] for token in ["挂科", "课堂", "作息", "在线学习", "体质"])
    assert "较高风险" in payload["intervention_plan"]
    assert payload["top_risk_factors"][0]["feature_cn"] in payload["intervention_plan"]
    assert "作息失衡风险组" in payload["report_text"]
    assert "较高风险" in payload["report_text"]
    assert "证据提示：当前维度包含 caveated/deferred 证据" in payload["report_text"]


def test_build_report_payload_is_deterministic() -> None:
    payload_one = build_report_payload(
        base_risk_score=51.0,
        risk_adjustment_score=0.0,
        adjusted_risk_score=51.0,
        risk_delta=0.0,
        risk_change_direction="steady",
        risk_level="一般风险",
        group_segment="课堂参与薄弱组",
        dimension_scores=[{"dimension": "课堂学习投入", "score": 0.24}],
    )
    payload_two = build_report_payload(
        base_risk_score=51.0,
        risk_adjustment_score=0.0,
        adjusted_risk_score=51.0,
        risk_delta=0.0,
        risk_change_direction="steady",
        risk_level="一般风险",
        group_segment="课堂参与薄弱组",
        dimension_scores=[{"dimension": "课堂学习投入", "score": 0.24}],
    )

    assert payload_one == payload_two
    assert payload_one["report_text"].strip() != ""
    assert payload_one["priority_interventions"]


def test_build_report_payload_handles_one_shot_dimension_scores() -> None:
    def score_rows() -> Iterator[dict[str, object]]:
        yield from _dimension_scores()

    payload = build_report_payload(
        base_risk_score=88.0,
        risk_adjustment_score=-6.0,
        adjusted_risk_score=82.0,
        risk_delta=-3.5,
        risk_change_direction="falling",
        risk_level="高风险",
        group_segment="作息失衡风险组",
        dimension_scores=score_rows(),
    )

    assert [factor["dimension_code"] for factor in payload["top_risk_factors"]] == [
        "academic_base",
        "network_habits",
        "daily_routine_boundary",
    ]
    assert "高风险" in payload["report_text"]
    assert "学业基础预警" in payload["report_text"]
    assert "月均上网时长 42" in payload["report_text"]
    assert "证据提示：当前维度包含 caveated/deferred 证据" in payload["report_text"]


def test_build_report_payload_handles_sparse_dimension_scores() -> None:
    payload = build_report_payload(
        base_risk_score=16.0,
        risk_adjustment_score=0.0,
        adjusted_risk_score=16.0,
        risk_delta=0.0,
        risk_change_direction="steady",
        risk_level="低风险",
        group_segment="学习投入稳定组",
        dimension_scores=[],
    )

    assert len(payload["top_risk_factors"]) == 3
    assert [factor["dimension_code"] for factor in payload["top_risk_factors"]] == [
        "academic_base",
        "class_engagement",
        "online_activeness",
    ]
    assert len(payload["top_protective_factors"]) == 3
    assert all(factor["effect"] == "neutral" for factor in payload["top_risk_factors"])
    assert all(factor["importance"] == 0.0 for factor in payload["top_risk_factors"])
    assert all(factor["label"] == "" for factor in payload["top_risk_factors"])
    assert all(factor["explanation"] == "" for factor in payload["top_risk_factors"])
    assert all(factor["provenance"] == {} for factor in payload["top_risk_factors"])
    assert payload["report_text"].strip() != ""
    assert "学习投入稳定组" in payload["report_text"]
    assert "低风险" in payload["report_text"]
    assert "暂无可核对指标" in payload["report_text"]
    assert "low" not in payload["report_text"]
    assert "仅作中性参考" in payload["report_text"]
    assert "可作为稳定支撑" not in payload["report_text"]
    assert payload["version"] == "v1_calibrated_report"
    assert len(payload["priority_interventions"]) == 3


def test_build_report_payload_falls_back_when_academic_metrics_are_missing() -> None:
    payload = build_report_payload(
        base_risk_score=16.0,
        risk_adjustment_score=0.0,
        adjusted_risk_score=16.0,
        risk_delta=0.0,
        risk_change_direction="steady",
        risk_level="低风险",
        group_segment="学习投入稳定组",
        dimension_scores=[
            {
                "dimension": "学业基础表现",
                "dimension_code": "academic_base",
                "score": 0.2,
                "level": "low",
                "label": "学业基础预警",
                "metrics": [],
                "explanation": "学业基础表现处于学业基础预警。",
                "provenance": {"has_caveated_metrics": False, "has_deferred_metrics": False},
            }
        ],
    )

    assert payload["base_risk_explanation"] == "学业结果指标暂缺，基础风险解释仅供参考。"
    assert "学期GPA 未提供" not in payload["base_risk_explanation"]
    assert "基础风险分" not in payload["base_risk_explanation"]
    assert "仅供参考" in payload["base_risk_explanation"]


def test_build_top_factors_prefers_calibrated_explanations_over_plain_scores() -> None:
    payload = build_report_payload(
        base_risk_score=86.0,
        risk_adjustment_score=-12.0,
        adjusted_risk_score=74.0,
        risk_delta=8.5,
        risk_change_direction="rising",
        risk_level="较高风险",
        group_segment="作息失衡风险组",
        dimension_scores=_dimension_scores(),
    )

    assert payload["top_risk_factors"][1]["feature"] == "network_habits"
    assert "网络作息失衡" in payload["report_text"]
    assert "不声称深夜指标" in payload["report_text"]


def test_build_top_factors_pushes_unavailable_dimensions_behind_available_ones() -> None:
    scores = _dimension_scores()
    scores[1] = {
        **scores[1],
        "score": 0.0,
        "label": "当前学期无有效数据",
        "metrics": [],
        "explanation": "课堂学习投入当前学期无有效源表指标，暂不做该维度判定。",
        "provenance": {"is_unavailable": True, "unavailable_reason": "no_metrics"},
    }

    factors = build_top_factors(
        risk_level="high",
        group_segment="作息失衡风险组",
        dimension_scores=scores,
    )

    assert [factor["dimension_code"] for factor in factors] == [
        "academic_base",
        "network_habits",
        "daily_routine_boundary",
    ]
    assert all(factor["dimension_code"] != "class_engagement" for factor in factors)


def test_build_report_payload_structurally_uses_metrics_and_provenance() -> None:
    scores = _dimension_scores()
    scores[0] = {
        **scores[0],
        "explanation": "占位说明，不应成为唯一信息来源。",
    }
    scores[4] = {
        **scores[4],
        "provenance": {
            "has_caveated_metrics": True,
            "has_deferred_metrics": True,
            "threshold_strategies": ["hybrid"],
        },
    }

    payload = build_report_payload(
        base_risk_score=88.0,
        risk_adjustment_score=-12.0,
        adjusted_risk_score=76.0,
        risk_delta=6.0,
        risk_change_direction="rising",
        risk_level="较高风险",
        group_segment="作息失衡风险组",
        dimension_scores=scores,
    )

    assert "指标：学期GPA 2.1" in payload["report_text"]
    assert "当前维度得分 0.18，水平 低。" in payload["report_text"]
    assert "证据提示：当前维度包含 caveated/deferred 证据，解读时需保留口径限制。" in payload["report_text"]
    assert payload["top_risk_factors"][0]["dimension_code"] == "academic_base"
    assert payload["top_risk_factors"][0]["label"] == "学业基础预警"
    assert payload["top_risk_factors"][0]["explanation"] == "占位说明，不应成为唯一信息来源。"
    network_factor = next(
        factor for factor in payload["top_risk_factors"] if factor["dimension_code"] == "network_habits"
    )
    assert network_factor["provenance"]["has_deferred_metrics"] is True
    assert [item["priority"] for item in payload["priority_interventions"]] == [1, 2, 3]
