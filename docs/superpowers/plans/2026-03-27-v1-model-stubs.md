# V1 Model Stubs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

> **Note (2026-03-28):** 本文是历史执行计划。文中的绝对路径保留原始上下文，但当前仓库请以相对路径 `projects/model-stubs` 和 `docs/v1-api-contract.md` 为准。

**Goal:** 在独立子项目 `projects/model-stubs` 中实现一个离线结果层 CLI，读取上游 `student_term_features` 与必要维度输入，稳定产出风险、分层、解释、建议、总览和模型摘要制品，供后续 `demo-api` 直接读取。

**Architecture:** 保持“结果层”边界清晰。`model-stubs` 不读取原始 Excel，不训练正式模型，只消费 `analytics-db` 的标准化输入，并以确定性 stub 规则生成 4 份核心结果文件和 1 份 warnings 文件。字段命名与 `docs/superpowers/specs/2026-03-27-v1-model-stubs-design.md` 以及 `docs/v1-api-contract.md` 对齐。

**Tech Stack:** Python 3.12+, `uv`, `pandas`, `pytest`, 标准库 `argparse`, `dataclasses`, `json`, `hashlib`, `datetime`, `pathlib`

---

## 实施前文件地图

### 需要创建的文件

- `C:\Users\Orion\Desktop\StudentBehavior\projects\model-stubs\pyproject.toml`
- `C:\Users\Orion\Desktop\StudentBehavior\projects\model-stubs\src\student_behavior_model_stubs\__init__.py`
- `C:\Users\Orion\Desktop\StudentBehavior\projects\model-stubs\src\student_behavior_model_stubs\config.py`
- `C:\Users\Orion\Desktop\StudentBehavior\projects\model-stubs\src\student_behavior_model_stubs\io.py`
- `C:\Users\Orion\Desktop\StudentBehavior\projects\model-stubs\src\student_behavior_model_stubs\scoring.py`
- `C:\Users\Orion\Desktop\StudentBehavior\projects\model-stubs\src\student_behavior_model_stubs\templates.py`
- `C:\Users\Orion\Desktop\StudentBehavior\projects\model-stubs\src\student_behavior_model_stubs\reporting.py`
- `C:\Users\Orion\Desktop\StudentBehavior\projects\model-stubs\src\student_behavior_model_stubs\build_outputs.py`
- `C:\Users\Orion\Desktop\StudentBehavior\projects\model-stubs\src\student_behavior_model_stubs\cli.py`
- `C:\Users\Orion\Desktop\StudentBehavior\projects\model-stubs\tests\test_config.py`
- `C:\Users\Orion\Desktop\StudentBehavior\projects\model-stubs\tests\test_io.py`
- `C:\Users\Orion\Desktop\StudentBehavior\projects\model-stubs\tests\test_scoring.py`
- `C:\Users\Orion\Desktop\StudentBehavior\projects\model-stubs\tests\test_templates.py`
- `C:\Users\Orion\Desktop\StudentBehavior\projects\model-stubs\tests\test_build_outputs.py`
- `C:\Users\Orion\Desktop\StudentBehavior\projects\model-stubs\tests\test_cli.py`

### 运行时产物

- `C:\Users\Orion\Desktop\StudentBehavior\artifacts\model_stubs\v1_student_results.csv`
- `C:\Users\Orion\Desktop\StudentBehavior\artifacts\model_stubs\v1_student_reports.jsonl`
- `C:\Users\Orion\Desktop\StudentBehavior\artifacts\model_stubs\v1_overview_by_term.json`
- `C:\Users\Orion\Desktop\StudentBehavior\artifacts\model_stubs\v1_model_summary.json`
- `C:\Users\Orion\Desktop\StudentBehavior\artifacts\model_stubs\v1_warnings.json`

## 全局约束

