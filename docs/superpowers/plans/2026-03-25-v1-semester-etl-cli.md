# V1 学期特征 ETL CLI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在隔离子项目 `projects/semester-etl` 中实现一个项目绑定型离线 ETL CLI，读取仓库根目录 `数据集及类型` 下的冻结源表，输出 `v1_semester_features.csv` 和 `v1_warnings.json`。

**Architecture:** 使用 `uv` 管理的最小 Python 包结构，并把代码工程隔离到 `projects/semester-etl` 目录；运行入口仍从仓库根目录触发。数据链路严格以 `考勤汇总.xlsx` 生成 `(student_id, term_key)` 基础行集，`学生基本信息.xlsx` 只做专业字段广播，`上网统计.xlsx` 在当前快照下按冻结规则整表降级并输出告警摘要。

**Tech Stack:** Python 3.12+, `uv`, `pandas`, `openpyxl`, `pytest`, 标准库 `argparse`, `dataclasses`, `json`, `pathlib`

---

## 实施前文件地图

### 需要创建的文件

- `C:\Users\Orion\Desktop\StudentBehavior\projects\semester-etl\pyproject.toml`
  - 定义项目元数据、依赖、测试依赖和 `semester-features` 命令入口
- `C:\Users\Orion\Desktop\StudentBehavior\projects\semester-etl\src\student_behavior_etl\__init__.py`
  - 包初始化
- `C:\Users\Orion\Desktop\StudentBehavior\projects\semester-etl\src\student_behavior_etl\config.py`
  - 固定项目路径、输出文件名、数据类配置
- `C:\Users\Orion\Desktop\StudentBehavior\projects\semester-etl\src\student_behavior_etl\normalize.py`
  - 学号清洗、`XN/XQ -> term_key` 归一化
- `C:\Users\Orion\Desktop\StudentBehavior\projects\semester-etl\src\student_behavior_etl\reporting.py`
  - warning 计数器、source status 和 JSON 输出
- `C:\Users\Orion\Desktop\StudentBehavior\projects\semester-etl\src\student_behavior_etl\io.py`
  - Excel 读取、必需列校验、临时文件过滤
- `C:\Users\Orion\Desktop\StudentBehavior\projects\semester-etl\src\student_behavior_etl\build_semester_features.py`
  - 聚合 `attendance_record_count`、补齐 `major_name`、网络源降级、生成最终 CSV DataFrame
- `C:\Users\Orion\Desktop\StudentBehavior\projects\semester-etl\src\student_behavior_etl\cli.py`
  - CLI 入口、`build` 子命令、终端摘要输出
- `C:\Users\Orion\Desktop\StudentBehavior\projects\semester-etl\tests\test_config.py`
  - 默认路径与输出文件名测试
- `C:\Users\Orion\Desktop\StudentBehavior\projects\semester-etl\tests\test_normalize.py`
  - 学号和学期键归一化测试
- `C:\Users\Orion\Desktop\StudentBehavior\projects\semester-etl\tests\test_reporting.py`
  - warning 结构和 reason key 测试
- `C:\Users\Orion\Desktop\StudentBehavior\projects\semester-etl\tests\test_build_semester_features.py`
  - 核心构建逻辑测试
- `C:\Users\Orion\Desktop\StudentBehavior\projects\semester-etl\tests\test_cli.py`
  - CLI 集成测试

### 目录与运行时产物

- `C:\Users\Orion\Desktop\StudentBehavior\projects\semester-etl\`
  - 隔离的 Python 工程根目录

- `C:\Users\Orion\Desktop\StudentBehavior\artifacts\semester_features\`
  - 运行时自动创建，不手动提交真实产物
- `C:\Users\Orion\Desktop\StudentBehavior\数据集及类型\`
  - 项目固定输入目录，不通过公共 CLI 参数覆盖

## 全局约束

- 全程遵守 TDD：先写失败测试，再写最小实现，再跑通过。
- 不新增公共路径参数；测试需要临时目录时，只能通过内部配置对象或 builder seam 注入。
- 不从 `TJNY` 反推学期。
- 不引入未冻结字段，不扩展到模型或后端任务。
- 所有最终输出行必须按 `(student_id, term_key)` 升序稳定排序。
- `学生基本信息.xlsx` 中若同一 `student_id` 出现多个不同 `ZYM`，必须 hard-fail。

### Task 1: 建立最小工程骨架与固定路径配置

**Files:**
- Create: `C:\Users\Orion\Desktop\StudentBehavior\projects\semester-etl\pyproject.toml`
- Create: `C:\Users\Orion\Desktop\StudentBehavior\projects\semester-etl\src\student_behavior_etl\__init__.py`
- Create: `C:\Users\Orion\Desktop\StudentBehavior\projects\semester-etl\src\student_behavior_etl\config.py`
- Create: `C:\Users\Orion\Desktop\StudentBehavior\projects\semester-etl\src\student_behavior_etl\cli.py`
- Test: `C:\Users\Orion\Desktop\StudentBehavior\projects\semester-etl\tests\test_config.py`

- [ ] **Step 1: 写最小工程壳子，先让 `uv` 和 `pytest` 可用**

```toml
[project]
name = "student-behavior-etl"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = ["pandas>=2.2", "openpyxl>=3.1"]

