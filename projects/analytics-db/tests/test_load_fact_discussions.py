from student_behavior_analytics_db.load_fact_discussions import load_fact_discussions


def test_load_discussions_keeps_reply_events():
    df = load_fact_discussions(
        [
            {
                "REPLY_LOGIN_NAME": " pjxuqxbj759 ",
                "term_key": "2024-1",
                "COURSE_ID": 214279479,
                "COURSE_NAME": "思想道德修养与法律基础",
                "TOPIC_ID": 216076649,
                "TOPIC_TITLE": "专题五：你的梦想是什么？",
                "CREATER_ROLE": 1,
                "CREATER_NAME": "同学|老师",
                "REPLY_USER_NAME": "同学|老师",
                "REPLY_USER_ROLE": 3,
                "REPLY_CONTENT": "中国早日称霸",
                "ISDELETE": 0,
                "TOPIC_ISDELETE": 0,
                "CREATE_TIME": "2024-10-08 10:00:00",
                "INSERT_TIME": "2024-10-08 10:01:00",
                "source_file": "讨论记录.xlsx",
                "source_row_hash": "discussion-1",
            },
            {
                "COURSE_ID": 1,
                "source_file": "讨论记录.xlsx",
                "source_row_hash": "discussion-2",
            },
        ]
    )

    assert df.to_dict(orient="records") == [
        {
            "student_id": "pjxuqxbj759",
            "term_key": "2024-1",
            "course_id": 214279479,
            "course_name": "思想道德修养与法律基础",
            "topic_id": 216076649,
            "topic_title": "专题五：你的梦想是什么？",
            "creator_role": 1,
            "creator_name": "同学|老师",
            "reply_user_name": "同学|老师",
            "reply_user_role": 3,
            "reply_content": "中国早日称霸",
            "isdelete": 0,
            "topic_isdelete": 0,
            "created_at": "2024-10-08 10:00:00",
            "inserted_at": "2024-10-08 10:01:00",
            "source_file": "讨论记录.xlsx",
            "source_row_hash": "discussion-1",
        }
    ]
