from pathlib import Path

import pandas as pd
import pytest

from student_behavior_analytics_db.build_demo_features_from_excels import (
    _build_row_hash,
    _is_late_return_event,
    build_demo_features_from_excels,
)


def _write_excel(path: Path, rows: list[dict[str, object]], columns: list[str] | None = None) -> None:
    frame = pd.DataFrame(rows, columns=columns)
    frame.to_excel(path, index=False)


def _write_required_default_excels(
    data_dir: Path,
    *,
    student_rows: list[dict[str, object]],
    grade_rows: list[dict[str, object]] | None = None,
    attendance_rows: list[dict[str, object]] | None = None,
    enrollment_rows: list[dict[str, object]] | None = None,
    evaluation_rows: list[dict[str, object]] | None = None,
) -> None:
    _write_excel(
        data_dir / "学生基本信息.xlsx",
        student_rows,
        ["XH", "XB", "MZMC", "ZZMMMC", "XSM", "ZYM"],
    )
    _write_excel(
        data_dir / "学生成绩.xlsx",
        grade_rows or [],
        ["XH", "KSSJ", "KCH", "KCM", "KCCJ", "JDCJ", "XF", "DJCJ", "KSLXDM", "CXBKBZ"],
    )
    _write_excel(
        data_dir / "考勤汇总.xlsx",
        attendance_rows or [],
        ["XN", "XQ", "RQ", "XH", "ZT", "DKSJ"],
    )
    _write_excel(
        data_dir / "学生选课信息.xlsx",
        enrollment_rows or [],
        ["XH", "JXBH", "KCH", "KKXN", "KKXQ"],
    )
    _write_excel(
        data_dir / "本科生综合测评.xlsx",
        evaluation_rows or [],
        ["XH", "CPXN", "CPXQ", "PDXN", "PDXQ", "ZYNJPM", "ZYNJRS"],
    )


def _write_required_heavy_excels(data_dir: Path) -> None:
    _write_excel(data_dir / "学生签到记录.xlsx", [], ["LOGIN_NAME", "ATTEND_TIME", "INSERT_TIME"])
    _write_excel(data_dir / "图书馆打卡记录.xlsx", [], ["cardld", "visittime", "direction"])
    _write_excel(
        data_dir / "学生作业提交记录.xlsx",
        [],
        [
            "CREATER_LOGIN_NAME",
            "WORK_ID",
            "WORK_TITLE",
            "COURSE_ID",
            "COURSE_NAME",
            "STATUS",
            "FULLMARKS",
            "SCORE",
            "TYPE",
            "CREATER_TIME",
            "ANSWER_TIME",
            "REVIEW_TIME",
            "UPDATE_TIME",
            "INSERT_TIME",
        ],
    )
    _write_excel(
        data_dir / "考试提交记录.xlsx",
        [],
        [
            "CREATER_LOGIN_NAME",
            "WORK_ID",
            "WORK_TITLE",
            "COURSE_ID",
            "COURSE_NAME",
            "STATUS",
            "FULLMARKS",
            "SCORE",
            "TYPE",
            "CREATER_TIME",
            "ANSWER_TIME",
            "REVIEW_TIME",
            "UPDATE_TIME",
            "INSERT_TIME",
        ],
    )
    _write_excel(
        data_dir / "讨论记录.xlsx",
        [],
        [
            "COURSE_ID",
            "COURSE_NAME",
            "TOPIC_ID",
            "TOPIC_TITLE",
            "CREATER_ROLE",
            "CREATER_NAME",
            "CREATER_LOGIN_NAME",
            "CREATE_TIME",
            "REPLY_USER_NAME",
            "REPLY_LOGIN_NAME",
            "REPLY_USER_ROLE",
            "REPLY_CONTENT",
            "ISDELETE",
            "INSERT_TIME",
            "TOPIC_ISDELETE",
        ],
    )
    _write_excel(
        data_dir / "课堂任务参与.xlsx",
        [],
        [
            "USER_ID",
            "LOGIN_NAME",
            "USER_NAME",
            "DEPARTMENT_NAME",
            "MAJOR_NAME",
            "CLASS_NAME",
            "STATE",
            "SCHOOL_YEAR",
            "COURSE_ID",
            "COURSE_NAME",
            "JWCOURSE_ID",
            "CREATE_TIME",
            "TASK_RATE",
            "UPDATE_TIME",
            "INSERT_TIME",
        ],
    )
    _write_excel(data_dir / "跑步打卡.xlsx", [], ["PUNCH_DAY", "PUNCH_TIME", "TERM_ID", "USERNUM", "STATE"])