- 全程遵守 TDD：先写失败测试，再写最小实现，再跑通过。
- `model-stubs` 只读取上游结果文件或 DataFrame，不直接读取原始 Excel。
- 结果层必须显式保留 `stub` 身份，不得使用误导性命名暗示真实模型已训练完成。
- `updated_at` 与 `generated_at` 必须是运行时真实时间戳，禁止保留占位符字符串。
- `risk_probability`、`risk_level`、`quadrant_label` 必须可重复、可解释、非全常量。
- `student_name` 若无法从上游稳定拿到，允许回退为 `student_id`，但必须作为占位策略显式测试。
- 空特征允许降级，不允许拍脑袋补假值。

### Task 1: 搭建独立结果层子项目骨架

**Files:**
- Create: `C:\Users\Orion\Desktop\StudentBehavior\projects\model-stubs\pyproject.toml`
- Create: `C:\Users\Orion\Desktop\StudentBehavior\projects\model-stubs\src\student_behavior_model_stubs\__init__.py`
- Create: `C:\Users\Orion\Desktop\StudentBehavior\projects\model-stubs\src\student_behavior_model_stubs\config.py`
- Create: `C:\Users\Orion\Desktop\StudentBehavior\projects\model-stubs\src\student_behavior_model_stubs\cli.py`
- Test: `C:\Users\Orion\Desktop\StudentBehavior\projects\model-stubs\tests\test_config.py`

- [ ] **Step 1: 写最小工程和 CLI 失败测试**

```python
from pathlib import Path

from student_behavior_model_stubs.config import build_default_paths


def test_build_default_paths_uses_project_bound_locations() -> None:
    repo_root = Path(r"C:\Users\Orion\Desktop\StudentBehavior")
    paths = build_default_paths(repo_root)
    assert paths.output_dir == repo_root / "artifacts" / "model_stubs"
    assert paths.student_results_csv == paths.output_dir / "v1_student_results.csv"
    assert paths.model_summary_json == paths.output_dir / "v1_model_summary.json"
```

- [ ] **Step 2: 运行测试确认失败**

Run: `uv run --project projects/model-stubs pytest projects/model-stubs/tests/test_config.py -v`
Expected: FAIL because project files do not exist yet

- [ ] **Step 3: 创建最小 Python 工程与 CLI 壳子**

```toml
[project]
name = "student-behavior-model-stubs"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = ["pandas>=2.2"]

[dependency-groups]
dev = ["pytest>=8.0"]

[project.scripts]
student-behavior-stubs = "student_behavior_model_stubs.cli:main"
```

```python
def main(argv: list[str] | None = None) -> int:
    raise NotImplementedError("CLI is not implemented yet")
```

- [ ] **Step 4: 实现最小路径配置**

```python
@dataclass(frozen=True)
class DefaultPaths:
    output_dir: Path
    student_results_csv: Path
    student_reports_jsonl: Path
    overview_json: Path
    model_summary_json: Path
    warnings_json: Path
```

- [ ] **Step 5: 重新运行配置测试确认通过**

Run: `uv run --project projects/model-stubs pytest projects/model-stubs/tests/test_config.py -v`
Expected: PASS

- [ ] **Step 6: 提交**

```bash
git add projects/model-stubs
git commit -m "feat: scaffold model stubs project"
```

### Task 2: 固定输入读取与上游字段校验

**Files:**
- Create: `C:\Users\Orion\Desktop\StudentBehavior\projects\model-stubs\src\student_behavior_model_stubs\io.py`
- Test: `C:\Users\Orion\Desktop\StudentBehavior\projects\model-stubs\tests\test_io.py`

- [ ] **Step 1: 写输入读取和字段校验失败测试**

```python
import pandas as pd
import pytest

from student_behavior_model_stubs.io import validate_required_columns


def test_validate_required_columns_rejects_missing_fields() -> None:
    frame = pd.DataFrame({"student_id": ["1"], "term_key": ["2023-1"]})
    with pytest.raises(ValueError, match="missing required columns"):
        validate_required_columns(frame, {"student_id", "term_key", "risk_label"})
```

