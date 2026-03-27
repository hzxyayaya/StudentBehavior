import pandas as pd

from student_behavior_analytics_db.build_student_term_features import (
    build_student_term_features,
)


def test_build_student_term_features_outputs_expected_columns_and_metrics():
    features = build_student_term_features(
        students=pd.DataFrame(
            [
                {
                    "student_id": "stu-1",
                    "major_name": "软件工程",
                    "college_name": "计算机学院",
                }
            ]
        ),
        grades=pd.DataFrame(
            [
                {
                    "student_id": "stu-1",
                    "term_key": "2024-1",
                    "score": 90,
                    "gpa": 3.8,
                    "passed": True,
                },
                {
                    "student_id": "stu-1",
                    "term_key": "2024-1",
                    "score": 60,
                    "gpa": 2.0,
                    "passed": False,
                },
            ]
        ),
        attendance=pd.DataFrame(
            [
                {
                    "student_id": "stu-1",
                    "term_key": "2024-1",
                    "attendance_status": "present",
                    "attended_at": "2024-09-02 08:00:00",
                },
                {
                    "student_id": "stu-1",
                    "term_key": "2024-1",
                    "attendance_status": "absent",
                    "attended_at": "2024-09-03 08:00:00",
                },
            ]
        ),
        enrollments=pd.DataFrame(
            [
                {"student_id": "stu-1", "term_key": "2024-1", "course_id": "C-1"},
                {"student_id": "stu-1", "term_key": "2024-1", "course_id": "C-2"},
            ]
        ),
        signins=pd.DataFrame(
            [
                {"student_id": "stu-1", "term_key": "2024-1", "signed_in_at": "2024-09-02 08:00:00"},
                {"student_id": "stu-1", "term_key": "2024-1", "signed_in_at": "2024-09-03 08:00:00"},
            ]
        ),
        assignments=pd.DataFrame(
            [
                {"student_id": "stu-1", "term_key": "2024-1", "work_id": 1},
                {"student_id": "stu-1", "term_key": "2024-1", "work_id": 2},
            ]
        ),
        exams=pd.DataFrame(
            [
                {"student_id": "stu-1", "term_key": "2024-1", "work_id": 10},
            ]
        ),
        tasks=pd.DataFrame(
            [
                {"student_id": "stu-1", "term_key": "2024-1", "task_rate": 0.8},
            ]
        ),
        discussions=pd.DataFrame(
            [
                {"student_id": "stu-1", "term_key": "2024-1", "reply_content": "hello"},
                {"student_id": "stu-1", "term_key": "2024-1", "reply_content": "world"},
            ]
        ),
        library=pd.DataFrame(
            [
                {"student_id": "stu-1", "term_key": "2024-1", "visited_at": "2024-09-02 08:00:00", "visit_date": "2024-09-02"},
                {"student_id": "stu-1", "term_key": "2024-1", "visited_at": "2024-09-02 09:00:00", "visit_date": "2024-09-02"},
                {"student_id": "stu-1", "term_key": "2024-1", "visited_at": "2024-09-03 10:00:00", "visit_date": "2024-09-03"},
            ]
        ),
        running=pd.DataFrame(
            [
                {"student_id": "stu-1", "term_key": "2024-1", "ran_at": "2024-09-02 06:30:00", "run_date": "2024-09-02"},
                {"student_id": "stu-1", "term_key": "2024-1", "ran_at": "2024-09-02 07:30:00", "run_date": "2024-09-02"},
            ]
        ),
    )

    assert set(features.columns) == {
        "student_id",
        "term_key",
        "major_name",
        "college_name",
        "avg_course_score",
        "failed_course_count",
        "avg_gpa",
        "major_rank_pct",
        "risk_label",
        "attendance_record_count",
        "attendance_normal_rate",
        "selected_course_count",
        "sign_event_count",
        "assignment_submit_count",
        "exam_submit_count",
        "task_participation_rate",
        "discussion_reply_count",
        "library_visit_count",
        "library_active_days",
        "running_punch_count",
        "morning_activity_rate",
    }

    assert features.to_dict(orient="records") == [
        {
            "student_id": "stu-1",
            "term_key": "2024-1",
            "major_name": "软件工程",
            "college_name": "计算机学院",
            "avg_course_score": 75.0,
            "failed_course_count": 1,
            "avg_gpa": 2.9,
            "major_rank_pct": None,
            "risk_label": None,
            "attendance_record_count": 2,
            "attendance_normal_rate": 0.5,
            "selected_course_count": 2,
            "sign_event_count": 2,
            "assignment_submit_count": 2,
            "exam_submit_count": 1,
            "task_participation_rate": 0.8,
            "discussion_reply_count": 2,
            "library_visit_count": 3,
            "library_active_days": 2,
            "running_punch_count": 2,
            "morning_activity_rate": 0.5,
        }
    ]


def test_build_student_term_features_keeps_draft_source_metrics_null_when_inputs_are_empty():
    features = build_student_term_features(
        students=pd.DataFrame(
            [
                {
                    "student_id": "stu-1",
                    "major_name": "软件工程",
                    "college_name": "计算机学院",
                }
            ]
        ),
        grades=pd.DataFrame(
            [
                {
                    "student_id": "stu-1",
                    "term_key": "2024-1",
                    "score": 90,
                    "gpa": 3.8,
                    "passed": True,
                }
            ]
        ),
        attendance=pd.DataFrame(
            [
                {
                    "student_id": "stu-1",
                    "term_key": "2024-1",
                    "attendance_status": "present",
                    "attended_at": "2024-09-02 08:00:00",
                }
            ]
        ),
        enrollments=pd.DataFrame(
            [
                {"student_id": "stu-1", "term_key": "2024-1", "course_id": "C-1"},
            ]
        ),
        signins=pd.DataFrame(columns=["student_id", "term_key", "signed_in_at"]),
        assignments=pd.DataFrame(columns=["student_id", "term_key", "work_id"]),
        exams=pd.DataFrame(columns=["student_id", "term_key", "work_id"]),
        tasks=pd.DataFrame(columns=["student_id", "term_key", "task_rate"]),
        discussions=pd.DataFrame(columns=["student_id", "term_key", "reply_content"]),
        library=pd.DataFrame(columns=["student_id", "term_key", "visited_at", "visit_date"]),
        running=pd.DataFrame(columns=["student_id", "term_key", "ran_at", "run_date"]),
    )

    assert features.to_dict(orient="records") == [
        {
            "student_id": "stu-1",
            "term_key": "2024-1",
            "major_name": "软件工程",
            "college_name": "计算机学院",
            "avg_course_score": 90.0,
            "failed_course_count": 0,
            "avg_gpa": 3.8,
            "major_rank_pct": None,
            "risk_label": None,
            "attendance_record_count": 1,
            "attendance_normal_rate": 1.0,
            "selected_course_count": 1,
            "sign_event_count": None,
            "assignment_submit_count": None,
            "exam_submit_count": None,
            "task_participation_rate": None,
            "discussion_reply_count": None,
            "library_visit_count": None,
            "library_active_days": None,
            "running_punch_count": None,
            "morning_activity_rate": None,
        }
    ]
