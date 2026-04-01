from student_behavior_analytics_db.load_fact_attendance import load_fact_attendance


def test_load_attendance_records_maps_xn_xq_to_term_key():
    df = load_fact_attendance(
        [
            {
                "XH": " pjxyqxbj337 ",
                "XN": "2024-2025",
                "XQ": 1,
                "attendance_status": "present",
                "attended_at": "2024-09-02",
                "source_file": "考勤汇总.xlsx",
                "source_row_hash": "attendance-1",
            }
        ]
    )

    assert df.to_dict(orient="records") == [
        {
            "student_id": "pjxyqxbj337",
            "term_key": "2024-1",
            "attendance_status": "present",
            "attended_at": "2024-09-02",
            "source_file": "考勤汇总.xlsx",
            "source_row_hash": "attendance-1",
        }
    ]


def test_load_attendance_records_supports_real_excel_columns():
    df = load_fact_attendance(
        [
            {
                "XH": " pjxyqxbj337 ",
                "XN": "2024-2025",
                "XQ": 1,
                "ZT": "正常",
                "DKSJ": "2024-09-02 08:01:00",
                "source_file": "考勤汇总.xlsx",
                "source_row_hash": "attendance-real-1",
            }
        ]
    )

    assert df.to_dict(orient="records") == [
        {
            "student_id": "pjxyqxbj337",
            "term_key": "2024-1",
            "attendance_status": "正常",
            "attended_at": "2024-09-02 08:01:00",
            "source_file": "考勤汇总.xlsx",
            "source_row_hash": "attendance-real-1",
        }
    ]