- [ ] **Step 2: 增加“只接受结果层输入，不直接读原始 Excel”的边界测试**

```python
def test_read_features_requires_tabular_export_not_excel_name_guessing() -> None:
    ...
```

- [ ] **Step 3: 运行测试确认失败**

Run: `uv run --project projects/model-stubs pytest projects/model-stubs/tests/test_io.py -v`
Expected: FAIL because helpers do not exist

- [ ] **Step 4: 实现最小读取与校验逻辑**

```python
REQUIRED_FEATURE_COLUMNS = {
    "student_id",
    "term_key",
    "major_name",
    "risk_label",
    "avg_course_score",
    "failed_course_count",
    "attendance_normal_rate",
}
```

- [ ] **Step 5: 增加空值兼容测试**

```python
def test_optional_draft_source_columns_may_be_null() -> None:
    ...
```

- [ ] **Step 6: 跑测试确认全部通过**

Run: `uv run --project projects/model-stubs pytest projects/model-stubs/tests/test_io.py -v`
Expected: PASS

- [ ] **Step 7: 提交**

```bash
git add projects/model-stubs/src/student_behavior_model_stubs/io.py projects/model-stubs/tests/test_io.py
git commit -m "feat: add model stub input validation"
```

### Task 3: 实现风险概率与风险等级规则

**Files:**
- Create: `C:\Users\Orion\Desktop\StudentBehavior\projects\model-stubs\src\student_behavior_model_stubs\scoring.py`
- Test: `C:\Users\Orion\Desktop\StudentBehavior\projects\model-stubs\tests\test_scoring.py`

- [ ] **Step 1: 写风险概率失败测试**

```python
def test_compute_risk_probability_is_deterministic() -> None:
    row = {
        "student_id": "20230001",
        "term_key": "2023-1",
        "risk_label": 1,
        "failed_course_count": 2,
        "avg_course_score": 61.0,
        "attendance_normal_rate": 0.42,
    }
    assert compute_risk_probability(row) == compute_risk_probability(row)
```

- [ ] **Step 2: 写风险等级阈值测试**

```python
def test_map_risk_level_respects_frozen_thresholds() -> None:
    assert map_risk_level(0.80) == "high"
    assert map_risk_level(0.50) == "medium"
    assert map_risk_level(0.30) == "low"
```

- [ ] **Step 3: 写“概率范围与保留两位小数”测试**

```python
def test_compute_risk_probability_is_clamped_and_rounded() -> None:
    ...
```

- [ ] **Step 4: 运行测试确认失败**

Run: `uv run --project projects/model-stubs pytest projects/model-stubs/tests/test_scoring.py -v`
Expected: FAIL because scoring module does not exist

- [ ] **Step 5: 实现最小风险打分**

```python
def compute_risk_probability(row: Mapping[str, object]) -> float:
    ...


def map_risk_level(probability: float) -> str:
    ...
```

- [ ] **Step 6: 增加空特征降级测试**

```python
def test_compute_risk_probability_handles_null_metrics_without_crash() -> None:
    ...
```

- [ ] **Step 7: 跑测试确认全部通过**

Run: `uv run --project projects/model-stubs pytest projects/model-stubs/tests/test_scoring.py -v`
Expected: PASS

- [ ] **Step 8: 提交**

```bash
git add projects/model-stubs/src/student_behavior_model_stubs/scoring.py projects/model-stubs/tests/test_scoring.py
git commit -m "feat: add stub risk scoring rules"
```

### Task 4: 实现四象限与维度评分规则

**Files:**
- Modify: `C:\Users\Orion\Desktop\StudentBehavior\projects\model-stubs\src\student_behavior_model_stubs\scoring.py`
- Test: `C:\Users\Orion\Desktop\StudentBehavior\projects\model-stubs\tests\test_scoring.py`

- [ ] **Step 1: 写四象限映射失败测试**