[dependency-groups]
dev = ["pytest>=8.0"]

[project.scripts]
semester-features = "student_behavior_etl.cli:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

```python
def main(argv: list[str] | None = None) -> int:
    raise NotImplementedError("CLI is not implemented yet")
```

- [ ] **Step 2: 同步开发依赖**

Run: `uv sync --project projects/semester-etl --dev`
Expected: environment created successfully with `pytest` available

- [ ] **Step 3: 写默认路径失败测试**

```python
from pathlib import Path

from student_behavior_etl.config import build_default_paths


def test_build_default_paths_uses_project_bound_locations() -> None:
    repo_root = Path(r"C:\Users\Orion\Desktop\StudentBehavior")

    paths = build_default_paths(repo_root)

    assert paths.input_dir == repo_root / "数据集及类型"
    assert paths.output_dir == repo_root / "artifacts" / "semester_features"
    assert paths.output_csv == paths.output_dir / "v1_semester_features.csv"
    assert paths.output_warning_json == paths.output_dir / "v1_warnings.json"
```

- [ ] **Step 4: 运行测试，确认当前失败**

Run: `uv run --project projects/semester-etl pytest projects/semester-etl/tests/test_config.py -v`
Expected: FAIL with `ModuleNotFoundError` or import failure for `student_behavior_etl.config`

- [ ] **Step 5: 写最小配置实现**

```python
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DefaultPaths:
    input_dir: Path
    output_dir: Path
    output_csv: Path
    output_warning_json: Path


def build_default_paths(repo_root: Path) -> DefaultPaths:
    output_dir = repo_root / "artifacts" / "semester_features"
    return DefaultPaths(
        input_dir=repo_root / "数据集及类型",
        output_dir=output_dir,
        output_csv=output_dir / "v1_semester_features.csv",
        output_warning_json=output_dir / "v1_warnings.json",
    )
```

- [ ] **Step 6: 重新运行配置测试，确认通过**

Run: `uv run --project projects/semester-etl pytest projects/semester-etl/tests/test_config.py -v`
Expected: PASS

- [ ] **Step 7: 提交骨架**

```bash
git add projects/semester-etl/pyproject.toml projects/semester-etl/src/student_behavior_etl/__init__.py projects/semester-etl/src/student_behavior_etl/config.py projects/semester-etl/src/student_behavior_etl/cli.py projects/semester-etl/tests/test_config.py
git commit -m "feat: scaffold semester etl project"
```

### Task 2: 实现学号与学期键归一化

**Files:**
- Create: `C:\Users\Orion\Desktop\StudentBehavior\projects\semester-etl\src\student_behavior_etl\normalize.py`
- Test: `C:\Users\Orion\Desktop\StudentBehavior\projects\semester-etl\tests\test_normalize.py`

- [ ] **Step 1: 写 `student_id` 和 `term_key` 失败测试**

```python
import pytest

from student_behavior_etl.normalize import normalize_student_id, normalize_term_key


def test_normalize_student_id_trims_and_preserves_value() -> None:
    assert normalize_student_id("  pjxyqxbj337  ") == "pjxyqxbj337"


def test_normalize_student_id_rejects_empty_value() -> None:
    assert normalize_student_id("   ") is None


def test_normalize_term_key_from_xn_and_xq() -> None:
    assert normalize_term_key("2023-2024", 2) == "2023-2"


@pytest.mark.parametrize(
    "xn,xq",
    [("", 1), ("2023-2024", 3), (None, 1), ("2023/2024", 1), ("foo-bar", 1), ("23-2024", 1)],
)
def test_normalize_term_key_rejects_invalid_values(xn, xq) -> None:
    assert normalize_term_key(xn, xq) is None
```

- [ ] **Step 2: 运行归一化测试，确认失败**

Run: `uv run --project projects/semester-etl pytest projects/semester-etl/tests/test_normalize.py -v`
Expected: FAIL because `normalize.py` does not exist yet

- [ ] **Step 3: 写最小归一化实现**

```python
from __future__ import annotations
import re


def normalize_student_id(raw: object) -> str | None:
    if raw is None:
        return None
    value = str(raw).strip()
    return value or None


def normalize_term_key(raw_xn: object, raw_xq: object) -> str | None:
    if raw_xn is None or raw_xq is None:
        return None
    xn = str(raw_xn).strip()
    if not xn or not re.fullmatch(r"\d{4}-\d{4}", xn):
        return None
    left_year, right_year = xn.split("-", 1)
    if int(right_year) != int(left_year) + 1:
        return None
    term_year = left_year
    try:
        term_no = int(raw_xq)
    except (TypeError, ValueError):
        return None
    if term_no not in (1, 2):
        return None
    return f"{term_year}-{term_no}"
```

- [ ] **Step 4: 重新运行归一化测试，确认通过**

