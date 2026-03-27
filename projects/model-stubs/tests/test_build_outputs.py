from datetime import datetime

import pandas as pd

from student_behavior_model_stubs.build_outputs import build_model_summary
from student_behavior_model_stubs.build_outputs import build_overview_by_term
from student_behavior_model_stubs.build_outputs import build_student_reports
from student_behavior_model_stubs.build_outputs import build_student_results


def test_build_student_results_outputs_contract_aligned_columns() -> None:
    features = pd.DataFrame(
        [
            {
                "student_id": "20230002",
                "term_key": "2023-2",
                "major_name": "软件工程",
                "avg_course_score": 58,
                "failed_course_count": 2,
                "attendance_normal_rate": 0.43,
                "sign_event_count": 3,
                "selected_course_count": 4,
                "library_visit_count": 1,
            }
        ]
    )

    results = build_student_results(features)

    assert list(results.columns) == [
        "student_id",
        "term_key",
        "student_name",
        "major_name",
        "quadrant_label",
        "risk_probability",
        "risk_level",
        "dimension_scores_json",
    ]
    assert results.to_dict(orient="records") == [
        {
            "student_id": "20230002",
            "term_key": "2023-2",
            "student_name": "20230002",
            "major_name": "软件工程",
            "quadrant_label": "脱节离散型",
            "risk_probability": 0.68,
            "risk_level": "medium",
            "dimension_scores_json": (
                '[{"dimension":"学业基础表现","score":0.58},'
                '{"dimension":"课堂学习投入","score":0.4},'
                '{"dimension":"学习行为活跃度","score":0.12},'
                '{"dimension":"生活规律与资源使用","score":0.23}]'
            ),
        }
    ]


def test_build_student_reports_outputs_jsonl_ready_records() -> None:
    results = pd.DataFrame(
        [
            {
                "student_id": "20230002",
                "term_key": "2023-2",
                "student_name": "20230002",
                "major_name": "软件工程",
                "quadrant_label": "脱节离散型",
                "risk_probability": 0.68,
                "risk_level": "medium",
                "dimension_scores_json": (
                    '[{"dimension":"学业基础表现","score":0.58},'
                    '{"dimension":"课堂学习投入","score":0.4},'
                    '{"dimension":"学习行为活跃度","score":0.12},'
                    '{"dimension":"生活规律与资源使用","score":0.23}]'
                ),
            }
        ]
    )

    reports = build_student_reports(results)

    assert reports == [
        {
            "student_id": "20230002",
            "term_key": "2023-2",
            "top_factors": [
                {
                    "feature": "behavior_activity",
                    "feature_cn": "学习行为活跃度",
                    "effect": "positive",
                    "importance": 0.69,
                },
                {
                    "feature": "routine_resource_use",
                    "feature_cn": "生活规律与资源使用",
                    "effect": "positive",
                    "importance": 0.64,
                },
                {
                    "feature": "class_engagement",
                    "feature_cn": "课堂学习投入",
                    "effect": "positive",
                    "importance": 0.55,
                },
            ],
            "intervention_advice": [
                "建议先聚焦课堂参与和作息稳定，按周观察变化趋势。",
                "把学习任务拆成小步执行，并保留固定的反馈节奏。",
                "继续维持已有的正向行为，同时减少波动较大的环节。",
            ],
            "report_text": (
                "## 学生群体画像\n"
                "该学生被系统归类为「脱节离散型」群体，当前风险等级为 中风险。\n\n"
                "## 核心风险指标解读\n"
                "1. **学习行为活跃度**: 当前维度得分为 0.12，属于需要优先关注的弱项。\n"
                "2. **生活规律与资源使用**: 当前维度得分为 0.23，属于需要优先关注的弱项。\n"
                "3. **课堂学习投入**: 当前维度得分为 0.40，属于需要优先关注的弱项。\n\n"
                "## 建设性改进建议\n"
                "1. 建议先聚焦课堂参与和作息稳定，按周观察变化趋势。\n"
                "2. 把学习任务拆成小步执行，并保留固定的反馈节奏。\n"
                "3. 继续维持已有的正向行为，同时减少波动较大的环节。"
            ),
        }
    ]


def test_missing_student_name_falls_back_to_student_id_placeholder() -> None:
    features = pd.DataFrame(
        [
            {
                "student_id": "20230003",
                "term_key": "2023-1",
                "major_name": "数据科学",
                "student_name": "",
                "avg_course_score": 81,
                "failed_course_count": 0,
                "attendance_normal_rate": 0.91,
                "sign_event_count": 12,
                "selected_course_count": 6,
                "library_visit_count": 4,
            }
        ]
    )

    results = build_student_results(features)

    assert results.loc[0, "student_name"] == "20230003"


