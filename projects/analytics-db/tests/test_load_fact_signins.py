from student_behavior_analytics_db.load_fact_signins import load_fact_signins


def test_load_signin_events_uses_deterministic_timestamp_mapping_only():
    df = load_fact_signins(
        [
            {
                "XH": " pjxyqxbj337 ",
                "term_key": "2024-2",
                "signed_in_at": "2024-10-08 08:15:00",
                "source_file": "学生签到记录.xlsx",
                "source_row_hash": "signin-1",
            },
            {
                "XH": "stu-2",
                "signed_in_at": "2024-10-08 08:30:00",
                "source_file": "学生签到记录.xlsx",
                "source_row_hash": "signin-2",
            },
        ]
    )

    assert df.to_dict(orient="records") == [
        {
            "student_id": "pjxyqxbj337",
            "term_key": "2024-2",
            "signed_in_at": "2024-10-08 08:15:00",
            "source_file": "学生签到记录.xlsx",
            "source_row_hash": "signin-1",
        }
    ]