Run: `uv run --project projects/semester-etl pytest projects/semester-etl/tests/test_normalize.py -v`
Expected: PASS

- [ ] **Step 5: 提交归一化能力**

```bash
git add projects/semester-etl/src/student_behavior_etl/normalize.py projects/semester-etl/tests/test_normalize.py
git commit -m "feat: add semester etl normalization helpers"
```

### Task 3: 实现 warning 模型与源表读取校验

**Files:**
- Create: `C:\Users\Orion\Desktop\StudentBehavior\projects\semester-etl\src\student_behavior_etl\reporting.py`
- Create: `C:\Users\Orion\Desktop\StudentBehavior\projects\semester-etl\src\student_behavior_etl\io.py`
- Test: `C:\Users\Orion\Desktop\StudentBehavior\projects\semester-etl\tests\test_reporting.py`

- [ ] **Step 1: 写 warning 与列校验失败测试**

```python
import pytest

from student_behavior_etl.io import validate_required_columns
from student_behavior_etl.reporting import WarningCollector


def test_warning_collector_uses_frozen_reason_keys() -> None:
    collector = WarningCollector()
    collector.bump_dropped_attendance("missing_student_id")
    collector.bump_dropped_attendance("invalid_term_fields")
    collector.bump_dropped_final("missing_major_name")
    collector.add_source_status("考勤汇总.xlsx", "used", 3, "attendance rows loaded")

    payload = collector.to_payload(output_file="out.csv")

    assert payload["dropped_attendance_rows"]["missing_student_id"] == 1
    assert payload["dropped_attendance_rows"]["invalid_term_fields"] == 1
    assert payload["dropped_final_rows"]["missing_major_name"] == 1
    assert payload["source_file_status"][0]["source_file"] == "考勤汇总.xlsx"
    assert payload["source_file_status"][0]["status"] == "used"
    assert payload["source_file_status"][0]["rows_read"] == 3
    assert payload["generated_at"].endswith("Z")


def test_validate_required_columns_rejects_missing_columns() -> None:
    with pytest.raises(ValueError, match="missing required columns"):
        validate_required_columns(["XH", "XN"], {"XH", "XN", "XQ"})
```

- [ ] **Step 2: 运行 warning 测试，确认失败**

Run: `uv run --project projects/semester-etl pytest projects/semester-etl/tests/test_reporting.py -v`
Expected: FAIL because reporting/io helpers do not exist yet

- [ ] **Step 3: 写最小 warning 与校验实现**

```python
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class WarningCollector:
    dropped_attendance_rows: Counter = field(default_factory=Counter)
    dropped_final_rows: Counter = field(default_factory=Counter)
    source_file_status: list[dict[str, object]] = field(default_factory=list)
    degraded_sources: list[dict[str, object]] = field(default_factory=list)

    def bump_dropped_attendance(self, reason: str) -> None:
        self.dropped_attendance_rows[reason] += 1

    def bump_dropped_final(self, reason: str) -> None:
        self.dropped_final_rows[reason] += 1

    def add_source_status(self, source_file: str, status: str, rows_read: int, notes: str) -> None:
        self.source_file_status.append(
            {
                "source_file": source_file,
                "status": status,
                "rows_read": rows_read,
                "notes": notes,
            }
        )

    def to_payload(self, output_file: str) -> dict[str, object]:
        return {
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "output_file": output_file,
            "source_file_status": self.source_file_status,
            "dropped_attendance_rows": {
                "missing_student_id": self.dropped_attendance_rows["missing_student_id"],
                "invalid_term_fields": self.dropped_attendance_rows["invalid_term_fields"],
            },
            "dropped_final_rows": {
                "missing_major_name": self.dropped_final_rows["missing_major_name"],
            },
            "degraded_sources": self.degraded_sources,
        }
```

```python
def validate_required_columns(actual_columns: list[str], required_columns: set[str]) -> None:
    missing = sorted(required_columns - set(actual_columns))
    if missing:
        raise ValueError(f"missing required columns: {', '.join(missing)}")
```

- [ ] **Step 4: 重新运行 warning 测试，确认通过**

Run: `uv run --project projects/semester-etl pytest projects/semester-etl/tests/test_reporting.py -v`
Expected: PASS

- [ ] **Step 5: 提交 warning 与列校验**

```bash
git add projects/semester-etl/src/student_behavior_etl/reporting.py projects/semester-etl/src/student_behavior_etl/io.py projects/semester-etl/tests/test_reporting.py
git commit -m "feat: add etl warning reporting primitives"
```

### Task 4: 实现考勤聚合、专业补齐和排序规则

**Files:**
- Create: `C:\Users\Orion\Desktop\StudentBehavior\projects\semester-etl\src\student_behavior_etl\build_semester_features.py`
- Modify: `C:\Users\Orion\Desktop\StudentBehavior\projects\semester-etl\src\student_behavior_etl\io.py`
- Test: `C:\Users\Orion\Desktop\StudentBehavior\projects\semester-etl\tests\test_build_semester_features.py`

- [ ] **Step 1: 写基础特征构建失败测试**

