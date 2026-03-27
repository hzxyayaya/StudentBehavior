from student_behavior_analytics_db.load_students import load_students


def test_load_students_keeps_minimal_profile_columns():
    df = load_students(
        [
            {
                "XH": " pjxyqxbj337 ",
                "gender": "男",
                "ethnicity": "汉族",
                "political_status": "共青团员",
                "major_name": "软件工程",
                "college_name": "计算机学院",
                "class_name": "软件2401",
                "enrollment_year": 2024,
                "ignored": "drop",
            }
        ]
    )

    assert df.to_dict(orient="records") == [
        {
            "student_id": "pjxyqxbj337",
            "gender": "男",
            "ethnicity": "汉族",
            "political_status": "共青团员",
            "major_name": "软件工程",
            "college_name": "计算机学院",
            "class_name": "软件2401",
            "enrollment_year": 2024,
        }
    ]