```python
def test_compute_quadrant_label_returns_frozen_enum() -> None:
    label = compute_quadrant_label(
        {
            "student_id": "20230001",
            "term_key": "2023-1",
            "attendance_normal_rate": 0.88,
            "sign_event_count": 20,
            "selected_course_count": 9,
            "avg_course_score": 86,
            "failed_course_count": 0,
            "library_visit_count": 25,
        }
    )
    assert label in {"自律共鸣型", "被动守纪型", "脱节离散型", "情绪驱动型"}
```

- [ ] **Step 2: 写维度评分结构测试**

```python
def test_build_dimension_scores_returns_four_dimensions() -> None:
    ...
```

- [ ] **Step 3: 写“分数范围和保留两位小数”测试**

```python
def test_dimension_scores_are_clamped_and_rounded() -> None:
    ...
```

- [ ] **Step 4: 运行测试确认失败**

Run: `uv run --project projects/model-stubs pytest projects/model-stubs/tests/test_scoring.py -v`
Expected: FAIL because quadrant and dimension scoring functions do not exist

- [ ] **Step 5: 实现四象限规则与 4 维评分**

```python
def compute_quadrant_label(row: Mapping[str, object]) -> str:
    ...


def build_dimension_scores(row: Mapping[str, object]) -> list[dict[str, object]]:
    ...
```

- [ ] **Step 6: 增加“空生活行为特征不崩溃”测试**

```python
def test_compute_quadrant_label_handles_missing_library_metrics() -> None:
    ...
```

- [ ] **Step 7: 跑测试确认全部通过**

Run: `uv run --project projects/model-stubs pytest projects/model-stubs/tests/test_scoring.py -v`
Expected: PASS

- [ ] **Step 8: 提交**

```bash
git add projects/model-stubs/src/student_behavior_model_stubs/scoring.py projects/model-stubs/tests/test_scoring.py
git commit -m "feat: add quadrant and dimension score stubs"
```

### Task 5: 实现解释、建议与摘要模板

**Files:**
- Create: `C:\Users\Orion\Desktop\StudentBehavior\projects\model-stubs\src\student_behavior_model_stubs\templates.py`
- Test: `C:\Users\Orion\Desktop\StudentBehavior\projects\model-stubs\tests\test_templates.py`

- [ ] **Step 1: 写 `top_factors` 结构失败测试**

```python
def test_build_top_factors_matches_api_contract_shape() -> None:
    ...
```

- [ ] **Step 2: 写 `intervention_advice` 和 `report_text` 失败测试**

```python
def test_build_report_payload_returns_readable_stub_content() -> None:
    ...
```

- [ ] **Step 3: 写“模板结果稳定且不为空”测试**

```python
def test_build_report_payload_is_deterministic() -> None:
    ...
```

- [ ] **Step 4: 运行测试确认失败**

Run: `uv run --project projects/model-stubs pytest projects/model-stubs/tests/test_templates.py -v`
Expected: FAIL because templates module does not exist

- [ ] **Step 5: 实现模板驱动解释与建议**

```python
def build_top_factors(...):
    ...


def build_report_payload(...):
    ...
```

- [ ] **Step 6: 增加“模板在低信息输入下仍能产出”测试**

```python
def test_build_report_payload_handles_sparse_dimension_scores() -> None:
    ...
```

- [ ] **Step 7: 跑测试确认全部通过**

Run: `uv run --project projects/model-stubs pytest projects/model-stubs/tests/test_templates.py -v`
Expected: PASS

- [ ] **Step 8: 提交**

```bash
git add projects/model-stubs/src/student_behavior_model_stubs/templates.py projects/model-stubs/tests/test_templates.py
git commit -m "feat: add explanation and advice templates"
```

### Task 6: 构建学生结果表与学生报告表

**Files:**
- Create: `C:\Users\Orion\Desktop\StudentBehavior\projects\model-stubs\src\student_behavior_model_stubs\build_outputs.py`
- Test: `C:\Users\Orion\Desktop\StudentBehavior\projects\model-stubs\tests\test_build_outputs.py`

