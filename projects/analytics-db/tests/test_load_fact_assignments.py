from student_behavior_analytics_db.load_fact_assignments import load_fact_assignments


def test_load_assignments_keeps_submit_events():
    df = load_fact_assignments(
        [
            {
                "CREATER_LOGIN_NAME": " pjxyqwbk736 ",
                "term_key": "2024-1",
                "WORK_ID": 29193512,
                "WORK_TITLE": "劳动教育大作业",
                "COURSE_ID": 225579931,
                "COURSE_NAME": "劳动教育",
                "STATUS": 3,
                "FULLMARKS": 100,
                "SCORE": 88,
                "TYPE": 1,
                "ANSWER_TIME": "2024-10-14 08:15:00",
                "INSERT_TIME": "2024-10-14 08:16:00",
                "source_file": "学生作业提交记录.xlsx",
                "source_row_hash": "assignment-1",
            },
            {
                "WORK_ID": 1,
                "source_file": "学生作业提交记录.xlsx",
                "source_row_hash": "assignment-2",
            },
        ]
    )

    assert df.to_dict(orient="records") == [
            {
                "student_id": "pjxyqwbk736",
                "term_key": "2024-1",
                "work_id": 29193512,
                "work_title": "劳动教育大作业",
            "course_id": 225579931,
            "course_name": "劳动教育",
            "status": 3,
            "fullmarks": 100,
                "score": 88,
                "type": 1,
                "submitted_at": "2024-10-14 08:15:00",
                "reviewed_at": None,
                "updated_at": None,
                "inserted_at": "2024-10-14 08:16:00",
                "source_file": "学生作业提交记录.xlsx",
                "source_row_hash": "assignment-1",
            }
    ]