def test_build_row_hash_is_content_based_and_row_order_independent():
    row = {"XH": "pjxyqxbj901", "KCCJ": 85}
    same_content_different_order = {"KCCJ": 85, "XH": "pjxyqxbj901"}

    assert _build_row_hash("学生成绩.xlsx", 2, row) == _build_row_hash(
        "学生成绩.xlsx", 99, same_content_different_order
    )
    assert _build_row_hash("学生成绩.xlsx", 2, row) != _build_row_hash(
        "学生成绩.xlsx", 2, {"XH": "pjxyqxbj901", "KCCJ": 86}
    )


def test_is_late_return_event_uses_22_to_05_59_window():
    assert _is_late_return_event(pd.Timestamp("2024-09-02 22:30:00"), 1) is True
    assert _is_late_return_event(pd.Timestamp("2024-09-03 05:59:59"), 1) is True
    assert _is_late_return_event(pd.Timestamp("2024-09-02 21:59:59"), 1) is False
    assert _is_late_return_event(pd.Timestamp("2024-09-03 06:00:00"), 1) is False


def test_is_late_return_event_requires_explicit_return_sign():
    assert _is_late_return_event(pd.Timestamp("2024-09-02 22:30:00"), None) is False
    assert _is_late_return_event(pd.Timestamp("2024-09-02 22:30:00"), "") is False