- [ ] **Step 1: 写学生结果表失败测试**

```python
def test_build_student_results_outputs_contract_aligned_columns() -> None:
    ...
```

- [ ] **Step 2: 写学生报告表失败测试**

```python
def test_build_student_reports_outputs_jsonl_ready_records() -> None:
    ...
```

- [ ] **Step 3: 写 `student_name` 占位规则测试**

```python
def test_missing_student_name_falls_back_to_student_id_placeholder() -> None:
    ...
```

- [ ] **Step 4: 运行测试确认失败**

Run: `uv run --project projects/model-stubs pytest projects/model-stubs/tests/test_build_outputs.py -v`
Expected: FAIL because build outputs module does not exist

- [ ] **Step 5: 实现学生结果与学生报告构建器**

```python
def build_student_results(features: pd.DataFrame, students: pd.DataFrame | None = None) -> pd.DataFrame:
    ...


def build_student_reports(student_results: pd.DataFrame) -> list[dict[str, object]]:
    ...
```

- [ ] **Step 6: 增加“输出稳定排序”测试**

```python
def test_build_student_results_sorts_by_student_id_and_term_key() -> None:
    ...
```

- [ ] **Step 7: 跑测试确认全部通过**

Run: `uv run --project projects/model-stubs pytest projects/model-stubs/tests/test_build_outputs.py -v`
Expected: PASS

- [ ] **Step 8: 提交**

```bash
git add projects/model-stubs/src/student_behavior_model_stubs/build_outputs.py projects/model-stubs/tests/test_build_outputs.py
git commit -m "feat: build student stub outputs"
```

### Task 7: 构建总览聚合与模型摘要文件

**Files:**
- Modify: `C:\Users\Orion\Desktop\StudentBehavior\projects\model-stubs\src\student_behavior_model_stubs\build_outputs.py`
- Test: `C:\Users\Orion\Desktop\StudentBehavior\projects\model-stubs\tests\test_build_outputs.py`

- [ ] **Step 1: 写总览聚合失败测试**

```python
def test_build_overview_by_term_contains_required_sections() -> None:
    ...
```

- [ ] **Step 2: 写模型摘要失败测试**

```python
def test_build_model_summary_marks_stub_identity_and_runtime_timestamp() -> None:
    summary = build_model_summary(now=datetime(2026, 3, 27, 12, 0, tzinfo=timezone.utc))
    assert summary["cluster_method"] == "stub-quadrant-rules"
    assert summary["risk_model"] == "stub-risk-rules"
    assert summary["updated_at"] == "2026-03-27T12:00:00+00:00"
```

- [ ] **Step 3: 写“禁止保留占位符时间戳”测试**

```python
def test_model_summary_updated_at_is_not_placeholder() -> None:
    ...
```

- [ ] **Step 4: 运行测试确认失败**

Run: `uv run --project projects/model-stubs pytest projects/model-stubs/tests/test_build_outputs.py -v`
Expected: FAIL because overview/model summary builders are incomplete

- [ ] **Step 5: 实现总览聚合与模型摘要**

```python
def build_overview_by_term(student_results: pd.DataFrame) -> dict[str, object]:
    ...


def build_model_summary(*, now: datetime) -> dict[str, object]:
    ...
```

- [ ] **Step 6: 增加趋势聚合测试**

```python
def test_build_overview_by_term_includes_trend_summary() -> None:
    ...
```

- [ ] **Step 7: 跑测试确认全部通过**

Run: `uv run --project projects/model-stubs pytest projects/model-stubs/tests/test_build_outputs.py -v`
Expected: PASS

- [ ] **Step 8: 提交**

```bash
git add projects/model-stubs/src/student_behavior_model_stubs/build_outputs.py projects/model-stubs/tests/test_build_outputs.py
git commit -m "feat: add overview and model summary outputs"
```

### Task 8: 实现 warnings 产物与 CLI 主命令

