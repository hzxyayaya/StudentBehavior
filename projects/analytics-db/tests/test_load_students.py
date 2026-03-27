from student_behavior_analytics_db.load_students import load_students


def test_load_students_deduplicates_and_supports_realistic_aliases():
    df = load_students(
        [
            {
                "学号": " pjxyqxbj337 ",
                "性别": "男",
                "民族": "汉族",
                "政治面貌": "共青团员",
                "专业名称": "软件工程",
                "学院名称": "计算机学院",
                "班级名称": "软件2401",
                "入学年份": "2024",
                "备注": "drop",
            },
            {
                "student_id": "pjxyqxbj337",
                "gender": "女",
                "ethnicity": "满族",
                "political_status": "群众",
                "major_name": "网络工程",
                "college_name": "信息学院",
                "class_name": "软件2402",
                "enrollment_year": 2025,
            },
            {
                "学号": None,
                "性别": "女",
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


def test_load_students_skips_missing_student_ids():
    df = load_students(
        [
            {
                "性别": "女",
                "民族": "汉族",
            }
        ]
    )

    assert df.to_dict(orient="records") == []