def test_build_demo_features_from_excels_generates_filtered_csv(tmp_path: Path):
    repo_root = tmp_path / "repo"
    data_dir = repo_root / "数据集及类型"
    output_csv = repo_root / "artifacts" / "semester_features" / "v1_semester_features.csv"
    data_dir.mkdir(parents=True)

    student_id = "pjxyqxbj901"
    neutral_status_student_id = "pjxyqxbj902"

    pd.DataFrame(
        [
            {"XH": student_id, "XB": "男", "MZMC": "汉族", "ZZMMMC": "群众", "XSM": "计科1班", "ZYM": "计算机科学"},
            {"XH": neutral_status_student_id, "XB": "女", "MZMC": "汉族", "ZZMMMC": "群众", "XSM": "计科2班", "ZYM": "软件工程"},
        ]
    ).to_excel(
        data_dir / "学生基本信息.xlsx", index=False
    )
    pd.DataFrame(
        [
            {
                "XH": student_id,
                "KSSJ": "2024-09-02 09:00:00",
                "KCH": "CS201",
                "KCM": "数据结构",
                "KCCJ": 55,
                "JDCJ": 1.2,
                "XF": 3,
                "DJCJ": "55",
                "KSLXDM": "01",
                "CXBKBZ": 0,
            },
            {
                "XH": student_id,
                "KSSJ": "2024-09-10 09:00:00",
                "KCH": "CS202",
                "KCM": "离散数学",
                "KCCJ": 65,
                "JDCJ": 2.5,
                "XF": 2,
                "DJCJ": "65",
                "KSLXDM": "01",
                "CXBKBZ": 0,
            },
        ]
    ).to_excel(
        data_dir / "学生成绩.xlsx", index=False
    )
    pd.DataFrame(
        [
            {"XN": "2024-2025", "XQ": 1, "RQ": "2024-09-02", "XH": student_id, "ZT": "正常", "DKSJ": "2024-09-02 08:01:00"},
            {"XN": "2024-2025", "XQ": 1, "RQ": "2024-09-03", "XH": student_id, "ZT": "迟到", "DKSJ": "2024-09-03 08:20:00"},
            {"XN": "2024-2025", "XQ": 1, "RQ": "2024-09-04", "XH": student_id, "ZT": "旷课", "DKSJ": "2024-09-04 08:00:00"},
            {"XN": "2024-2025", "XQ": 1, "RQ": "2024-09-05", "XH": student_id, "ZT": "缺勤", "DKSJ": "2024-09-05 08:00:00"},
        ]
    ).to_excel(
        data_dir / "考勤汇总.xlsx", index=False
    )
    pd.DataFrame([{"XH": student_id, "KKXN": "2024-2025", "KKXQ": 1, "KCH": "CS201", "JXBH": "JXB001"}]).to_excel(
        data_dir / "学生选课信息.xlsx", index=False
    )
    pd.DataFrame([{"LOGIN_NAME": student_id, "ATTEND_TIME": 1725264000000, "INSERT_TIME": "2024-09-02 08:01:00"}]).to_excel(
        data_dir / "学生签到记录.xlsx", index=False
    )
    pd.DataFrame(
        [
            {"cardld": student_id, "visittime": "2024-09-03 08:00:00", "direction": "in", "gateno": "A01"},
            {"cardld": student_id, "visittime": "2024-09-03 10:00:00", "direction": "out", "gateno": "A01"},
            {"cardld": student_id, "visittime": "2024-09-04 09:00:00", "direction": "in", "gateno": "A01"},
            {"cardld": student_id, "visittime": "2024-09-04 12:00:00", "direction": "out", "gateno": "A01"},
        ]
    ).to_excel(
        data_dir / "图书馆打卡记录.xlsx", index=False
    )
    pd.DataFrame([{"CREATER_LOGIN_NAME": student_id, "WORK_ID": 1, "COURSE_ID": 101, "COURSE_NAME": "数据结构", "STATUS": 1, "FULLMARKS": 100, "SCORE": 90, "TYPE": 1, "CREATER_TIME": "2024-09-05 10:00:00", "ANSWER_TIME": "2024-09-05 11:00:00", "REVIEW_TIME": "2024-09-06 12:00:00", "UPDATE_TIME": "2024-09-06 13:00:00", "INSERT_TIME": "2024-09-05 10:00:00"}]).to_excel(
        data_dir / "学生作业提交记录.xlsx", index=False
    )
    pd.DataFrame([{"CREATER_LOGIN_NAME": student_id, "WORK_ID": 2, "COURSE_ID": 101, "COURSE_NAME": "数据结构", "STATUS": 1, "FULLMARKS": 100, "SCORE": 88, "TYPE": 1, "CREATER_TIME": "2024-09-10 10:00:00", "ANSWER_TIME": "2024-09-10 11:00:00", "REVIEW_TIME": "2024-09-11 12:00:00", "UPDATE_TIME": "2024-09-11 13:00:00", "INSERT_TIME": "2024-09-10 10:00:00"}]).to_excel(
        data_dir / "考试提交记录.xlsx", index=False
    )
    pd.DataFrame([{"COURSE_ID": 101, "COURSE_NAME": "数据结构", "TOPIC_ID": 1, "TOPIC_TITLE": "讨论1", "CREATER_ROLE": 1, "CREATER_NAME": "学生A", "CREATER_LOGIN_NAME": student_id, "CREATE_TIME": "2024-09-12 10:00:00", "REPLY_USER_NAME": "学生A", "REPLY_LOGIN_NAME": student_id, "REPLY_USER_ROLE": 1, "REPLY_CONTENT": "已完成", "ISDELETE": 0, "INSERT_TIME": "2024-09-12 10:00:00", "TOPIC_ISDELETE": 0}]).to_excel(
        data_dir / "讨论记录.xlsx", index=False
    )
    pd.DataFrame(
        [
            {
                "USER_ID": 1,
                "LOGIN_NAME": student_id,
                "USER_NAME": "学生A",
                "DEPARTMENT_NAME": "信息学院",
                "MAJOR_NAME": "计算机科学",
                "CLASS_NAME": "计科1班",
                "STATE": 1,
                "SCHOOL_YEAR": "2024-2025",
                "COURSE_ID": 101,
                "COURSE_NAME": "数据结构",
                "JWCOURSE_ID": "JW101",
                "CREATE_TIME": "2024-09-01 09:00:00",
                "TASK_RATE": 0.8,
                "VIDEOJOB_RATE": 0.8,
                "VIDEOJOB_TIME": 120,
                "TEST_AVGSCORE": 80,
                "WORK_AVGSCORE": 85,
                "EXAM_AVGSCORE": 90,
                "BBS_NUM": 2,
                "TOPIC_NUM": 1,
                "REPLY_NUM": 3,
                "PV": 50,
                "UPDATE_TIME": "2024-09-01 10:00:00",
                "INSERT_TIME": "2024-09-01 09:00:00",
            }
        ]
    ).to_excel(
        data_dir / "课堂任务参与.xlsx", index=False
    )
    pd.DataFrame(
        [
            {"PUNCH_DAY": "2024-09-02", "PUNCH_TIME": "06:30:00", "TERM_ID": 1, "USERNUM": student_id, "STATE": 1},
            {"PUNCH_DAY": "2024-09-09", "PUNCH_TIME": "06:45:00", "TERM_ID": 1, "USERNUM": student_id, "STATE": 1},
        ]
    ).to_excel(
        data_dir / "跑步打卡.xlsx", index=False
    )
    pd.DataFrame([{"XH": student_id, "CPXN": "2024-2025", "CPXQ": 1, "PDXN": "2024-2025", "PDXQ": 1, "ZYNJPM": 90, "ZYNJRS": 100}]).to_excel(
        data_dir / "本科生综合测评.xlsx", index=False
    )
    pd.DataFrame([{"LOGIN_NAME": student_id, "XM": "学生A", "DEPARTMENT_NAME": "信息学院", "MAJOR_NAME": "计算机科学", "CLASS_NAME": "计科1班", "ROLEID": 3, "BFB": 99.6}]).to_excel(
        data_dir / "线上学习（综合表现）.xlsx", index=False
    )
    pd.DataFrame(
        [
            {"XSBH": student_id, "TJNY": "2024-09-01", "SWLJSC": 100, "XXPJZ": 80, "XN": "2024-2025", "XQ": 1},
            {"XSBH": student_id, "TJNY": "2024-10-01", "SWLJSC": 140, "XXPJZ": 90, "XN": "2024-2025", "XQ": 1},
        ]
    ).to_excel(data_dir / "上网统计.xlsx", index=False)
    pd.DataFrame(
        [
            {"IDSERTAL": student_id, "LOGINTIME": "2024-09-02 06:30:00", "LOGINADDRESS": "A校区-东南门", "LOGINSIGN": 0},
            {"IDSERTAL": student_id, "LOGINTIME": "2024-09-02 22:30:00", "LOGINADDRESS": "A校区-东南门", "LOGINSIGN": 1},
            {"IDSERTAL": student_id, "LOGINTIME": "2024-09-03 07:30:00", "LOGINADDRESS": "A校区-东南门", "LOGINSIGN": 0},
            {"IDSERTAL": student_id, "LOGINTIME": "2024-09-03 23:30:00", "LOGINADDRESS": "A校区-东南门", "LOGINSIGN": 1},
            {"IDSERTAL": student_id, "LOGINTIME": "2024-09-04 06:45:00", "LOGINADDRESS": "A校区-东南门", "LOGINSIGN": 0},
            {"IDSERTAL": student_id, "LOGINTIME": "2024-09-04 21:30:00", "LOGINADDRESS": "A校区-东南门", "LOGINSIGN": 1},
        ]
    ).to_excel(data_dir / "门禁数据.xlsx", index=False)
    pd.DataFrame([{"XH": student_id, "TCNF": 2024, "ZF": 85, "BMI": "175/68", "FHL": 2300, "WS": 9.1, "LDTY": 180}]).to_excel(
        data_dir / "体测数据.xlsx", index=False
    )
    pd.DataFrame(
        [
            {"XH": student_id, "XQ": "2024-2025学年第1学期", "ZC": 1, "DKCS": 11},
            {"XH": student_id, "XQ": "2024-2025学年第1学期", "ZC": 2, "DKCS": 9},
        ]
    ).to_excel(data_dir / "日常锻炼.xlsx", index=False)
    pd.DataFrame([{"XSBH": student_id, "JXJMC": "本科生一等奖学金", "PDXN": "2024-2025", "PDDJ": "一等奖", "JLJB": "校级", "FFJE": 5000}]).to_excel(
        data_dir / "奖学金获奖.xlsx", index=False
    )
    pd.DataFrame(
        [
            {"XH": student_id, "YDRQ": "2024-10-08", "YDLBDM": "休学", "YDYYDM": "health", "SFZX": "不在校"},
            {"XH": neutral_status_student_id, "YDRQ": "2024-10-09", "YDLBDM": "转专业", "YDYYDM": "major_adjustment", "SFZX": "在校"},
        ]
    ).to_excel(
        data_dir / "学籍异动.xlsx", index=False
    )
    pd.DataFrame([{"COURSE_CODE": "CS201", "TEACH_TIME": "2024-09-02 1-2", "HEAD_UP_RATE": 0.9, "FRONT_ROW_RATE": 0.4, "BOWING_RATE": 0.1}]).to_excel(
        data_dir / "上课信息统计表.xlsx", index=False
    )

    summary = build_demo_features_from_excels(repo_root=repo_root, data_dir=data_dir, output_csv=output_csv)

    assert summary["row_count"] == 2
    assert summary["include_heavy_sources"] is True
    frame = pd.read_csv(output_csv)
    expected_dimension_columns = {
        "academic_base_score_raw",
        "class_engagement_score_raw",
        "online_activeness_score_raw",
        "library_immersion_score_raw",
        "network_habits_score_raw",
        "daily_routine_boundary_score_raw",
        "physical_resilience_score_raw",
        "appraisal_status_alert_score_raw",
    }
    assert expected_dimension_columns.issubset(frame.columns)
    expected_support_columns = {
        "absence_count",
        "video_watch_time_sum",
        "online_test_avg_score",
        "online_work_avg_score",
        "online_exam_avg_score",
        "platform_engagement_score",
        "library_completed_visit_count",
        "monthly_online_duration_avg",
        "first_daily_access_time_avg",
        "first_daily_access_time_std",
        "late_return_ratio",
        "daily_access_time_variability",
        "scholarship_level_score",
        "status_change_count",
    }
    assert expected_support_columns.issubset(frame.columns)

    student_frame = frame.loc[frame["student_id"] == student_id].reset_index(drop=True)
    neutral_status_frame = frame.loc[frame["student_id"] == neutral_status_student_id].reset_index(drop=True)

    assert len(student_frame) == 1
    assert len(neutral_status_frame) == 1

    assert student_frame.loc[0, "student_id"] == student_id
    assert student_frame.loc[0, "term_key"] == "2024-1"
    assert student_frame.loc[0, "failed_course_count"] == 1
    assert student_frame.loc[0, "borderline_course_count"] == 1
    assert student_frame.loc[0, "attempted_credit_sum"] == 5
    assert student_frame.loc[0, "failed_course_ratio"] == 0.5
    assert student_frame.loc[0, "attendance_rate"] == pytest.approx(0.25)
    assert student_frame.loc[0, "late_count"] == 1
    assert student_frame.loc[0, "truancy_count"] == 1
    assert student_frame.loc[0, "absence_count"] == 1
    assert bool(student_frame.loc[0, "class_attention_metrics_available"]) is False
    assert "avg_head_up_rate" in frame.columns
    assert "avg_front_row_rate" in frame.columns
    assert "avg_bowing_rate" in frame.columns
    assert pd.isna(student_frame.loc[0, "avg_head_up_rate"])
    assert pd.isna(student_frame.loc[0, "avg_front_row_rate"])
    assert pd.isna(student_frame.loc[0, "avg_bowing_rate"])
    assert student_frame.loc[0, "video_completion_rate"] == 0.8
    assert student_frame.loc[0, "video_watch_time_sum"] == 120
    assert student_frame.loc[0, "online_test_avg_score"] == 80
    assert student_frame.loc[0, "online_work_avg_score"] == 85
    assert student_frame.loc[0, "online_exam_avg_score"] == 90
    assert student_frame.loc[0, "platform_engagement_score"] == pytest.approx(99.6)
    assert student_frame.loc[0, "forum_interaction_total"] == 6
    assert student_frame.loc[0, "library_visit_count"] == 4
    assert student_frame.loc[0, "library_completed_visit_count"] == 2
    assert student_frame.loc[0, "avg_library_stay_minutes"] == 150
    assert student_frame.loc[0, "term_online_duration_sum"] == 240
    assert student_frame.loc[0, "monthly_online_duration_avg"] == 120
    assert student_frame.loc[0, "online_duration_vs_school_avg_gap"] == 35
    assert bool(student_frame.loc[0, "network_habits_deep_night_metrics_available"]) is False
    assert student_frame.loc[0, "late_return_count"] == 2
    assert student_frame.loc[0, "first_daily_access_time_avg"] == pytest.approx(415)
    assert student_frame.loc[0, "first_daily_access_time_std"] == pytest.approx(25.495097567963924)
    assert student_frame.loc[0, "late_return_ratio"] == pytest.approx(2 / 3)
    assert student_frame.loc[0, "daily_access_time_variability"] == 60
    assert student_frame.loc[0, "physical_test_avg_score"] == 85
    assert bool(student_frame.loc[0, "physical_test_pass_flag"]) is True
    assert student_frame.loc[0, "weekly_exercise_count_avg"] == 10
    assert student_frame.loc[0, "scholarship_amount_sum"] == 5000
    assert student_frame.loc[0, "scholarship_level_score"] == 3
    assert student_frame.loc[0, "status_change_count"] == 1
    assert str(student_frame.loc[0, "negative_status_alert_flag"]).lower() == "true"

    assert neutral_status_frame.loc[0, "term_key"] == "2024-1"
    assert neutral_status_frame.loc[0, "status_change_count"] == 1
    assert str(neutral_status_frame.loc[0, "negative_status_alert_flag"]).lower() == "false"
    assert pd.isna(neutral_status_frame.loc[0, "scholarship_level_score"])

    assert student_frame.loc[0, "class_engagement_score_raw"] == pytest.approx(63.75)
    assert student_frame.loc[0, "online_activeness_score_raw"] == pytest.approx(79.1)
    assert student_frame.loc[0, "network_habits_score_raw"] == pytest.approx(62.5)
    assert student_frame.loc[0, "daily_routine_boundary_score_raw"] == pytest.approx(61.26511449689791)
    assert student_frame.loc[0, "appraisal_status_alert_score_raw"] == pytest.approx(50)
    assert neutral_status_frame.loc[0, "appraisal_status_alert_score_raw"] == pytest.approx(100)
    for column in expected_dimension_columns:
        assert pd.notna(student_frame.loc[0, column])