**Files:**
- Create: `C:\Users\Orion\Desktop\StudentBehavior\projects\model-stubs\src\student_behavior_model_stubs\reporting.py`
- Modify: `C:\Users\Orion\Desktop\StudentBehavior\projects\model-stubs\src\student_behavior_model_stubs\cli.py`
- Test: `C:\Users\Orion\Desktop\StudentBehavior\projects\model-stubs\tests\test_cli.py`

- [ ] **Step 1: 写 warnings 失败测试**

```python
def test_build_warnings_payload_uses_runtime_generated_at() -> None:
    ...
```

- [ ] **Step 2: 写 CLI 集成失败测试**

```python
def test_cli_build_writes_all_artifacts(tmp_path: Path) -> None:
    ...
```

- [ ] **Step 3: 写“warnings 不保留 placeholder，且含空值摘要”测试**

```python
def test_warnings_payload_includes_null_metric_summary_and_real_timestamp() -> None:
    ...
```

- [ ] **Step 4: 运行测试确认失败**

Run: `uv run --project projects/model-stubs pytest projects/model-stubs/tests/test_cli.py -v`
Expected: FAIL because reporting and CLI build command are incomplete

- [ ] **Step 5: 实现 warnings 构建与 CLI**

```python
def build_warnings_payload(..., now: datetime) -> dict[str, object]:
    ...


def main(argv: list[str] | None = None) -> int:
    ...
```

- [ ] **Step 6: 跑 CLI 测试确认通过**

Run: `uv run --project projects/model-stubs pytest projects/model-stubs/tests/test_cli.py -v`
Expected: PASS

- [ ] **Step 7: 提交**

```bash
git add projects/model-stubs/src/student_behavior_model_stubs/reporting.py projects/model-stubs/src/student_behavior_model_stubs/cli.py projects/model-stubs/tests/test_cli.py
git commit -m "feat: add model stubs cli and warnings"
```

### Task 9: 全量验证与真实快照验收

**Files:**
- Verify only

- [ ] **Step 1: 运行完整测试套件**

Run: `uv run --project projects/model-stubs pytest projects/model-stubs/tests -q`
Expected: PASS

- [ ] **Step 2: 运行 CLI 构建真实产物**

Run: `uv run --project projects/model-stubs student-behavior-stubs build`
Expected: 成功写出 5 个文件到 `artifacts/model_stubs`

- [ ] **Step 3: 检查产物结构**

Manual checks:

- `v1_student_results.csv` 包含冻结字段
- `v1_student_reports.jsonl` 每行是合法 JSON
- `v1_overview_by_term.json` 含 `student_count`、`risk_distribution`、`quadrant_distribution`、`major_risk_summary`、`trend_summary`
- `v1_model_summary.json` 的 `updated_at` 不是占位符
- `v1_warnings.json` 的 `generated_at` 不是占位符

- [ ] **Step 4: 做分布合理性检查**

Manual checks:

- `risk_level` 至少出现 2 档
- 4 个 `quadrant_label` 不要求全满，但不能全部相同
- `risk_probability` 不应全部完全一致

- [ ] **Step 5: 提交**

```bash
git add projects/model-stubs
git commit -m "feat: implement offline model stubs pipeline"
```

## Review Gates

- 在 Task 4 完成后，请做一次 spec review，确认四象限和 4 维评分规则没有偏离设计文档。
- 在 Task 7 完成后，请做一次 code quality review，确认总览聚合、时间戳写入和输出结构无明显缺口。
- 在 Task 9 完成后，再做一次最终 review，然后才允许进入合并流程。

## 完成定义

当以下条件全部满足时，本计划才算完成：

- `projects/model-stubs` 作为独立子项目存在并可通过 `uv` 运行
- 4 份核心结果文件和 1 份 warnings 文件都能稳定产出
- 输出字段与 API contract 对齐
- `updated_at` 与 `generated_at` 为真实运行时值
- 测试全部通过
- 真实快照构建成功
- 结果层明确保留 `stub` 身份，没有伪装成正式模型
