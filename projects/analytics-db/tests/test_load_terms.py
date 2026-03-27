from student_behavior_analytics_db.load_terms import load_terms


def test_load_terms_deduplicates_and_supports_realistic_aliases():
    df = load_terms(
        [
            {
                "学年学期": "2020-2021学年第1学期",
                "起始日期": "2020-09-01",
                "结束日期": "2021-01-15",
                "是否分析学期": "是",
            },
            {
                "XN": "2020-2021",
                "XQ": 1,
                "term_name": "重复学期行",
                "start_date": "2020-09-02",
                "end_date": "2021-01-16",
            },
            {
                "开课学年": "2024-2025",
                "开课学期": "2",
            },
            {
                "学年": "2023-2024",
            },
        ]
    )

    assert df.to_dict(orient="records") == [
        {
            "term_key": "2020-1",
            "school_year": "2020-2021",
            "term_no": 1,
            "term_name": "2020-2021学年第1学期",
            "start_date": "2020-09-01",
            "end_date": "2021-01-15",
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


def test_load_terms_skips_missing_and_invalid_rows():
    df = load_terms(
        [
            {"学年": "2023-2024"},
            {"学年学期": "2023-2025学年第1学期"},
        ]
    )

    assert df.to_dict(orient="records") == []
