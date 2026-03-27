from student_behavior_analytics_db.load_fact_evaluation_labels import (
    load_fact_evaluation_labels,
)


def test_load_evaluation_labels_builds_risk_label_from_frozen_rule():
    df = load_fact_evaluation_labels(
        [
            {
                "XH": " pjxyqxbj337 ",
                "XN": "2024-2025",
                "XQ": "1",
                "CPXQ": "1",
                "ZYNJPM": 80,
                "ZYNJRS": 100,
                "source_file": "本科生综合测评.xlsx",
                "source_row_hash": "label-1",
            },
            {
                "XH": "stu-2",
                "XN": "2024-2025",
                "XQ": "2",
                "CPXQ": "2",
                "ZYNJPM": 79,
                "ZYNJRS": 100,
                "source_file": "本科生综合测评.xlsx",
                "source_row_hash": "label-2",
            },
            {
                "XH": "stu-3",
                "XN": "2024-2025",
                "CPXQ": "9",
                "ZYNJPM": 90,
                "ZYNJRS": 100,
                "source_file": "本科生综合测评.xlsx",
                "source_row_hash": "label-3",
            },
        ]
    )

    assert df.to_dict(orient="records") == [
        {
            "student_id": "pjxyqxbj337",
            "term_key": "2024-1",
            "risk_label": 1,
            "evaluation_source": "supervised_term_1",
            "source_file": "本科生综合测评.xlsx",
            "source_row_hash": "label-1",
        },
        {
            "student_id": "stu-2",
            "term_key": "2024-2",
            "risk_label": 0,
            "evaluation_source": "supervised_term_2",
            "source_file": "本科生综合测评.xlsx",
            "source_row_hash": "label-2",
        },
        {
            "student_id": "stu-3",
            "term_key": "annual_or_unknown_term",
            "risk_label": 1,
            "evaluation_source": "annual_or_unknown_term",
            "source_file": "本科生综合测评.xlsx",
            "source_row_hash": "label-3",
        },
    ]