```python
import pandas as pd

from student_behavior_etl.build_semester_features import build_semester_feature_frame
from student_behavior_etl.reporting import WarningCollector


def test_builds_attendance_features_and_major_name() -> None:
    attendance = pd.DataFrame(
        [
            {"XH": "stu-2", "XN": "2023-2024", "XQ": 1},
            {"XH": "stu-1", "XN": "2023-2024", "XQ": 2},
            {"XH": "stu-1", "XN": "2023-2024", "XQ": 2},
        ]
    )
    students = pd.DataFrame(
        [
            {"XH": "stu-1", "ZYM": "信息安全"},
            {"XH": "stu-2", "ZYM": "电子信息工程"},
        ]
    )

    result = build_semester_feature_frame(
        attendance_df=attendance,
        student_df=students,
        internet_df=None,
        collector=WarningCollector(),
    )

    assert result.to_dict(orient="records") == [
        {
            "student_id": "stu-1",
            "term_key": "2023-2",
            "major_name": "信息安全",
            "attendance_record_count": 2,
            "internet_duration_sum": 0.0,
        },
        {
            "student_id": "stu-2",
            "term_key": "2023-1",
            "major_name": "电子信息工程",
            "attendance_record_count": 1,
            "internet_duration_sum": 0.0,
        },
    ]
```

- [ ] **Step 2: 写重复专业冲突失败测试**

```python
import pandas as pd
import pytest

from student_behavior_etl.build_semester_features import build_student_dimension


def test_duplicate_student_major_conflict_hard_fails() -> None:
    students = pd.DataFrame(
        [
            {"XH": "stu-1", "ZYM": "信息安全"},
            {"XH": "stu-1", "ZYM": "电子信息工程"},
        ]
    )

    with pytest.raises(ValueError, match="conflicting major_name"):
        build_student_dimension(students)


def test_missing_major_name_rows_are_removed_from_dimension() -> None:
    students = pd.DataFrame(
        [
            {"XH": "stu-1", "ZYM": ""},
            {"XH": "stu-2", "ZYM": None},
            {"XH": "stu-3", "ZYM": "信息安全"},
        ]
    )

    result = build_student_dimension(students)

    assert result.to_dict(orient="records") == [
        {"student_id": "stu-3", "major_name": "信息安全"},
    ]
```

- [ ] **Step 3: 运行构建测试，确认失败**

Run: `uv run --project projects/semester-etl pytest projects/semester-etl/tests/test_build_semester_features.py -v`
Expected: FAIL because builder does not exist yet

- [ ] **Step 4: 写最小聚合实现**

```python
import pandas as pd

from student_behavior_etl.normalize import normalize_student_id, normalize_term_key


def normalize_major_name(raw: object) -> str | None:
    if raw is None or pd.isna(raw):
        return None
    value = str(raw).strip()
    return value or None


def build_student_dimension(student_df: pd.DataFrame) -> pd.DataFrame:
    cleaned = student_df.assign(
        student_id=student_df["XH"].map(normalize_student_id),
        major_name=student_df["ZYM"].map(normalize_major_name),
    )[["student_id", "major_name"]]
    cleaned = cleaned.dropna(subset=["student_id", "major_name"])
    conflicts = cleaned.groupby("student_id")["major_name"].nunique()
    if (conflicts > 1).any():
        raise ValueError("conflicting major_name for duplicated student_id")
    return cleaned.drop_duplicates(subset=["student_id", "major_name"])


def build_semester_feature_frame(attendance_df, student_df, internet_df, collector):
    normalized = attendance_df.assign(
        student_id=attendance_df["XH"].map(normalize_student_id),
        term_key=attendance_df.apply(
            lambda row: normalize_term_key(row["XN"], row["XQ"]), axis=1
        ),
    )
    valid = normalized.dropna(subset=["student_id", "term_key"])
    aggregated = (
        valid.groupby(["student_id", "term_key"], as_index=False)
        .size()
        .rename(columns={"size": "attendance_record_count"})
    )
    dimension = build_student_dimension(student_df)
    joined = aggregated.merge(dimension, how="left", on="student_id")
    joined["internet_duration_sum"] = 0.0
    joined = joined[["student_id", "term_key", "major_name", "attendance_record_count", "internet_duration_sum"]]
    return joined.sort_values(["student_id", "term_key"]).reset_index(drop=True)
```

- [ ] **Step 5: 重新运行构建测试，确认通过**

Run: `uv run --project projects/semester-etl pytest projects/semester-etl/tests/test_build_semester_features.py -v`
Expected: PASS

- [ ] **Step 6: 提交基础构建能力**

```bash
git add projects/semester-etl/src/student_behavior_etl/build_semester_features.py projects/semester-etl/src/student_behavior_etl/io.py projects/semester-etl/tests/test_build_semester_features.py
git commit -m "feat: build attendance-based semester features"
```

### Task 5: 接入行级告警和网络源整表降级