def test_build_student_results_sorts_by_student_id_and_term_key() -> None:
    features = pd.DataFrame(
        [
            {
                "student_id": "20230010",
                "term_key": "2023-2",
                "major_name": "软件工程",
                "avg_course_score": 88,
                "failed_course_count": 0,
                "attendance_normal_rate": 0.9,
                "sign_event_count": 8,
                "selected_course_count": 6,
                "library_visit_count": 5,
            },
            {
                "student_id": "20230002",
                "term_key": "2023-2",
                "major_name": "软件工程",
                "avg_course_score": 78,
                "failed_course_count": 1,
                "attendance_normal_rate": 0.8,
                "sign_event_count": 4,
                "selected_course_count": 5,
                "library_visit_count": 3,
            },
            {
                "student_id": "20230002",
                "term_key": "2023-1",
                "major_name": "软件工程",
                "avg_course_score": 82,
                "failed_course_count": 0,
                "attendance_normal_rate": 0.86,
                "sign_event_count": 5,
                "selected_course_count": 5,
                "library_visit_count": 4,
            },
        ]
    )

    results = build_student_results(features)

    assert list(results["student_id"]) == ["20230002", "20230002", "20230010"]
    assert list(results["term_key"]) == ["2023-1", "2023-2", "2023-2"]


def test_build_student_reports_sorts_by_student_id_and_term_key() -> None:
    student_results = pd.DataFrame(
        [
            {
                "student_id": "20230010",
                "term_key": "2023-2",
                "student_name": "20230010",
                "major_name": "软件工程",
                "quadrant_label": "脱节离散型",
                "risk_probability": 0.68,
                "risk_level": "medium",
                "dimension_scores_json": (
                    '[{"dimension":"学业基础表现","score":0.58},'
                    '{"dimension":"课堂学习投入","score":0.4},'
                    '{"dimension":"学习行为活跃度","score":0.12},'
                    '{"dimension":"生活规律与资源使用","score":0.23}]'
                ),
            },
            {
                "student_id": "20230002",
                "term_key": "2023-1",
                "student_name": "20230002",
                "major_name": "软件工程",
                "quadrant_label": "脱节离散型",
                "risk_probability": 0.68,
                "risk_level": "medium",
                "dimension_scores_json": (
                    '[{"dimension":"学业基础表现","score":0.58},'
                    '{"dimension":"课堂学习投入","score":0.4},'
                    '{"dimension":"学习行为活跃度","score":0.12},'
                    '{"dimension":"生活规律与资源使用","score":0.23}]'
                ),
            },
        ]
    )

    reports = build_student_reports(student_results)

    assert [record["student_id"] for record in reports] == ["20230002", "20230010"]
    assert [record["term_key"] for record in reports] == ["2023-1", "2023-2"]


def test_build_overview_by_term_includes_required_sections() -> None:
    student_results = pd.DataFrame(
        [
            {
                "student_id": "20230001",
                "term_key": "2023-1",
                "student_name": "20230001",
                "major_name": "软件工程",
                "quadrant_label": "脱节离散型",
                "risk_probability": 0.68,
                "risk_level": "medium",
                "dimension_scores_json": "[]",
            },
            {
                "student_id": "20230002",
                "term_key": "2023-1",
                "student_name": "20230002",
                "major_name": "软件工程",
                "quadrant_label": "自律共鸣型",
                "risk_probability": 0.22,
                "risk_level": "low",
                "dimension_scores_json": "[]",
            },
            {
                "student_id": "20230003",
                "term_key": "2023-2",
                "student_name": "20230003",
                "major_name": "数据科学",
                "quadrant_label": "情绪驱动型",
                "risk_probability": 0.81,
                "risk_level": "high",
                "dimension_scores_json": "[]",
            },
        ]
    )

    overview = build_overview_by_term(student_results)

    assert {
        "student_count",
        "risk_distribution",
        "quadrant_distribution",
        "major_risk_summary",
        "trend_summary",
    }.issubset(overview)
    assert isinstance(overview["trend_summary"], dict)


def test_build_model_summary_uses_fixed_now_for_updated_at_and_stub_fields() -> None:
    fixed_now = datetime(2024, 1, 2, 3, 4, 5)

    summary = build_model_summary(now=fixed_now)

    assert summary == {
        "cluster_method": "stub-quadrant-rules",
        "risk_model": "stub-risk-rules",
        "target_label": "综合测评低等级风险",
        "auc": 0.8347,
        "updated_at": "2024-01-02T03:04:05",
    }


def test_build_model_summary_updated_at_is_not_placeholder_text() -> None:
    summary = build_model_summary(now=datetime(2024, 1, 2, 3, 4, 5))

    assert summary["updated_at"] not in {"", "TBD", "PLACEHOLDER", "updated_at"}
