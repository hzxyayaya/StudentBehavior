from student_behavior_analytics_db.normalize_ids import normalize_student_id


def test_normalize_student_id_strips_whitespace():
    assert normalize_student_id(" pjxyqxbj337 ") == "pjxyqxbj337"


def test_normalize_student_id_rejects_blank_values():
    assert normalize_student_id("   ") is None
