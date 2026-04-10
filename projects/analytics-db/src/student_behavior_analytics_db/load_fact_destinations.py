from __future__ import annotations

from typing import Any

import pandas as pd

from .normalize_ids import normalize_student_id

_DESTINATION_COLUMNS = (
    "student_id",
    "graduate_year",
    "destination_label",
    "destination_source",
    "destination_code_raw",
    "destination_name_raw",
    "employer_property_code_raw",
    "employer_property_name_raw",
    "industry_code_raw",
    "industry_name_raw",
    "source_file",
    "source_row_hash",
)

_STUDENT_ID_KEYS = ("student_id", "SID", "XH", "XSBH", "LOGIN_NAME", "USERNUM")
_GRADUATE_YEAR_KEYS = ("graduate_year", "GRADUATE_YEAR", "BYNF")
_PUBLIC_SECTOR_EMPLOYER_CODES = {
    "01",  # 高等教育单位（repo workbook taxonomy）
    "21",  # 党政机关
    "22",  # 科研设计单位
    "23",  # 高等教育单位
    "24",  # 中初教育单位
    "25",  # 医疗卫生单位
    "26",  # 其他事业单位
    "28",  # 部队
}


def load_fact_destinations(rows: list[dict[str, Any]]) -> pd.DataFrame:
    records = []
    for row in rows:
        student_id = _pick_student_id(row)
        graduate_year = _normalize_number(_first_value(row, *_GRADUATE_YEAR_KEYS))
        destination_code = _normalize_text(_first_value(row, "destination_code", "BYQX"))
        destination_name = _normalize_text(_first_value(row, "destination_name", "BYQXMC"))
        employer_property_code = _normalize_text(_first_value(row, "employer_property_code", "DWXZ"))
        employer_property_name = _normalize_text(_first_value(row, "employer_property_name", "DWXZMC"))
        source_file = _normalize_text(_first_value(row, "source_file"))
        source_row_hash = _normalize_text(_first_value(row, "source_row_hash", "row_hash"))
        if (
            student_id is None
            or graduate_year is None
            or destination_code is None
            or destination_name is None
            or source_file is None
            or source_row_hash is None
        ):
            continue

        destination_label, destination_source = _classify_destination(
            destination_code=destination_code,
            destination_name=destination_name,
            employer_property_code=employer_property_code,
            employer_property_name=employer_property_name,
        )
        records.append(
            {
                "student_id": student_id,
                "graduate_year": graduate_year,
                "destination_label": destination_label,
                "destination_source": destination_source,
                "destination_code_raw": destination_code,
                "destination_name_raw": destination_name,
                "employer_property_code_raw": employer_property_code,
                "employer_property_name_raw": employer_property_name,
                "industry_code_raw": _normalize_text(_first_value(row, "industry_code", "DWHY")),
                "industry_name_raw": _normalize_text(_first_value(row, "industry_name", "DWHYMC")),
                "source_file": source_file,
                "source_row_hash": source_row_hash,
            }
        )

    return _as_frame(records, _DESTINATION_COLUMNS)


def _pick_student_id(row: dict[str, Any]) -> str | None:
    for key in _STUDENT_ID_KEYS:
        student_id = normalize_student_id(row.get(key))
        if student_id is not None:
            return student_id
    return None


def _classify_destination(
    *,
    destination_code: str,
    destination_name: str,
    employer_property_code: str | None,
    employer_property_name: str | None,
) -> tuple[str, str]:
    if _contains_study_keyword(destination_code, destination_name):
        return "升学", "byqx_study"
    if _contains_abroad_keyword(destination_code, destination_name):
        return "出国出境", "byqx_abroad"
    if _contains_public_sector_keyword(destination_code, destination_name):
        return "体制内", "byqx_public_sector"
    if _contains_pending_keyword(destination_code, destination_name):
        return "待定其他", "byqx_pending_other"
    if _is_employment_like(destination_code, destination_name) and _is_public_sector_employer(
        employer_property_code,
        employer_property_name,
    ):
        return "体制内", "dwxz_public_sector"
    if _is_employment_like(destination_code, destination_name):
        return "企业就业", "byqx_employment"
    return "待定其他", "byqx_pending_other"


def _contains_study_keyword(code: str, name: str) -> bool:
    text = f"{code} {name}"
    return any(keyword in text for keyword in ("升学", "读研", "考研", "硕士", "博士", "专升本", "继续深造"))


def _contains_abroad_keyword(code: str, name: str) -> bool:
    text = f"{code} {name}"
    return any(keyword in text for keyword in ("出国", "出境", "留学", "境外"))


def _contains_public_sector_keyword(code: str, name: str) -> bool:
    text = f"{code} {name}"
    return any(keyword in text for keyword in ("国家基层项目", "地方基层项目", "公务员", "选调", "事业单位", "部队", "军队"))


def _contains_pending_keyword(code: str, name: str) -> bool:
    text = f"{code} {name}"
    return any(keyword in text for keyword in ("待就业", "暂不就业", "求职中", "拟升学", "拟考公", "拟创业", "其他暂不就业"))


def _is_employment_like(code: str, name: str) -> bool:
    text = f"{code} {name}"
    return any(
        keyword in text
        for keyword in (
            "签就业协议",
            "签劳动合同",
            "就业",
            "单位就业",
            "企业",
            "自主创业",
            "自由职业",
            "灵活就业",
        )
    )


def _is_public_sector_employer(code: str | None, name: str | None) -> bool:
    if code is not None and code in _PUBLIC_SECTOR_EMPLOYER_CODES:
        return True
    text = " ".join(value for value in (code, name) if value)
    return any(
        keyword in text
        for keyword in (
            "党政机关",
            "机关",
            "事业单位",
            "科研设计单位",
            "高等教育单位",
            "中初教育单位",
            "中等初等教育单位",
            "医疗卫生单位",
            "部队",
            "军队",
        )
    )


def _first_value(row: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key not in row:
            continue
        value = row.get(key)
        if value is None or isinstance(value, bool):
            continue
        if isinstance(value, float) and value != value:
            continue
        if isinstance(value, str):
            text = value.strip()
            if text:
                return text
            continue
        return value
    return None


def _normalize_text(raw: Any) -> str | None:
    if raw is None or isinstance(raw, bool):
        return None
    if isinstance(raw, float) and raw != raw:
        return None
    text = str(raw).strip()
    return text or None


def _normalize_number(raw: Any) -> int | None:
    if raw is None or isinstance(raw, bool):
        return None
    if isinstance(raw, float) and raw != raw:
        return None
    if isinstance(raw, int):
        return raw
    if isinstance(raw, float):
        return int(raw) if raw.is_integer() else None
    text = str(raw).strip()
    if not text:
        return None
    try:
        number = float(text)
    except ValueError:
        return None
    return int(number) if number.is_integer() else None


def _as_frame(records: list[dict[str, Any]], columns: tuple[str, ...]) -> pd.DataFrame:
    if not records:
        return pd.DataFrame(columns=columns)
    frame = pd.DataFrame(records, columns=columns)
    return frame.astype(object).where(pd.notna(frame), None)
