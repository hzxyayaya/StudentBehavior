from student_behavior_analytics_db.load_fact_running import load_fact_running


def test_load_running_events_maps_usernum_and_run_time():
    df = load_fact_running(
        [
            {
                "USERNUM": " pjxyqxbj795 ",
                "TERM_ID": 9,
                "PUNCH_DAY": "2020-09-25",
                "PUNCH_TIME": "06:25:06",
                "MACHINE_ID": 13,
                "STATE": 5,
                "source_file": "跑步打卡.xlsx",
                "source_row_hash": "running-1",
            }
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
            "student_id": "pjxyqxbj795",
            "term_key": "2020-1",
            "ran_at": "2020-09-25 06:25:06",
            "run_date": "2020-09-25",
            "distance_km": None,
            "source_file": "跑步打卡.xlsx",
            "source_row_hash": "running-1",
        }
    ]


def test_load_running_events_infer_term_without_term_calendar():
    df = load_fact_running(
        [
            {
                "USERNUM": "pjxyqxbj795",
                "TERM_ID": 9,
                "PUNCH_DAY": "2020-09-25",
                "PUNCH_TIME": "06:25:06",
                "source_file": "跑步打卡.xlsx",
                "source_row_hash": "running-raw-1",
            }
        ]
    )

    assert df.to_dict(orient="records") == [
        {
            "student_id": "pjxyqxbj795",
            "term_key": "2020-1",
            "ran_at": "2020-09-25 06:25:06",
            "run_date": "2020-09-25",
            "distance_km": None,
            "source_file": "跑步打卡.xlsx",
            "source_row_hash": "running-raw-1",
        }
    ]
