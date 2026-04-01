from pathlib import Path

from student_behavior_model_stubs.config import build_default_paths
from student_behavior_model_stubs.calibration import CALIBRATED_DIMENSIONS
from student_behavior_model_stubs.calibration import DIMENSION_LABELS
from student_behavior_model_stubs.calibration import LEVEL_LABELS
from student_behavior_model_stubs.calibration import METRIC_DISPLAY_METADATA
from student_behavior_model_stubs.calibration import METRIC_RULE_DECLARATIONS
from student_behavior_model_stubs.calibration import THRESHOLD_STRATEGY_METADATA


def test_build_default_paths_uses_project_bound_locations() -> None:
    repo_root = Path(r"C:\Users\Orion\Desktop\StudentBehavior")
    paths = build_default_paths(repo_root)
    assert paths.output_dir == repo_root / "artifacts" / "model_stubs"
    assert paths.student_results_csv == paths.output_dir / "v1_student_results.csv"
    assert paths.student_reports_jsonl == paths.output_dir / "v1_student_reports.jsonl"
    assert paths.overview_json == paths.output_dir / "v1_overview_by_term.json"
    assert paths.model_summary_json == paths.output_dir / "v1_model_summary.json"
    assert paths.warnings_json == paths.output_dir / "v1_warnings.json"


def test_calibration_config_exports_ordered_dimensions() -> None:
    assert CALIBRATED_DIMENSIONS == [
        "academic_base",
        "class_engagement",
        "online_activeness",
        "library_immersion",
        "network_habits",
        "daily_routine_boundary",
        "physical_resilience",
        "appraisal_status_alert",
    ]


