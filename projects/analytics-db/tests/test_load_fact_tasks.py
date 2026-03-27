from datetime import time

from student_behavior_analytics_db.load_fact_tasks import load_fact_tasks


def test_load_tasks_keeps_learning_activity_metrics():
    df = load_fact_tasks(
        [
            {
                "LOGIN_NAME": " pjxxxxbj986 ",
                "term_key": "2021-1",
                "USER_ID": 147061147,
                "USER_NAME": "同学|老师",
                "DEPARTMENT_NAME": "通信工程学院",
                "MAJOR_NAME": "通信工程",
                "CLASS_NAME": "2001911",
                "STATE": 0,
                "SCHOOL_YEAR": 2020,
                "COURSE_ID": 214279116,
                "COURSE_NAME": "学业指导",
                "JWCOURSE_ID": "TS000001",
                "CREATE_TIME": "2024-09-01 08:00:00",
                "COURSE_TYPE": 0,
                "COURSE_STATUS": 0,
                "COURSE_DELETE": 0,
                "CLAZZ_ID": 31296642,
                "CLAZZ_NAME": "教学班1",
                "CLAZZ_STATUS": 0,
                "CLAZZ_STATE": 1,
                "JOB_NUM": 3,
                "JOB_RATE": 0.75,
                "VIDEOJOB_NUM": 2,
                "VIDEOJOB_RATE": 0.5,
                "VIDEOJOB_TIME": 120,
                "TEST_NUM": 1,
                "TEST_RATE": 0.25,
                "TEST_AVGSCORE": 85,
                "WORK_NUM": 4,
                "WORK_RATE": 1.0,
                "WORK_AVGSCORE": 92,
                "EXAM_NUM": 1,
                "EXAM_RATE": 0.25,
                "EXAM_AVGSCORE": 88,
                "PV": 12,
                "SIGN_NUM": 6,
                "SIGN_RATE": 0.9,
                "COURSE_LIVE_TIME": 360,
                "SPECIAL_TIME": 45,
                "BBS_NUM": 7,
                "TOPIC_NUM": 2,
                "REPLY_NUM": 5,
                "POINTS": 18,
                "TASK_NUM": 9,
                "TASK_RATE": 0.8,
                "UPDATE_TIME": "2024-09-01 08:10:00",
                "INSERT_TIME": "2024-09-01 08:11:00",
                "source_file": "课堂任务参与.xlsx",
                "source_row_hash": "task-1",
            },
            {
                "LOGIN_NAME": "missing",
                "source_file": "课堂任务参与.xlsx",
                "source_row_hash": "task-2",
            },
        ]
    )

    assert df.to_dict(orient="records") == [
        {
            "student_id": "pjxxxxbj986",
            "term_key": "2021-1",
            "user_id": 147061147,
            "user_name": "同学|老师",
            "department_name": "通信工程学院",
            "major_name": "通信工程",
            "class_name": "2001911",
            "state": 0,
            "school_year": 2020,
            "course_id": 214279116,
            "course_name": "学业指导",
            "jwcourse_id": "TS000001",
            "created_at": "2024-09-01 08:00:00",
            "course_type": 0,
            "course_status": 0,
            "course_delete": 0,
            "clazz_id": 31296642,
            "clazz_name": "教学班1",
            "clazz_status": 0,
            "clazz_state": 1,
            "job_num": 3,
            "job_rate": 0.75,
            "videojob_num": 2,
            "videojob_rate": 0.5,
            "videojob_time": 120,
            "test_num": 1,
            "test_rate": 0.25,
            "test_avgscore": 85,
            "work_num": 4,
            "work_rate": 1.0,
            "work_avgscore": 92,
            "exam_num": 1,
            "exam_rate": 0.25,
            "exam_avgscore": 88,
            "pv": 12,
            "sign_num": 6,
            "sign_rate": 0.9,
            "course_live_time": 360,
            "special_time": 45,
            "bbs_num": 7,
            "topic_num": 2,
            "reply_num": 5,
            "points": 18,
            "task_num": 9,
            "task_rate": 0.8,
            "updated_at": "2024-09-01 08:10:00",
            "inserted_at": "2024-09-01 08:11:00",
            "source_file": "课堂任务参与.xlsx",
            "source_row_hash": "task-1",
        }
    ]


def test_load_tasks_drops_raw_time_only_source_rows():
    df = load_fact_tasks(
        [
            {
                "LOGIN_NAME": "pjxxxxbj986",
                "CREATE_TIME": time(0, 47, 32),
                "INSERT_TIME": time(0, 41, 31),
                "source_file": "课堂任务参与.xlsx",
                "source_row_hash": "task-raw-1",
            }
        ]
    )

    assert df.to_dict(orient="records") == []