**Files:**
- Modify: `C:\Users\Orion\Desktop\StudentBehavior\projects\semester-etl\src\student_behavior_etl\build_semester_features.py`
- Modify: `C:\Users\Orion\Desktop\StudentBehavior\projects\semester-etl\src\student_behavior_etl\reporting.py`
- Test: `C:\Users\Orion\Desktop\StudentBehavior\projects\semester-etl\tests\test_build_semester_features.py`

- [ ] **Step 1: 写考勤脏行与网络降级失败测试**

```python
import pandas as pd

from student_behavior_etl.build_semester_features import build_semester_feature_frame
from student_behavior_etl.reporting import WarningCollector


def test_invalid_attendance_rows_are_dropped_with_warning_counts() -> None:
    attendance = pd.DataFrame(
        [
            {"XH": "stu-1", "XN": "2023-2024", "XQ": 1},
            {"XH": " ", "XN": "2023-2024", "XQ": 1},
            {"XH": "stu-2", "XN": "2023-2024", "XQ": 9},
        ]
    )
    students = pd.DataFrame(
        [
            {"XH": "stu-1", "ZYM": "信息安全"},
            {"XH": "stu-2", "ZYM": "电子信息工程"},
        ]
    )
    collector = WarningCollector()

    result = build_semester_feature_frame(attendance, students, None, collector)

    assert len(result) == 1
    assert collector.dropped_attendance_rows["missing_student_id"] == 1
    assert collector.dropped_attendance_rows["invalid_term_fields"] == 1


def test_rows_without_major_name_are_dropped_and_counted() -> None:
    attendance = pd.DataFrame([{"XH": "stu-1", "XN": "2023-2024", "XQ": 1}])
    students = pd.DataFrame([{"XH": "stu-1", "ZYM": ""}])
    collector = WarningCollector()

    result = build_semester_feature_frame(attendance, students, None, collector)

    assert result.empty
    assert collector.dropped_final_rows["missing_major_name"] == 1


def test_internet_source_degrades_when_term_fields_are_missing() -> None:
    attendance = pd.DataFrame([{"XH": "stu-1", "XN": "2023-2024", "XQ": 1}])
    students = pd.DataFrame([{"XH": "stu-1", "ZYM": "信息安全"}])
    internet = pd.DataFrame(
        [
            {"XSBH": "stu-1", "XN": None, "XQ": None, "TJNY": "2023-03-01", "SWLJSC": 12.5},
            {"XSBH": "stu-1", "XN": None, "XQ": None, "TJNY": "2023-04-01", "SWLJSC": 2.5},
        ]
    )
    collector = WarningCollector()

    result = build_semester_feature_frame(attendance, students, internet, collector)

    assert result.loc[0, "internet_duration_sum"] == 0.0
    degraded = collector.degraded_sources[0]
    assert degraded["source_file"] == "上网统计.xlsx"
    assert degraded["excluded_row_count"] == 2
    assert degraded["tjny_min"] == "2023-03-01"
    assert degraded["tjny_max"] == "2023-04-01"


def test_internet_source_can_aggregate_when_frozen_term_fields_exist() -> None:
    attendance = pd.DataFrame([{"XH": "stu-1", "XN": "2023-2024", "XQ": 1}])
    students = pd.DataFrame([{"XH": "stu-1", "ZYM": "信息安全"}])
    internet = pd.DataFrame(
        [
            {"XSBH": "stu-1", "XN": "2023-2024", "XQ": 1, "TJNY": "2023-03-01", "SWLJSC": 12.5},
            {"XSBH": "stu-1", "XN": "2023-2024", "XQ": 1, "TJNY": "2023-04-01", "SWLJSC": 2.5},
        ]
    )
    collector = WarningCollector()

    result = build_semester_feature_frame(attendance, students, internet, collector)

    assert result.loc[0, "internet_duration_sum"] == 15.0
    assert collector.degraded_sources == []
```

- [ ] **Step 2: 运行降级测试，确认失败**

Run: `uv run --project projects/semester-etl pytest projects/semester-etl/tests/test_build_semester_features.py -v`
Expected: FAIL because warning counters and degraded source details are incomplete

- [ ] **Step 3: 写最小降级与 warning 集成实现**