def test_build_demo_features_from_excels_drops_unmapped_alias_student_rows(tmp_path: Path):
    repo_root = tmp_path / "repo"
    data_dir = repo_root / "数据集及类型"
    output_csv = repo_root / "artifacts" / "semester_features" / "v1_semester_features.csv"
    data_dir.mkdir(parents=True)

    official_student_id = "pjxyqxbj901"
    _write_required_default_excels(
        data_dir,
        student_rows=[
            {"XH": official_student_id, "XB": "男", "MZMC": "汉族", "ZZMMMC": "群众", "XSM": "计科1班", "ZYM": "计算机科学"}
        ],
        grade_rows=[
            {
                "XH": official_student_id,
                "KSSJ": "2024-09-02 09:00:00",
                "KCH": "CS201",
                "KCM": "数据结构",
                "KCCJ": 75,
                "JDCJ": 2.8,
                "XF": 3,
                "DJCJ": "75",
                "KSLXDM": "01",
                "CXBKBZ": 0,
            }
        ],
    )
    _write_excel(
        data_dir / "学籍异动.xlsx",
        [{"LOGIN_NAME": "alias-not-on-roster", "YDRQ": "2024-10-08", "YDLBDM": "休学", "YDYYDM": "health", "SFZX": "不在校"}],
        ["LOGIN_NAME", "YDRQ", "YDLBDM", "YDYYDM", "SFZX"],
    )
    _write_required_heavy_excels(data_dir)

    summary = build_demo_features_from_excels(repo_root=repo_root, data_dir=data_dir, output_csv=output_csv)

    assert summary["row_count"] == 1
    frame = pd.read_csv(output_csv)
    assert frame["student_id"].tolist() == [official_student_id]


