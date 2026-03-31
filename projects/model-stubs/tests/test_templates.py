from collections.abc import Iterator

from student_behavior_model_stubs.templates import build_report_payload
from student_behavior_model_stubs.templates import build_top_factors


def test_build_top_factors_matches_api_contract_shape() -> None:
    dimension_scores = [
        {"dimension": "学业基础表现", "score": 0.18},
        {"dimension": "课堂学习投入", "score": 0.32},
        {"dimension": "学习行为活跃度", "score": 0.57},
        {"dimension": "生活规律与资源使用", "score": 0.81},
    ]

    assert build_top_factors(
        risk_level="high",
        group_segment="作息失衡风险组",
        dimension_scores=dimension_scores,
    ) == [
        {
            "feature": "academic_base_score",
            "feature_cn": "学业基础表现",
            "effect": "positive",
            "importance": 0.66,
        },
        {
            "feature": "class_engagement",
            "feature_cn": "课堂学习投入",
            "effect": "positive",
            "importance": 0.59,
        },
        {
            "feature": "behavior_activity",
            "feature_cn": "学习行为活跃度",
            "effect": "negative",
            "importance": 0.47,
        },
    ]


def test_build_report_payload_returns_readable_stub_content() -> None:
    dimension_scores = [
        {"dimension": "学业基础表现", "score": 0.18},
        {"dimension": "课堂学习投入", "score": 0.32},
        {"dimension": "学习行为活跃度", "score": 0.57},
        {"dimension": "生活规律与资源使用", "score": 0.81},
    ]

    assert build_report_payload(
        risk_level="high",
        group_segment="作息失衡风险组",
        dimension_scores=dimension_scores,
    ) == {
        "top_factors": [
            {
                "feature": "academic_base_score",
                "feature_cn": "学业基础表现",
                "effect": "positive",
                "importance": 0.66,
            },
            {
                "feature": "class_engagement",
                "feature_cn": "课堂学习投入",
                "effect": "positive",
                "importance": 0.59,
            },
            {
                "feature": "behavior_activity",
                "feature_cn": "学习行为活跃度",
                "effect": "negative",
                "importance": 0.47,
            },
        ],
        "intervention_advice": [
            "优先安排一次一对一沟通，确认深夜在线和课堂投入偏低的原因。",
            "建议将本周学习目标拆成可执行清单，并按天跟进完成情况。",
            "同步提醒宿舍作息和电子设备使用边界，先把晚间行为稳定下来。",
        ],
        "report_text": (
            "## 学生群体画像\n"
            "该学生当前属于「作息失衡风险组」，当前风险等级为 高风险。\n\n"
            "## 核心风险指标解读\n"
            "1. **学业基础表现**: 当前维度得分为 0.18，属于需要优先关注的弱项。\n"
            "2. **课堂学习投入**: 当前维度得分为 0.32，属于需要优先关注的弱项。\n"
            "3. **学习行为活跃度**: 当前维度得分为 0.57，保持观察即可。\n\n"
            "## 建设性改进建议\n"
            "1. 优先安排一次一对一沟通，确认深夜在线和课堂投入偏低的原因。\n"
            "2. 建议将本周学习目标拆成可执行清单，并按天跟进完成情况。\n"
            "3. 同步提醒宿舍作息和电子设备使用边界，先把晚间行为稳定下来。"
        ),
    }


def test_build_report_payload_is_deterministic() -> None:
    dimension_scores = [
        {"dimension": "课堂学习投入", "score": 0.24},
    ]

    payload_one = build_report_payload(
        risk_level="medium",
        group_segment="课堂参与薄弱组",
        dimension_scores=dimension_scores,
    )
    payload_two = build_report_payload(
        risk_level="medium",
        group_segment="课堂参与薄弱组",
        dimension_scores=dimension_scores,
    )

    assert payload_one == payload_two
    assert payload_one["report_text"].strip() != ""
    assert payload_one["intervention_advice"]


def test_build_report_payload_handles_one_shot_dimension_scores() -> None:
    def score_rows() -> Iterator[dict[str, object]]:
        yield {"dimension": "学业基础表现", "score": 0.18}
        yield {"dimension": "课堂学习投入", "score": 0.32}
        yield {"dimension": "学习行为活跃度", "score": 0.57}
        yield {"dimension": "生活规律与资源使用", "score": 0.81}

    payload = build_report_payload(
        risk_level="high",
        group_segment="作息失衡风险组",
        dimension_scores=score_rows(),
    )

    assert payload["top_factors"] == [
        {
            "feature": "academic_base_score",
            "feature_cn": "学业基础表现",
            "effect": "positive",
            "importance": 0.66,
        },
        {
            "feature": "class_engagement",
            "feature_cn": "课堂学习投入",
            "effect": "positive",
            "importance": 0.59,
        },
        {
            "feature": "behavior_activity",
            "feature_cn": "学习行为活跃度",
            "effect": "negative",
            "importance": 0.47,
        },
    ]
    assert "高风险" in payload["report_text"]


def test_build_report_payload_handles_sparse_dimension_scores() -> None:
    payload = build_report_payload(
        risk_level="low",
        group_segment="学习投入稳定组",
        dimension_scores=[],
    )

    assert len(payload["top_factors"]) == 3
    assert payload["top_factors"] == [
        {
            "feature": "academic_base_score",
            "feature_cn": "学业基础表现",
            "effect": "neutral",
            "importance": 0.0,
        },
        {
            "feature": "class_engagement",
            "feature_cn": "课堂学习投入",
            "effect": "neutral",
            "importance": 0.0,
        },
        {
            "feature": "behavior_activity",
            "feature_cn": "学习行为活跃度",
            "effect": "neutral",
            "importance": 0.0,
        },
    ]
    assert payload["report_text"].strip() != ""
    assert "学习投入稳定组" in payload["report_text"]
    assert "低风险" in payload["report_text"]
    assert "暂无有效数据" in payload["report_text"]
    assert "low" not in payload["report_text"]