```python
def build_semester_feature_frame(attendance_df, student_df, internet_df, collector):
    normalized = attendance_df.assign(
        student_id=attendance_df["XH"].map(normalize_student_id),
        term_key=attendance_df.apply(
            lambda row: normalize_term_key(row["XN"], row["XQ"]), axis=1
        ),
    )
    missing_student_mask = normalized["student_id"].isna()
    invalid_term_mask = normalized["term_key"].isna() & ~missing_student_mask
    collector.dropped_attendance_rows["missing_student_id"] += int(missing_student_mask.sum())
    collector.dropped_attendance_rows["invalid_term_fields"] += int(invalid_term_mask.sum())

    valid = normalized.loc[~missing_student_mask & ~invalid_term_mask].copy()
    aggregated = (
        valid.groupby(["student_id", "term_key"], as_index=False)
        .size()
        .rename(columns={"size": "attendance_record_count"})
    )
    dimension = build_student_dimension(student_df)
    joined = aggregated.merge(dimension, how="left", on="student_id")
    missing_major_mask = joined["major_name"].isna()
    collector.dropped_final_rows["missing_major_name"] += int(missing_major_mask.sum())
    joined = joined.loc[~missing_major_mask].copy()

    joined["internet_duration_sum"] = 0.0
    if internet_df is not None and not internet_df.empty:
        normalized_internet = internet_df.assign(
            student_id=internet_df["XSBH"].map(normalize_student_id),
            term_key=internet_df.apply(
                lambda row: normalize_term_key(row["XN"], row["XQ"]), axis=1
            ),
        )
        valid_internet = normalized_internet.dropna(subset=["student_id", "term_key"]).copy()
        if not valid_internet.empty:
            internet_agg = (
                valid_internet.groupby(["student_id", "term_key"], as_index=False)["SWLJSC"]
                .sum()
                .rename(columns={"SWLJSC": "internet_duration_sum"})
            )
            joined = joined.drop(columns=["internet_duration_sum"]).merge(
                internet_agg,
                how="left",
                on=["student_id", "term_key"],
            )
            joined["internet_duration_sum"] = joined["internet_duration_sum"].fillna(0.0)
        else:
            collector.degraded_sources.append(
                {
                    "source_file": "上网统计.xlsx",
                    "reason": "missing frozen XN/XQ; TJNY inference disabled",
                    "excluded_row_count": int(len(internet_df)),
                    "affected_student_count": int(internet_df["XSBH"].astype(str).str.strip().nunique()),
                    "tjny_min": str(internet_df["TJNY"].min()),
                    "tjny_max": str(internet_df["TJNY"].max()),
                }
            )
```

- [ ] **Step 4: 重新运行降级测试，确认通过**

Run: `uv run --project projects/semester-etl pytest projects/semester-etl/tests/test_build_semester_features.py -v`
Expected: PASS

- [ ] **Step 5: 提交降级逻辑**

```bash
git add projects/semester-etl/src/student_behavior_etl/build_semester_features.py projects/semester-etl/src/student_behavior_etl/reporting.py projects/semester-etl/tests/test_build_semester_features.py
git commit -m "feat: degrade internet source under frozen term rules"
```

### Task 6: 实现 Excel 读取器、JSON 写出和 CLI 入口

**Files:**
- Modify: `C:\Users\Orion\Desktop\StudentBehavior\projects\semester-etl\src\student_behavior_etl\io.py`
- Modify: `C:\Users\Orion\Desktop\StudentBehavior\projects\semester-etl\src\student_behavior_etl\reporting.py`
- Modify: `C:\Users\Orion\Desktop\StudentBehavior\projects\semester-etl\src\student_behavior_etl\cli.py`
- Test: `C:\Users\Orion\Desktop\StudentBehavior\projects\semester-etl\tests\test_cli.py`

- [ ] **Step 1: 写 CLI 集成失败测试**

```python
import json
from pathlib import Path

import pandas as pd
import pytest

from student_behavior_etl.cli import run_build
from student_behavior_etl.config import DefaultPaths


def test_run_build_writes_csv_and_warning_json(tmp_path: Path) -> None:
    input_dir = tmp_path / "数据集及类型"
    output_dir = tmp_path / "artifacts" / "semester_features"
    input_dir.mkdir(parents=True)

    pd.DataFrame([{"XH": "stu-1", "ZYM": "信息安全"}]).to_excel(input_dir / "学生基本信息.xlsx", index=False)
    pd.DataFrame([{"XH": "stu-1", "XN": "2023-2024", "XQ": 1}]).to_excel(input_dir / "考勤汇总.xlsx", index=False)
    pd.DataFrame([{"XSBH": "stu-1", "XN": None, "XQ": None, "TJNY": "2023-03-01", "SWLJSC": 9.5}]).to_excel(input_dir / "上网统计.xlsx", index=False)

    paths = DefaultPaths(
        input_dir=input_dir,
        output_dir=output_dir,
        output_csv=output_dir / "v1_semester_features.csv",
        output_warning_json=output_dir / "v1_warnings.json",
    )

    summary = run_build(paths)

    csv_df = pd.read_csv(paths.output_csv)
    warning_payload = json.loads(paths.output_warning_json.read_text(encoding="utf-8"))

    assert list(csv_df.columns) == [
        "student_id",
        "term_key",
        "major_name",
        "attendance_record_count",
        "internet_duration_sum",
    ]
    assert warning_payload["degraded_sources"][0]["source_file"] == "上网统计.xlsx"
    assert summary["rows_written"] == 1
    assert summary["sources_read"] == ["学生基本信息.xlsx", "考勤汇总.xlsx", "上网统计.xlsx"]
    assert summary["internet_source_degraded"] is True
    assert summary["dropped_attendance_rows"] == 0


def test_run_build_marks_internet_source_used_when_frozen_term_fields_exist(tmp_path: Path) -> None:
    input_dir = tmp_path / "数据集及类型"
    output_dir = tmp_path / "artifacts" / "semester_features"
    input_dir.mkdir(parents=True)

    pd.DataFrame([{"XH": "stu-1", "ZYM": "信息安全"}]).to_excel(input_dir / "学生基本信息.xlsx", index=False)
    pd.DataFrame([{"XH": "stu-1", "XN": "2023-2024", "XQ": 1}]).to_excel(input_dir / "考勤汇总.xlsx", index=False)
    pd.DataFrame(
        [{"XSBH": "stu-1", "XN": "2023-2024", "XQ": 1, "TJNY": "2023-03-01", "SWLJSC": 9.5}]
    ).to_excel(input_dir / "上网统计.xlsx", index=False)

    paths = DefaultPaths(
        input_dir=input_dir,
        output_dir=output_dir,
        output_csv=output_dir / "v1_semester_features.csv",
        output_warning_json=output_dir / "v1_warnings.json",
    )

    summary = run_build(paths)
    warning_payload = json.loads(paths.output_warning_json.read_text(encoding="utf-8"))

    assert summary["internet_source_degraded"] is False
    assert warning_payload["source_file_status"][2]["status"] == "used"


def test_run_build_hard_fails_when_required_source_is_missing(tmp_path: Path) -> None:
    input_dir = tmp_path / "数据集及类型"
    output_dir = tmp_path / "artifacts" / "semester_features"
    input_dir.mkdir(parents=True)

    pd.DataFrame([{"XH": "stu-1", "ZYM": "信息安全"}]).to_excel(input_dir / "学生基本信息.xlsx", index=False)
    pd.DataFrame([{"XH": "stu-1", "XN": "2023-2024", "XQ": 1}]).to_excel(input_dir / "考勤汇总.xlsx", index=False)

    paths = DefaultPaths(
        input_dir=input_dir,
        output_dir=output_dir,
        output_csv=output_dir / "v1_semester_features.csv",
        output_warning_json=output_dir / "v1_warnings.json",
    )

    with pytest.raises(FileNotFoundError):
        run_build(paths)
```

