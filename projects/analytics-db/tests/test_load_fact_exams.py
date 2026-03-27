from datetime import time

from student_behavior_analytics_db.load_fact_exams import load_fact_exams


def test_load_exams_keeps_submission_events_and_term_alias():
    df = load_fact_exams(
        [
            {
                "CREATER_LOGIN_NAME": " pjxuqwbj750 ",
                "学年学期": "2024-2025学年第2学期",
                "WORK_ID": 20595439,
                "WORK_TITLE": "劳动的未来",
                "COURSE_ID": 225379960,
                "COURSE_NAME": "大学生劳动教育理论在线课程",
                "STATUS": 4,
                "FULLMARKS": 100,
                "SCORE": 100,
                "TYPE": 3,
                "ANSWER_TIME": "2024-12-01 09:05:00",
                "INSERT_TIME": "2024-12-01 09:06:00",
                "source_file": "考试提交记录.xlsx",
                "source_row_hash": "exam-1",
            },
            {
                "CREATER_LOGIN_NAME": "missing",
                "source_file": "考试提交记录.xlsx",
                "source_row_hash": "exam-2",
            },
        ]
    )

    assert df.to_dict(orient="records") == [
            {
                "student_id": "pjxuqwbj750",
                "term_key": "2024-2",
                "work_id": 20595439,
                "work_title": "劳动的未来",
            "course_id": 225379960,
            "course_name": "大学生劳动教育理论在线课程",
            "status": 4,
            "fullmarks": 100,
                "score": 100,
                "type": 3,
                "submitted_at": "2024-12-01 09:05:00",
                "reviewed_at": None,
                "updated_at": None,
                "inserted_at": "2024-12-01 09:06:00",
                "source_file": "考试提交记录.xlsx",
                "source_row_hash": "exam-1",
            }
    ]


def test_load_exams_drops_raw_time_only_source_rows():
    df = load_fact_exams(
        [
            {
                "CREATER_LOGIN_NAME": "pjxuqwbj750",
                "ANSWER_TIME": time(0, 10, 32),
                "INSERT_TIME": time(0, 5, 25),
                "source_file": "考试提交记录.xlsx",
                "source_row_hash": "exam-raw-1",
            }
        ]
    )

    assert df.to_dict(orient="records") == []