def test_calibration_config_exports_metric_rules_and_display_metadata() -> None:
    assert LEVEL_LABELS == {"high": "高", "medium": "中", "low": "低"}
    assert set(THRESHOLD_STRATEGY_METADATA) == {"fixed", "quantile", "hybrid"}
    assert set(METRIC_DISPLAY_METADATA) == set(CALIBRATED_DIMENSIONS)
    assert set(METRIC_RULE_DECLARATIONS) == set(CALIBRATED_DIMENSIONS)
    expected_rules = {
        "academic_base": {
            "metrics": [
                "term_gpa",
                "failed_course_count",
                "borderline_course_count",
                "failed_course_ratio",
            ],
            "strategies": ["fixed", "fixed", "fixed", "fixed"],
            "raw_fields": {
                "term_gpa": ["JDCJ", "XF"],
                "failed_course_count": ["KCCJ", "DJCJ", "KSLXDM"],
                "borderline_course_count": ["KCCJ", "DJCJ"],
                "failed_course_ratio": ["KCCJ", "DJCJ", "KSLXDM"],
            },
            "display": [
                "学期GPA",
                "挂科门数",
                "边缘课程数",
                "挂科占比",
            ],
        },
        "class_engagement": {
            "metrics": [
                "attendance_rate",
                "late_count",
                "truancy_count",
                "absence_count",
            ],
            "strategies": ["fixed", "fixed", "fixed", "fixed"],
            "raw_fields": {
                "attendance_rate": ["ZTDM", "ZT", "DKSJ"],
                "late_count": ["ZTDM", "ZT", "DKSJ"],
                "truancy_count": ["ZTDM", "ZT", "DKSJ"],
                "absence_count": ["ZTDM", "ZT", "DKSJ"],
            },
            "display": [
                "出勤率",
                "迟到次数",
                "旷课次数",
                "缺勤次数",
            ],
        },
        "online_activeness": {
            "metrics": [
                "video_completion_rate",
                "online_test_avg_score",
                "online_work_avg_score",
                "online_exam_avg_score",
                "platform_engagement_score",
                "forum_interaction_total",
            ],
            "strategies": ["fixed", "fixed", "fixed", "fixed", "quantile", "quantile"],
            "raw_fields": {
                "video_completion_rate": ["VIDEOJOB_RATE"],
                "online_test_avg_score": ["TEST_AVGSCORE"],
                "online_work_avg_score": ["WORK_AVGSCORE"],
                "online_exam_avg_score": ["EXAM_AVGSCORE"],
                "platform_engagement_score": ["BFB"],
                "forum_interaction_total": ["BBS_NUM", "TOPIC_NUM", "REPLY_NUM"],
            },
            "display": [
                "视频完成率",
                "测验均分",
                "作业均分",
                "考试均分",
                "平台活跃度",
                "论坛互动总量",
            ],
        },
        "library_immersion": {
            "metrics": [
                "library_completed_visit_count",
                "avg_library_stay_minutes",
                "weekly_library_visit_avg",
            ],
            "strategies": ["hybrid", "fixed", "hybrid"],
            "raw_fields": {
                "library_completed_visit_count": ["visittime", "direction", "gateno"],
                "avg_library_stay_minutes": ["visittime", "direction"],
                "weekly_library_visit_avg": ["visittime"],
            },
            "display": [
                "入馆次数",
                "平均停留时长",
                "周均入馆次数",
            ],
        },
        "network_habits": {
            "metrics": [
                "monthly_online_duration_avg",
                "term_online_duration_sum",
                "online_duration_vs_school_avg_gap",
            ],
            "strategies": ["hybrid", "hybrid", "hybrid"],
            "raw_fields": {
                "monthly_online_duration_avg": ["SWLJSC"],
                "term_online_duration_sum": ["SWLJSC", "TJNY", "XN", "XQ"],
                "online_duration_vs_school_avg_gap": ["SWLJSC", "TJNY", "XN", "XQ", "XXPJZ"],
            },
            "display": [
                "月均上网时长",
                "学期总上网时长",
                "相对学校平均值偏差",
            ],
        },
        "daily_routine_boundary": {
            "metrics": [
                "first_daily_access_time_avg",
                "first_daily_access_time_std",
                "late_return_count",
                "late_return_ratio",
                "daily_access_time_variability",
            ],
            "strategies": ["hybrid", "hybrid", "fixed", "fixed", "quantile"],
            "raw_fields": {
                "first_daily_access_time_avg": ["LOGINTIME", "LOGINSIGN"],
                "first_daily_access_time_std": ["LOGINTIME", "LOGINSIGN"],
                "late_return_count": ["LOGINTIME", "LOGINSIGN"],
                "late_return_ratio": ["LOGINTIME", "LOGINSIGN"],
                "daily_access_time_variability": ["LOGINTIME"],
            },
            "display": [
                "首次进出平均时间",
                "时间波动",
                "晚归次数",
                "晚归比例",
                "日内作息波动",
            ],
        },
        "physical_resilience": {
            "metrics": [
                "physical_test_avg_score",
                "physical_test_pass_flag",
                "weekly_running_count_avg",
                "weekly_exercise_count_avg",
            ],
            "strategies": ["fixed", "fixed", "quantile", "quantile"],
            "raw_fields": {
                "physical_test_avg_score": ["ZF", "TCNF"],
                "physical_test_pass_flag": ["ZF"],
                "weekly_running_count_avg": ["PUNCH_DAY", "WEEKNUM"],
                "weekly_exercise_count_avg": ["DKCS", "ZC", "XQ"],
            },
            "display": [
                "体测均分",
                "是否达标",
                "周均跑步次数",
                "周均锻炼次数",
            ],
        },
        "appraisal_status_alert": {
            "metrics": [
                "scholarship_amount_sum",
                "scholarship_level_score",
                "negative_status_alert_flag",
                "status_change_count",
            ],
            "strategies": ["fixed", "fixed", "fixed", "fixed"],
            "raw_fields": {
                "scholarship_amount_sum": ["FFJE"],
                "scholarship_level_score": ["PDDJ", "JLJB"],
                "negative_status_alert_flag": ["SFZX", "YDLBDM", "YDYYDM"],
                "status_change_count": ["YDLBDM", "YDYYDM", "YDRQ"],
            },
            "display": [
                "奖学金金额",
                "奖学金等级",
                "是否存在异动预警",
                "异动次数",
            ],
        },
    }
    for dimension, expected in expected_rules.items():
        rules = METRIC_RULE_DECLARATIONS[dimension]
        assert [rule["metric"] for rule in rules] == expected["metrics"]
        assert [rule["threshold_strategy"] for rule in rules] == expected["strategies"]
        assert [rule["display_name"] for rule in rules] == expected["display"]
        assert METRIC_DISPLAY_METADATA[dimension]["dimension_label"] == DIMENSION_LABELS[dimension]
        assert METRIC_DISPLAY_METADATA[dimension]["metric_labels"] == expected["display"]
        assert METRIC_DISPLAY_METADATA[dimension]["metric_names"] == expected["metrics"]
        assert METRIC_DISPLAY_METADATA[dimension]["metric_evidence_labels"] == expected["display"]
        assert len(METRIC_DISPLAY_METADATA[dimension]["metric_aggregations"]) == len(expected["metrics"])
        assert len(METRIC_DISPLAY_METADATA[dimension]["metric_directions"]) == len(expected["metrics"])
        assert METRIC_DISPLAY_METADATA[dimension]["level_labels"] == LEVEL_LABELS
        for metric_name, raw_fields in expected["raw_fields"].items():
            rule = next(rule for rule in rules if rule["metric"] == metric_name)
            assert rule["dimension_label"] == DIMENSION_LABELS[dimension]
            assert rule["raw_fields"] == raw_fields
            assert rule["evidence_label"]
            assert rule["aggregation"]
            assert rule["influence_direction"] in {"positive", "negative", "neutral"}
            assert "deferred_status" in rule

    assert METRIC_RULE_DECLARATIONS["class_engagement"][0]["deferred_status"]["state"] == "caveated"
    assert METRIC_RULE_DECLARATIONS["network_habits"][0]["deferred_status"]["condition"] == "deep_night_metrics_blocked"