- [ ] **Step 2: 运行 CLI 测试，确认失败**

Run: `uv run --project projects/semester-etl pytest projects/semester-etl/tests/test_cli.py -v`
Expected: FAIL because CLI and file writers do not exist yet

- [ ] **Step 3: 写最小 CLI、读取器和 JSON 写出实现**

```python
import json
from pathlib import Path

import pandas as pd


def read_excel_required(path: Path, required_columns: set[str]) -> pd.DataFrame:
    frame = pd.read_excel(path)
    validate_required_columns(list(frame.columns), required_columns)
    return frame


def write_warning_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
```

```python
import argparse
from pathlib import Path

from student_behavior_etl.build_semester_features import build_semester_feature_frame
from student_behavior_etl.config import build_default_paths
from student_behavior_etl.io import read_excel_required, write_warning_json
from student_behavior_etl.reporting import WarningCollector


def run_build(paths):
    collector = WarningCollector()
    student_df = read_excel_required(paths.input_dir / "学生基本信息.xlsx", {"XH", "ZYM"})
    collector.add_source_status("学生基本信息.xlsx", "used", len(student_df), "student dimension loaded")
    attendance_df = read_excel_required(paths.input_dir / "考勤汇总.xlsx", {"XH", "XN", "XQ"})
    collector.add_source_status("考勤汇总.xlsx", "used", len(attendance_df), "attendance rows loaded")
    internet_df = read_excel_required(paths.input_dir / "上网统计.xlsx", {"XSBH", "XN", "XQ", "TJNY", "SWLJSC"})
    result = build_semester_feature_frame(attendance_df, student_df, internet_df, collector)
    degraded_internet = next(
        (item for item in collector.degraded_sources if item["source_file"] == "上网统计.xlsx"),
        None,
    )
    collector.add_source_status(
        "上网统计.xlsx",
        "degraded" if degraded_internet else "used",
        len(internet_df),
        degraded_internet["reason"] if degraded_internet else "internet rows aggregated by frozen XN/XQ",
    )
    paths.output_dir.mkdir(parents=True, exist_ok=True)
    result.to_csv(paths.output_csv, index=False, encoding="utf-8-sig")
    payload = collector.to_payload(output_file=str(paths.output_csv))
    write_warning_json(paths.output_warning_json, payload)
    return {
        "sources_read": ["学生基本信息.xlsx", "考勤汇总.xlsx", "上网统计.xlsx"],
        "rows_written": int(len(result)),
        "student_count": int(result["student_id"].nunique()),
        "term_count": int(result["term_key"].nunique()),
        "dropped_attendance_rows": int(sum(collector.dropped_attendance_rows.values())),
        "internet_source_degraded": bool(collector.degraded_sources),
        "warning_file": str(paths.output_warning_json),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("build")
    args = parser.parse_args(argv)
    if args.command == "build":
        summary = run_build(build_default_paths(Path.cwd()))
        print("\n".join([
            f"sources_read={', '.join(summary['sources_read'])}",
            f"rows_written={summary['rows_written']}",
            f"student_count={summary['student_count']}",
            f"term_count={summary['term_count']}",
            f"dropped_attendance_rows={summary['dropped_attendance_rows']}",
            f"internet_source_degraded={summary['internet_source_degraded']}",
            f"warning_file={summary['warning_file']}",
        ]))
        return 0
    return 1
```

