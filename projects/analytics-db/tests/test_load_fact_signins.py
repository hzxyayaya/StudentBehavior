from student_behavior_analytics_db.load_fact_signins import load_fact_signins


def test_load_signin_events_maps_real_source_rows_with_term_calendar():
    df = load_fact_signins(
        [
            {
                "LOGIN_NAME": " pjxyqxbj337 ",
                "ATTEND_TIME": 1602642284000,
                "INSERT_TIME": "2020-11-21 04:02:00",
                "source_file": "学生签到记录.xlsx",
                "source_row_hash": "signin-1",
            },
            {
                "LOGIN_NAME": "stu-2",
                "ATTEND_TIME": "1602642291000",
                "INSERT_TIME": "2020-11-21 04:02:00",
                "source_file": "学生签到记录.xlsx",
                "source_row_hash": "signin-2",
            },
        ],
        terms=[
            {
                "term_key": "2020-1",
                "start_date": "2020-09-01",
                "end_date": "2021-01-15",
            }
        ],
    )

    assert df.to_dict(orient="records") == [
        {
            "student_id": "pjxyqxbj337",
            "term_key": "2020-1",
            "signed_in_at": "2020-10-14 02:24:44",
            "source_file": "学生签到记录.xlsx",
            "source_row_hash": "signin-1",
        },
        {
            "student_id": "stu-2",
            "term_key": "2020-1",
            "signed_in_at": "2020-10-14 02:24:51",
            "source_file": "学生签到记录.xlsx",
            "source_row_hash": "signin-2",
        },
    ]


def test_load_signin_events_drops_rows_without_term_calendar():
    df = load_fact_signins(
        [
            {
                "LOGIN_NAME": "pjxyqxbj337",
                "ATTEND_TIME": 1602642284000,
                "source_file": "学生签到记录.xlsx",
                "source_row_hash": "signin-1",
            }
        ]
    )

    assert df.to_dict(orient="records") == []
