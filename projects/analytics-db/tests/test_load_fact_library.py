from student_behavior_analytics_db.load_fact_library import load_fact_library


def test_load_library_visits_maps_cardld_and_visit_time():
    df = load_fact_library(
        [
            {
                "cardld": " pjxyqwbk736 ",
                "visittime": "2023-05-27 13:00:47",
                "type": "本科生",
                "dept": "网络与信息安全学院",
                "gateno": 7,
                "direction": 1,
                "source_file": "图书馆打卡记录.xlsx",
                "source_row_hash": "library-1",
            }
        ],
        terms=[
            {
                "term_key": "2022-2",
                "start_date": "2023-02-01",
                "end_date": "2023-06-30",
            }
        ],
    )

    assert df.to_dict(orient="records") == [
        {
            "student_id": "pjxyqwbk736",
            "term_key": "2022-2",
            "visited_at": "2023-05-27 13:00:47",
            "visit_date": "2023-05-27",
            "source_file": "图书馆打卡记录.xlsx",
            "source_row_hash": "library-1",
        }
    ]


def test_load_library_visits_drops_rows_without_term_calendar():
    df = load_fact_library(
        [
            {
                "cardld": "pjxyqwbk736",
                "visittime": "2023-05-27 13:00:47",
                "source_file": "图书馆打卡记录.xlsx",
                "source_row_hash": "library-raw-1",
            }
        ]
    )

    assert df.to_dict(orient="records") == []