- [ ] **Step 4: 重新运行 CLI 测试，确认通过**

Run: `uv run --project projects/semester-etl pytest projects/semester-etl/tests/test_cli.py -v`
Expected: PASS

- [ ] **Step 5: 提交 CLI 入口**

```bash
git add projects/semester-etl/src/student_behavior_etl/io.py projects/semester-etl/src/student_behavior_etl/reporting.py projects/semester-etl/src/student_behavior_etl/cli.py projects/semester-etl/tests/test_cli.py
git commit -m "feat: add semester feature cli entrypoint"
```

### Task 7: 跑全量验证并用真实数据快照验收

**Files:**
- Modify: `C:\Users\Orion\Desktop\StudentBehavior\projects\semester-etl\src\student_behavior_etl\cli.py`
- Modify: `C:\Users\Orion\Desktop\StudentBehavior\projects\semester-etl\src\student_behavior_etl\reporting.py`
- Modify: `C:\Users\Orion\Desktop\StudentBehavior\projects\semester-etl\src\student_behavior_etl\build_semester_features.py`
- Test: `C:\Users\Orion\Desktop\StudentBehavior\projects\semester-etl\tests\test_config.py`
- Test: `C:\Users\Orion\Desktop\StudentBehavior\projects\semester-etl\tests\test_normalize.py`
- Test: `C:\Users\Orion\Desktop\StudentBehavior\projects\semester-etl\tests\test_reporting.py`
- Test: `C:\Users\Orion\Desktop\StudentBehavior\projects\semester-etl\tests\test_build_semester_features.py`
- Test: `C:\Users\Orion\Desktop\StudentBehavior\projects\semester-etl\tests\test_cli.py`

- [ ] **Step 1: 跑完整测试集**

Run: `uv run --project projects/semester-etl pytest projects/semester-etl/tests -v`
Expected: PASS

- [ ] **Step 2: 用真实项目快照运行 CLI**

Run: `uv run --project projects/semester-etl semester-features build`
Expected:
- 退出码为 `0`
- 生成 `C:\Users\Orion\Desktop\StudentBehavior\artifacts\semester_features\v1_semester_features.csv`
- 生成 `C:\Users\Orion\Desktop\StudentBehavior\artifacts\semester_features\v1_warnings.json`

- [ ] **Step 3: 执行人工验收命令并记录核验结论，确认真实快照符合冻结口径**

```bash
@'
import json
import pandas as pd
from pathlib import Path

csv_path = Path(r"C:\Users\Orion\Desktop\StudentBehavior\artifacts\semester_features\v1_semester_features.csv")
warning_path = Path(r"C:\Users\Orion\Desktop\StudentBehavior\artifacts\semester_features\v1_warnings.json")

df = pd.read_csv(csv_path)
payload = json.loads(warning_path.read_text(encoding="utf-8"))

assert list(df.columns) == [
    "student_id",
    "term_key",
    "major_name",
    "attendance_record_count",
    "internet_duration_sum",
]
assert df["internet_duration_sum"].eq(0).all()
assert payload["degraded_sources"][0]["source_file"] == "上网统计.xlsx"
print("real snapshot acceptance passed")
'@ | uv run --project projects/semester-etl python -
```

Note:
- 如果不把这条做成自动化测试，就必须在最终说明里明确人工核验了哪些列和结果。
- 若 CLI 摘要缺少 `sources_read`、`rows_written`、`student_count`、`term_count`、`dropped_attendance_rows`、降级说明或 warning 文件路径，本任务中补齐。

- [ ] **Step 4: 如有必要做最小修正后，再跑一次全量验证**

Run:
- `uv run --project projects/semester-etl pytest projects/semester-etl/tests -v`
- `uv run --project projects/semester-etl semester-features build`

Expected: PASS and artifacts updated

- [ ] **Step 5: 提交验收版实现**

```bash
git add projects/semester-etl/pyproject.toml projects/semester-etl/src/student_behavior_etl projects/semester-etl/tests
git commit -m "feat: ship v1 semester feature etl cli"
```

## 完成定义

- `uv run --project projects/semester-etl semester-features build` 在仓库根目录可直接运行
- 输出 CSV 仅包含冻结的 5 个字段
- 输出 JSON 具有稳定的 warning 结构
- 行排序稳定为 `(student_id, term_key)` 升序
- 当前真实快照下 `internet_duration_sum` 全为 `0`
- `上网统计.xlsx` 被整表降级且原因写入 JSON
- 所有测试通过
- git 工作区干净

## 执行备注

- 推荐执行方式：`superpowers:subagent-driven-development`
- 每个 Task 完成后必须先过 spec review，再过 code quality review
- 若 reviewer 要求扩大范围到未冻结字段，直接拒绝并引用 spec 与 frozen docs
