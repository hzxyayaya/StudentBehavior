from student_behavior_analytics_db.load_terms import load_terms


def test_load_terms_builds_term_rows_from_known_school_year_formats():
    df = load_terms(
        [
            {"term_name": "2020-2021学年第1学期"},
            {"school_year": "2024-2025", "term_no": 2},
        ]
    )

    assert df.to_dict(orient="records") == [
        {
            "term_key": "2020-1",
            "school_year": "2020-2021",
            "term_no": 1,
            "term_name": "2020-2021学年第1学期",
            "start_date": None,
            "end_date": None,
            "is_analysis_term": True,
        },
        {
            "term_key": "2024-2",
            "school_year": "2024-2025",
            "term_no": 2,
            "term_name": "2024-2025学年第2学期",
            "start_date": None,
            "end_date": None,
            "is_analysis_term": True,
        },
    ]

