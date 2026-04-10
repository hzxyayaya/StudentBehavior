from student_behavior_analytics_db.load_fact_destinations import load_fact_destinations


def test_load_fact_destinations_normalizes_student_ids_labels_and_preserves_raw_fields():
    df = load_fact_destinations(
        [
            {
                "SID": " pjxyqxbj337 ",
                "GRADUATE_YEAR": "2025",
                "BYQX": "10",
                "BYQXMC": "国内升学",
                "DWXZ": "01",
                "DWXZMC": "高等教育单位",
                "DWHY": "P",
                "DWHYMC": "教育",
                "source_file": "毕业去向.xlsx",
                "source_row_hash": "dest-1",
            },
            {
                "XSBH": "stu-2",
                "GRADUATE_YEAR": 2024,
                "BYQX": "46",
                "BYQXMC": "签就业协议形式就业",
                "DWXZ": "10",
                "DWXZMC": "民营企业",
                "DWHY": "I",
                "DWHYMC": "信息传输、软件和信息技术服务业",
                "source_file": "毕业去向.xlsx",
                "source_row_hash": "dest-2",
            },
            {
                "LOGIN_NAME": "stu-3",
                "GRADUATE_YEAR": "2024",
                "BYQX": "71",
                "BYQXMC": "国家基层项目",
                "source_file": "毕业去向.xlsx",
                "source_row_hash": "dest-3",
            },
            {
                "USERNUM": "stu-4",
                "GRADUATE_YEAR": "2024",
                "BYQX": "80",
                "BYQXMC": "出国、出境",
                "source_file": "毕业去向.xlsx",
                "source_row_hash": "dest-4",
            },
            {
                "student_id": "stu-5",
                "GRADUATE_YEAR": "2024",
                "BYQX": "99",
                "BYQXMC": "待就业",
                "source_file": "毕业去向.xlsx",
                "source_row_hash": "dest-5",
            },
        ]
    )

    assert df.to_dict(orient="records") == [
        {
            "student_id": "pjxyqxbj337",
            "graduate_year": 2025,
            "destination_label": "升学",
            "destination_source": "byqx_study",
            "destination_code_raw": "10",
            "destination_name_raw": "国内升学",
            "employer_property_code_raw": "01",
            "employer_property_name_raw": "高等教育单位",
            "industry_code_raw": "P",
            "industry_name_raw": "教育",
            "source_file": "毕业去向.xlsx",
            "source_row_hash": "dest-1",
        },
        {
            "student_id": "stu-2",
            "graduate_year": 2024,
            "destination_label": "企业就业",
            "destination_source": "byqx_employment",
            "destination_code_raw": "46",
            "destination_name_raw": "签就业协议形式就业",
            "employer_property_code_raw": "10",
            "employer_property_name_raw": "民营企业",
            "industry_code_raw": "I",
            "industry_name_raw": "信息传输、软件和信息技术服务业",
            "source_file": "毕业去向.xlsx",
            "source_row_hash": "dest-2",
        },
        {
            "student_id": "stu-3",
            "graduate_year": 2024,
            "destination_label": "体制内",
            "destination_source": "byqx_public_sector",
            "destination_code_raw": "71",
            "destination_name_raw": "国家基层项目",
            "employer_property_code_raw": None,
            "employer_property_name_raw": None,
            "industry_code_raw": None,
            "industry_name_raw": None,
            "source_file": "毕业去向.xlsx",
            "source_row_hash": "dest-3",
        },
        {
            "student_id": "stu-4",
            "graduate_year": 2024,
            "destination_label": "出国出境",
            "destination_source": "byqx_abroad",
            "destination_code_raw": "80",
            "destination_name_raw": "出国、出境",
            "employer_property_code_raw": None,
            "employer_property_name_raw": None,
            "industry_code_raw": None,
            "industry_name_raw": None,
            "source_file": "毕业去向.xlsx",
            "source_row_hash": "dest-4",
        },
        {
            "student_id": "stu-5",
            "graduate_year": 2024,
            "destination_label": "待定其他",
            "destination_source": "byqx_pending_other",
            "destination_code_raw": "99",
            "destination_name_raw": "待就业",
            "employer_property_code_raw": None,
            "employer_property_name_raw": None,
            "industry_code_raw": None,
            "industry_name_raw": None,
            "source_file": "毕业去向.xlsx",
            "source_row_hash": "dest-5",
        },
    ]


def test_load_fact_destinations_uses_employer_property_to_reclassify_public_sector_employment():
    df = load_fact_destinations(
        [
            {
                "SID": "stu-6",
                "GRADUATE_YEAR": 2025,
                "BYQX": "46",
                "BYQXMC": "签就业协议形式就业",
                "DWXZ": "21",
                "DWXZMC": "党政机关",
                "source_file": "毕业去向.xlsx",
                "source_row_hash": "dest-6",
            },
            {
                "SID": "stu-7",
                "GRADUATE_YEAR": 2025,
                "BYQX": "50",
                "BYQXMC": "单位就业",
                "DWXZMC": "科研设计单位",
                "source_file": "毕业去向.xlsx",
                "source_row_hash": "dest-7",
            },
        ]
    )

    assert df.loc[:, ["student_id", "destination_label", "destination_source"]].to_dict(orient="records") == [
        {
            "student_id": "stu-6",
            "destination_label": "体制内",
            "destination_source": "dwxz_public_sector",
        },
        {
            "student_id": "stu-7",
            "destination_label": "体制内",
            "destination_source": "dwxz_public_sector",
        },
    ]


def test_load_fact_destinations_uses_public_sector_dwxz_code_when_name_is_blank():
    df = load_fact_destinations(
        [
            {
                "SID": "stu-8",
                "GRADUATE_YEAR": 2025,
                "BYQX": "50",
                "BYQXMC": "单位就业",
                "DWXZ": "21",
                "DWXZMC": "",
                "source_file": "毕业去向.xlsx",
                "source_row_hash": "dest-8",
            }
        ]
    )

    assert df.loc[0, "destination_label"] == "体制内"
    assert df.loc[0, "destination_source"] == "dwxz_public_sector"


def test_load_fact_destinations_does_not_treat_generic_jiguan_text_as_public_sector_when_employer_is_private():
    df = load_fact_destinations(
        [
            {
                "SID": "stu-9",
                "GRADUATE_YEAR": 2025,
                "BYQX": "50",
                "BYQXMC": "单位就业（机关服务外包）",
                "DWXZ": "10",
                "DWXZMC": "民营企业",
                "source_file": "毕业去向.xlsx",
                "source_row_hash": "dest-9",
            }
        ]
    )

    assert df.loc[0, "destination_label"] == "企业就业"
    assert df.loc[0, "destination_source"] == "byqx_employment"


def test_load_fact_destinations_uses_repo_dwxz_code_01_when_name_is_blank():
    df = load_fact_destinations(
        [
            {
                "SID": "stu-10",
                "GRADUATE_YEAR": 2025,
                "BYQX": "50",
                "BYQXMC": "单位就业",
                "DWXZ": "01",
                "DWXZMC": "",
                "source_file": "毕业去向.xlsx",
                "source_row_hash": "dest-10",
            }
        ]
    )

    assert df.loc[0, "destination_label"] == "体制内"
    assert df.loc[0, "destination_source"] == "dwxz_public_sector"