def test_build_demo_features_from_excels_includes_heavy_metrics_by_default(tmp_path: Path):
    repo_root = tmp_path / "repo"
    data_dir = repo_root / "数据集及类型"
    output_csv = repo_root / "artifacts" / "semester_features" / "v1_semester_features.csv"
    data_dir.mkdir(parents=True)

    student_id = "pjxyqxbj901"
    _write_required_default_excels(
        data_dir,
        student_rows=[
            {"XH": student_id, "XB": "男", "MZMC": "汉族", "ZZMMMC": "群众", "XSM": "计科1班", "ZYM": "计算机科学"}
        ],
        grade_rows=[
            {
                "XH": student_id,
                "KSSJ": "2024-09-02 09:00:00",
                "KCH": "CS201",
                "KCM": "数据结构",
                "KCCJ": 75,
                "JDCJ": 2.8,
                "XF": 3,
                "DJCJ": "75",
                "KSLXDM": "01",
                "CXBKBZ": 0,
            }
        ],
    )
    _write_required_heavy_excels(data_dir)
    _write_excel(
        data_dir / "课堂任务参与.xlsx",
        [
            {
                "LOGIN_NAME": student_id,
                "SCHOOL_YEAR": "2024-2025",
                "COURSE_ID": 101,
                "COURSE_NAME": "数据结构",
                "CREATE_TIME": "2024-09-01 09:00:00",
                "TASK_RATE": 0.8,
                "VIDEOJOB_RATE": 0.8,
                "VIDEOJOB_TIME": 120,
                "TEST_AVGSCORE": 80,
                "WORK_AVGSCORE": 85,
                "EXAM_AVGSCORE": 90,
                "UPDATE_TIME": "2024-09-01 10:00:00",
                "INSERT_TIME": "2024-09-01 09:00:00",
            }
        ],
        [
            "LOGIN_NAME",
            "SCHOOL_YEAR",
            "COURSE_ID",
            "COURSE_NAME",
            "CREATE_TIME",
            "TASK_RATE",
            "VIDEOJOB_RATE",
            "VIDEOJOB_TIME",
            "TEST_AVGSCORE",
            "WORK_AVGSCORE",
            "EXAM_AVGSCORE",
            "UPDATE_TIME",
            "INSERT_TIME",
        ],
    )
    _write_excel(
        data_dir / "线上学习（综合表现）.xlsx",
        [{"LOGIN_NAME": student_id, "XM": "学生A", "ROLEID": 3, "BFB": 99.6}],
        ["LOGIN_NAME", "XM", "ROLEID", "BFB"],
    )
    _write_excel(
        data_dir / "上网统计.xlsx",
        [{"XSBH": student_id, "TJNY": "2024-09-01", "SWLJSC": 100, "XXPJZ": 80, "XN": "2024-2025", "XQ": 1}],
        ["XSBH", "TJNY", "SWLJSC", "XXPJZ", "XN", "XQ"],
    )
    _write_excel(
        data_dir / "图书馆打卡记录.xlsx",
        [
            {"cardld": student_id, "visittime": "2024-09-03 08:00:00", "direction": "in"},
            {"cardld": student_id, "visittime": "2024-09-03 10:00:00", "direction": "out"},
        ],
        ["cardld", "visittime", "direction"],
    )

    summary = build_demo_features_from_excels(repo_root=repo_root, data_dir=data_dir, output_csv=output_csv)

    assert summary["include_heavy_sources"] is True
    frame = pd.read_csv(output_csv)
    assert frame.loc[0, "video_watch_time_sum"] == 120
    assert frame.loc[0, "term_online_duration_sum"] == 100
    assert frame.loc[0, "library_completed_visit_count"] == 1
    assert pd.notna(frame.loc[0, "online_activeness_score_raw"])
