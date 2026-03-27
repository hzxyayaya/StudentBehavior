from student_behavior_analytics_db.load_fact_enrollments import load_fact_enrollments
from student_behavior_analytics_db.load_fact_grades import load_fact_grades


def test_load_enrollments_normalizes_student_id_and_term_key():
    df = load_fact_enrollments(
        [
            {
                "XH": " pjxyqxbj337 ",
                "XN": "2024-2025",
                "XQ": "1",
                "course_id": "C-101",
                "course_code": "CS101",
                "course_name": "Data Structures",
                "source_file": "学生选课信息.xlsx",
                "source_row_hash": "enrollment-1",
            }
        ]
    )

    assert df.to_dict(orient="records") == [
        {
            "student_id": "pjxyqxbj337",
            "term_key": "2024-1",
            "course_id": "C-101",
            "course_code": "CS101",
            "course_name": "Data Structures",
            "source_file": "学生选课信息.xlsx",
            "source_row_hash": "enrollment-1",
        }
    ]


def test_load_grade_records_preserves_score_and_gpa_fields():
    df = load_fact_grades(
        [
            {
                "student_id": " pjxyqxbj337 ",
                "XN": "2024-2025",
                "XQ": 2,
                "course_id": "C-201",
                "course_name": "Algorithms",
                "score": 86.5,
                "gpa": 3.75,
                "passed": True,
                "source_file": "学生成绩.xlsx",
                "source_row_hash": "grade-1",
            }
        ]
    )

    assert df.to_dict(orient="records") == [
        {
            "student_id": "pjxyqxbj337",
            "term_key": "2024-2",
            "course_id": "C-201",
            "course_name": "Algorithms",
            "score": 86.5,
            "gpa": 3.75,
            "passed": True,
            "source_file": "学生成绩.xlsx",
            "source_row_hash": "grade-1",
        }
    ]
