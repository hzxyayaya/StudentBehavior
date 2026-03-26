# V1 Analytics Database Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 建立 V1 分析中台数据库的首版最小物理模型，打通从源表字段归一到 `student_term_features` 核心宽表的数据库链路。

**Architecture:** 采用 PostgreSQL 风格的分层设计，但首版只在数据库内实现标准化层和分析层。原始 Excel 继续保留为文件侧证据源，数据库聚焦于 4 个核心识别维度所需的维度表、事实表和一张学期级分析宽表。

**Tech Stack:** PostgreSQL、Python、uv、pytest、SQL migration files、CSV/Excel ETL utilities

---

## File Structure

本计划默认实现代码放在新的独立子项目 `projects/analytics-db`，不要继续堆在仓库根目录或 `projects/semester-etl` 内。

建议目录结构：

- Create: `projects/analytics-db/pyproject.toml`
- Create: `projects/analytics-db/src/student_behavior_analytics_db/__init__.py`
- Create: `projects/analytics-db/src/student_behavior_analytics_db/config.py`
- Create: `projects/analytics-db/src/student_behavior_analytics_db/db.py`
- Create: `projects/analytics-db/src/student_behavior_analytics_db/normalize_ids.py`
- Create: `projects/analytics-db/src/student_behavior_analytics_db/normalize_terms.py`
- Create: `projects/analytics-db/src/student_behavior_analytics_db/source_catalog.py`
- Create: `projects/analytics-db/src/student_behavior_analytics_db/load_students.py`
- Create: `projects/analytics-db/src/student_behavior_analytics_db/load_terms.py`
- Create: `projects/analytics-db/src/student_behavior_analytics_db/load_courses.py`
- Create: `projects/analytics-db/src/student_behavior_analytics_db/load_majors.py`
- Create: `projects/analytics-db/src/student_behavior_analytics_db/load_fact_enrollments.py`
- Create: `projects/analytics-db/src/student_behavior_analytics_db/load_fact_grades.py`
- Create: `projects/analytics-db/src/student_behavior_analytics_db/load_fact_attendance.py`
- Create: `projects/analytics-db/src/student_behavior_analytics_db/load_fact_signins.py`
- Create: `projects/analytics-db/src/student_behavior_analytics_db/load_fact_assignments.py`
- Create: `projects/analytics-db/src/student_behavior_analytics_db/load_fact_exams.py`
- Create: `projects/analytics-db/src/student_behavior_analytics_db/load_fact_tasks.py`
- Create: `projects/analytics-db/src/student_behavior_analytics_db/load_fact_discussions.py`
- Create: `projects/analytics-db/src/student_behavior_analytics_db/load_fact_library.py`
- Create: `projects/analytics-db/src/student_behavior_analytics_db/load_fact_running.py`
- Create: `projects/analytics-db/src/student_behavior_analytics_db/load_fact_evaluation_labels.py`
- Create: `projects/analytics-db/src/student_behavior_analytics_db/build_student_term_features.py`
- Create: `projects/analytics-db/src/student_behavior_analytics_db/cli.py`
- Create: `projects/analytics-db/sql/001_create_dimensions.sql`
- Create: `projects/analytics-db/sql/002_create_fact_tables.sql`
- Create: `projects/analytics-db/sql/003_create_student_term_features.sql`
- Create: `projects/analytics-db/sql/004_indexes.sql`
- Create: `projects/analytics-db/tests/test_normalize_ids.py`
- Create: `projects/analytics-db/tests/test_normalize_terms.py`
- Create: `projects/analytics-db/tests/test_load_students.py`
- Create: `projects/analytics-db/tests/test_load_terms.py`
- Create: `projects/analytics-db/tests/test_load_fact_grades.py`
- Create: `projects/analytics-db/tests/test_load_fact_attendance.py`
- Create: `projects/analytics-db/tests/test_load_fact_signins.py`
- Create: `projects/analytics-db/tests/test_load_fact_assignments.py`
- Create: `projects/analytics-db/tests/test_load_fact_exams.py`
- Create: `projects/analytics-db/tests/test_load_fact_tasks.py`
- Create: `projects/analytics-db/tests/test_load_fact_discussions.py`
- Create: `projects/analytics-db/tests/test_load_fact_library.py`
- Create: `projects/analytics-db/tests/test_load_fact_running.py`
- Create: `projects/analytics-db/tests/test_load_fact_evaluation_labels.py`
- Create: `projects/analytics-db/tests/test_build_student_term_features.py`
- Create: `projects/analytics-db/tests/test_cli.py`
- Create: `docs/database-source-to-table-mapping.md`
- Create: `docs/student-term-features-metric-rules.md`

## Implementation Notes

- 严格以 [2026-03-26-v1-analytics-database-design.md](C:/Users/Orion/Desktop/StudentBehavior/docs/superpowers/specs/2026-03-26-v1-analytics-database-design.md) 为准。
- 首版仅接入以下源表：
  - `学生基本信息.xlsx`
  - `学生选课信息.xlsx`
  - `课程信息.xlsx`
  - `学生成绩.xlsx`
  - `本科生综合测评.xlsx`
  - `考勤汇总.xlsx`
  - `学生签到记录.xlsx`
  - `学生作业提交记录.xlsx`
  - `考试提交记录.xlsx`
  - `课堂任务参与.xlsx`
  - `讨论记录.xlsx`
  - `图书馆打卡记录.xlsx`
  - `跑步打卡.xlsx`
- 明确排除首版核心链路：
  - `上网统计.xlsx`
  - `门禁数据.xlsx`
  - `毕业去向.xlsx`
  - `奖学金获奖.xlsx`
  - `学籍异动.xlsx`
- 允许确定性归一，不允许猜测性学期推断。
- 所有事实表都要保留：
  - `student_id`
  - `term_key`
  - `source_file`
  - `source_row_hash`

### Task 1: 搭建独立数据库子项目骨架

**Files:**
- Create: `projects/analytics-db/pyproject.toml`
- Create: `projects/analytics-db/src/student_behavior_analytics_db/__init__.py`
- Create: `projects/analytics-db/src/student_behavior_analytics_db/config.py`
- Create: `projects/analytics-db/src/student_behavior_analytics_db/db.py`
- Create: `projects/analytics-db/src/student_behavior_analytics_db/cli.py`
- Test: `projects/analytics-db/tests/test_cli.py`

- [ ] **Step 1: 写 CLI 和配置加载失败测试**

```python
def test_cli_has_bootstrap_command():
    ...
```

- [ ] **Step 2: 运行测试确认失败**

Run: `uv run --project projects/analytics-db pytest projects/analytics-db/tests/test_cli.py -v`
Expected: FAIL because project files and CLI are not present

- [ ] **Step 3: 创建最小 Python 工程和 CLI 骨架**

```python
def main() -> int:
    return 0
```

- [ ] **Step 4: 运行测试确认通过**

Run: `uv run --project projects/analytics-db pytest projects/analytics-db/tests/test_cli.py -v`
Expected: PASS

- [ ] **Step 5: 提交**

```bash
git add projects/analytics-db
git commit -m "feat: scaffold analytics database project"
```

### Task 2: 实现统一主键和学期归一模块

**Files:**
- Create: `projects/analytics-db/src/student_behavior_analytics_db/normalize_ids.py`
- Create: `projects/analytics-db/src/student_behavior_analytics_db/normalize_terms.py`
- Test: `projects/analytics-db/tests/test_normalize_ids.py`
- Test: `projects/analytics-db/tests/test_normalize_terms.py`

- [ ] **Step 1: 写 `student_id` 归一失败测试**

```python
def test_normalize_student_id_accepts_known_alias_fields():
    assert normalize_student_id(" pjxyqxbj337 ") == "pjxyqxbj337"
```

- [ ] **Step 2: 写 `term_key` 归一失败测试**

```python
def test_normalize_term_key_from_school_year_and_term_no():
    assert normalize_term_key("2024-2025", 1) == "2024-1"
```

- [ ] **Step 3: 运行测试确认失败**

Run: `uv run --project projects/analytics-db pytest projects/analytics-db/tests/test_normalize_ids.py projects/analytics-db/tests/test_normalize_terms.py -v`
Expected: FAIL because normalization functions do not exist

- [ ] **Step 4: 实现最小归一逻辑**

```python
def normalize_student_id(raw: object) -> str | None:
    ...

def normalize_term_key(raw_year: object, raw_term: object) -> str | None:
    ...
```

- [ ] **Step 5: 增加“允许确定性归一，不允许猜测性推断”的边界测试**

```python
def test_guess_based_term_inference_is_rejected():
    assert infer_term_from_month_only("2023-03-01") is None
```

- [ ] **Step 6: 跑测试确认全部通过**

Run: `uv run --project projects/analytics-db pytest projects/analytics-db/tests/test_normalize_ids.py projects/analytics-db/tests/test_normalize_terms.py -v`
Expected: PASS

- [ ] **Step 7: 提交**

```bash
git add projects/analytics-db/src/student_behavior_analytics_db/normalize_ids.py projects/analytics-db/src/student_behavior_analytics_db/normalize_terms.py projects/analytics-db/tests/test_normalize_ids.py projects/analytics-db/tests/test_normalize_terms.py
git commit -m "feat: add id and term normalization"
```

### Task 3: 定义首版数据库 DDL

**Files:**
- Create: `projects/analytics-db/sql/001_create_dimensions.sql`
- Create: `projects/analytics-db/sql/002_create_fact_tables.sql`
- Create: `projects/analytics-db/sql/003_create_student_term_features.sql`
- Create: `projects/analytics-db/sql/004_indexes.sql`
- Modify: `projects/analytics-db/src/student_behavior_analytics_db/db.py`
- Test: `projects/analytics-db/tests/test_cli.py`

- [ ] **Step 1: 写 DDL 存在性和表名集合测试**

```python
EXPECTED_TABLES = {
    "students",
    "terms",
    "courses",
    "majors",
    "student_course_enrollments",
    "student_grade_records",
    "student_attendance_records",
    "student_signin_events",
    "student_assignment_submissions",
    "student_exam_submissions",
    "student_task_participation",
    "student_discussion_events",
    "student_library_visits",
    "student_running_events",
    "student_evaluation_labels",
    "student_term_features",
}
```

- [ ] **Step 2: 运行测试确认失败**

Run: `uv run --project projects/analytics-db pytest projects/analytics-db/tests/test_cli.py -v`
Expected: FAIL because migration SQL files do not exist

- [ ] **Step 3: 写最小 SQL DDL**

```sql
create table students (
  student_id text primary key,
  gender text,
  ethnicity text,
  political_status text,
  major_name text,
  college_name text,
  class_name text,
  enrollment_year integer
);
```

- [ ] **Step 4: 为事实表补齐统一追溯字段**

```sql
source_file text not null,
source_row_hash text not null
```

- [ ] **Step 5: 为 `student_term_features` 建主键和索引**

```sql
primary key (student_id, term_key)
```

- [ ] **Step 6: 跑测试确认通过**

Run: `uv run --project projects/analytics-db pytest projects/analytics-db/tests/test_cli.py -v`
Expected: PASS

- [ ] **Step 7: 提交**

```bash
git add projects/analytics-db/sql projects/analytics-db/src/student_behavior_analytics_db/db.py projects/analytics-db/tests/test_cli.py
git commit -m "feat: add analytics database ddl"
```

### Task 4: 实现学生、学期、专业、课程维度加载器

**Files:**
- Create: `projects/analytics-db/src/student_behavior_analytics_db/load_students.py`
- Create: `projects/analytics-db/src/student_behavior_analytics_db/load_terms.py`
- Create: `projects/analytics-db/src/student_behavior_analytics_db/load_courses.py`
- Create: `projects/analytics-db/src/student_behavior_analytics_db/load_majors.py`
- Test: `projects/analytics-db/tests/test_load_students.py`
- Test: `projects/analytics-db/tests/test_load_terms.py`

- [ ] **Step 1: 写 `students` 加载失败测试**

```python
def test_load_students_keeps_minimal_profile_columns():
    ...
```

- [ ] **Step 2: 写 `terms` 加载失败测试**

```python
def test_load_terms_builds_term_rows_from_known_school_year_formats():
    ...
```

- [ ] **Step 3: 运行测试确认失败**

Run: `uv run --project projects/analytics-db pytest projects/analytics-db/tests/test_load_students.py projects/analytics-db/tests/test_load_terms.py -v`
Expected: FAIL because loaders do not exist

- [ ] **Step 4: 实现学生维度加载器**

```python
def load_students(...):
    return pd.DataFrame(...)
```

- [ ] **Step 5: 实现学期维度加载器**

```python
def load_terms(...):
    return pd.DataFrame(...)
```

- [ ] **Step 6: 运行测试确认通过**

Run: `uv run --project projects/analytics-db pytest projects/analytics-db/tests/test_load_students.py projects/analytics-db/tests/test_load_terms.py -v`
Expected: PASS

- [ ] **Step 7: 提交**

```bash
git add projects/analytics-db/src/student_behavior_analytics_db/load_students.py projects/analytics-db/src/student_behavior_analytics_db/load_terms.py projects/analytics-db/src/student_behavior_analytics_db/load_courses.py projects/analytics-db/src/student_behavior_analytics_db/load_majors.py projects/analytics-db/tests/test_load_students.py projects/analytics-db/tests/test_load_terms.py
git commit -m "feat: add dimension loaders"
```

### Task 5: 实现课程与学业表现事实表

**Files:**
- Create: `projects/analytics-db/src/student_behavior_analytics_db/load_fact_enrollments.py`
- Create: `projects/analytics-db/src/student_behavior_analytics_db/load_fact_grades.py`
- Create: `projects/analytics-db/src/student_behavior_analytics_db/load_fact_evaluation_labels.py`
- Test: `projects/analytics-db/tests/test_load_fact_grades.py`
- Test: `projects/analytics-db/tests/test_load_fact_evaluation_labels.py`

- [ ] **Step 1: 写选课事实加载失败测试**

```python
def test_load_enrollments_normalizes_student_id_and_term_key():
    ...
```

- [ ] **Step 2: 写成绩事实加载失败测试**

```python
def test_load_grade_records_preserves_score_and_gpa_fields():
    ...
```

- [ ] **Step 3: 写评价标签事实加载失败测试**

```python
def test_load_evaluation_labels_builds_risk_label_from_frozen_rule():
    ...
```

- [ ] **Step 4: 运行测试确认失败**

Run: `uv run --project projects/analytics-db pytest projects/analytics-db/tests/test_load_fact_grades.py projects/analytics-db/tests/test_load_fact_evaluation_labels.py -v`
Expected: FAIL

- [ ] **Step 5: 实现三张事实表加载器**

```python
def load_fact_enrollments(...):
    ...

def load_fact_grades(...):
    ...

def load_fact_evaluation_labels(...):
    ...
```

- [ ] **Step 6: 跑测试确认通过**

Run: `uv run --project projects/analytics-db pytest projects/analytics-db/tests/test_load_fact_grades.py projects/analytics-db/tests/test_load_fact_evaluation_labels.py -v`
Expected: PASS

- [ ] **Step 7: 提交**

```bash
git add projects/analytics-db/src/student_behavior_analytics_db/load_fact_enrollments.py projects/analytics-db/src/student_behavior_analytics_db/load_fact_grades.py projects/analytics-db/src/student_behavior_analytics_db/load_fact_evaluation_labels.py projects/analytics-db/tests/test_load_fact_grades.py projects/analytics-db/tests/test_load_fact_evaluation_labels.py
git commit -m "feat: add academic fact loaders"
```

### Task 6: 实现课堂投入事实表

**Files:**
- Create: `projects/analytics-db/src/student_behavior_analytics_db/load_fact_attendance.py`
- Create: `projects/analytics-db/src/student_behavior_analytics_db/load_fact_signins.py`
- Test: `projects/analytics-db/tests/test_load_fact_attendance.py`
- Test: `projects/analytics-db/tests/test_load_fact_signins.py`

- [ ] **Step 1: 写考勤事实加载失败测试**

```python
def test_load_attendance_records_maps_xn_xq_to_term_key():
    ...
```

- [ ] **Step 2: 写签到事实加载失败测试**

```python
def test_load_signin_events_uses_deterministic_timestamp_mapping_only():
    ...
```

- [ ] **Step 3: 运行测试确认失败**

Run: `uv run --project projects/analytics-db pytest projects/analytics-db/tests/test_load_fact_attendance.py projects/analytics-db/tests/test_load_fact_signins.py -v`
Expected: FAIL

- [ ] **Step 4: 实现两张事实表加载器**

```python
def load_fact_attendance(...):
    ...

def load_fact_signins(...):
    ...
```

- [ ] **Step 5: 跑测试确认通过**

Run: `uv run --project projects/analytics-db pytest projects/analytics-db/tests/test_load_fact_attendance.py projects/analytics-db/tests/test_load_fact_signins.py -v`
Expected: PASS

- [ ] **Step 6: 提交**

```bash
git add projects/analytics-db/src/student_behavior_analytics_db/load_fact_attendance.py projects/analytics-db/src/student_behavior_analytics_db/load_fact_signins.py projects/analytics-db/tests/test_load_fact_attendance.py projects/analytics-db/tests/test_load_fact_signins.py
git commit -m "feat: add engagement fact loaders"
```

### Task 7: 实现学习行为活跃事实表

**Files:**
- Create: `projects/analytics-db/src/student_behavior_analytics_db/load_fact_assignments.py`
- Create: `projects/analytics-db/src/student_behavior_analytics_db/load_fact_exams.py`
- Create: `projects/analytics-db/src/student_behavior_analytics_db/load_fact_tasks.py`
- Create: `projects/analytics-db/src/student_behavior_analytics_db/load_fact_discussions.py`
- Test: `projects/analytics-db/tests/test_load_fact_assignments.py`
- Test: `projects/analytics-db/tests/test_load_fact_exams.py`
- Test: `projects/analytics-db/tests/test_load_fact_tasks.py`
- Test: `projects/analytics-db/tests/test_load_fact_discussions.py`

- [ ] **Step 1: 写四张学习行为事实表失败测试**

```python
def test_load_assignments_keeps_submit_events():
    ...
```

- [ ] **Step 2: 运行测试确认失败**

Run: `uv run --project projects/analytics-db pytest projects/analytics-db/tests/test_load_fact_assignments.py projects/analytics-db/tests/test_load_fact_exams.py projects/analytics-db/tests/test_load_fact_tasks.py projects/analytics-db/tests/test_load_fact_discussions.py -v`
Expected: FAIL

- [ ] **Step 3: 实现四张事实表加载器**

```python
def load_fact_assignments(...):
    ...
```

- [ ] **Step 4: 跑测试确认通过**

Run: `uv run --project projects/analytics-db pytest projects/analytics-db/tests/test_load_fact_assignments.py projects/analytics-db/tests/test_load_fact_exams.py projects/analytics-db/tests/test_load_fact_tasks.py projects/analytics-db/tests/test_load_fact_discussions.py -v`
Expected: PASS

- [ ] **Step 5: 提交**

```bash
git add projects/analytics-db/src/student_behavior_analytics_db/load_fact_assignments.py projects/analytics-db/src/student_behavior_analytics_db/load_fact_exams.py projects/analytics-db/src/student_behavior_analytics_db/load_fact_tasks.py projects/analytics-db/src/student_behavior_analytics_db/load_fact_discussions.py projects/analytics-db/tests/test_load_fact_assignments.py projects/analytics-db/tests/test_load_fact_exams.py projects/analytics-db/tests/test_load_fact_tasks.py projects/analytics-db/tests/test_load_fact_discussions.py
git commit -m "feat: add learning activity fact loaders"
```

### Task 8: 实现生活规律与资源使用事实表

**Files:**
- Create: `projects/analytics-db/src/student_behavior_analytics_db/load_fact_library.py`
- Create: `projects/analytics-db/src/student_behavior_analytics_db/load_fact_running.py`
- Test: `projects/analytics-db/tests/test_load_fact_library.py`
- Test: `projects/analytics-db/tests/test_load_fact_running.py`

- [ ] **Step 1: 写图书馆事实加载失败测试**

```python
def test_load_library_visits_maps_cardid_to_student_id():
    ...
```

- [ ] **Step 2: 写跑步事实加载失败测试**

```python
def test_load_running_events_uses_usernum_and_term_id_without_guessing():
    ...
```

- [ ] **Step 3: 运行测试确认失败**

Run: `uv run --project projects/analytics-db pytest projects/analytics-db/tests/test_load_fact_library.py projects/analytics-db/tests/test_load_fact_running.py -v`
Expected: FAIL

- [ ] **Step 4: 实现两张事实表加载器**

```python
def load_fact_library(...):
    ...

def load_fact_running(...):
    ...
```

- [ ] **Step 5: 跑测试确认通过**

Run: `uv run --project projects/analytics-db pytest projects/analytics-db/tests/test_load_fact_library.py projects/analytics-db/tests/test_load_fact_running.py -v`
Expected: PASS

- [ ] **Step 6: 提交**

```bash
git add projects/analytics-db/src/student_behavior_analytics_db/load_fact_library.py projects/analytics-db/src/student_behavior_analytics_db/load_fact_running.py projects/analytics-db/tests/test_load_fact_library.py projects/analytics-db/tests/test_load_fact_running.py
git commit -m "feat: add routine fact loaders"
```

### Task 9: 构建 `student_term_features` 核心宽表

**Files:**
- Create: `projects/analytics-db/src/student_behavior_analytics_db/build_student_term_features.py`
- Test: `projects/analytics-db/tests/test_build_student_term_features.py`
- Create: `docs/student-term-features-metric-rules.md`

- [ ] **Step 1: 写核心宽表失败测试**

```python
def test_build_student_term_features_outputs_expected_columns():
    expected = {
        "student_id",
        "term_key",
        "major_name",
        "college_name",
        "avg_course_score",
        "failed_course_count",
        "avg_gpa",
        "major_rank_pct",
        "risk_label",
        "attendance_record_count",
        "attendance_normal_rate",
        "selected_course_count",
        "sign_event_count",
        "assignment_submit_count",
        "exam_submit_count",
        "task_participation_rate",
        "discussion_reply_count",
        "library_visit_count",
        "library_active_days",
        "running_punch_count",
        "morning_activity_rate",
    }
    ...
```

- [ ] **Step 2: 运行测试确认失败**

Run: `uv run --project projects/analytics-db pytest projects/analytics-db/tests/test_build_student_term_features.py -v`
Expected: FAIL

- [ ] **Step 3: 实现最小聚合构建器**

```python
def build_student_term_features(...):
    return features
```

- [ ] **Step 4: 写指标规则说明文档**

内容至少覆盖：
- 每个指标来自哪张事实表
- 聚合公式
- 空值处理
- 排除规则

- [ ] **Step 5: 跑测试确认通过**

Run: `uv run --project projects/analytics-db pytest projects/analytics-db/tests/test_build_student_term_features.py -v`
Expected: PASS

- [ ] **Step 6: 提交**

```bash
git add projects/analytics-db/src/student_behavior_analytics_db/build_student_term_features.py projects/analytics-db/tests/test_build_student_term_features.py docs/student-term-features-metric-rules.md
git commit -m "feat: build student term feature mart"
```

### Task 10: 打通 CLI、加载顺序和数据库写入

**Files:**
- Modify: `projects/analytics-db/src/student_behavior_analytics_db/cli.py`
- Modify: `projects/analytics-db/src/student_behavior_analytics_db/db.py`
- Test: `projects/analytics-db/tests/test_cli.py`

- [ ] **Step 1: 写端到端 CLI 失败测试**

```python
def test_cli_runs_dimension_fact_and_mart_pipeline():
    ...
```

- [ ] **Step 2: 运行测试确认失败**

Run: `uv run --project projects/analytics-db pytest projects/analytics-db/tests/test_cli.py -v`
Expected: FAIL

- [ ] **Step 3: 实现数据库初始化和加载顺序**

顺序固定为：
1. 维度表
2. 事实表
3. `student_term_features`

- [ ] **Step 4: 跑测试确认通过**

Run: `uv run --project projects/analytics-db pytest projects/analytics-db/tests/test_cli.py -v`
Expected: PASS

- [ ] **Step 5: 提交**

```bash
git add projects/analytics-db/src/student_behavior_analytics_db/cli.py projects/analytics-db/src/student_behavior_analytics_db/db.py projects/analytics-db/tests/test_cli.py
git commit -m "feat: wire analytics database pipeline"
```

### Task 11: 补齐源表到数据库表的映射文档

**Files:**
- Create: `docs/database-source-to-table-mapping.md`

- [ ] **Step 1: 写映射文档**

文档至少覆盖：
- 每张首版源表映射到哪个维度表或事实表
- 原字段名到标准字段名的对应关系
- 哪些表被排除以及原因

- [ ] **Step 2: 自检文档与 spec 一致**

人工核对：
- 源表范围一致
- 排除项一致
- 核心宽表字段一致

- [ ] **Step 3: 提交**

```bash
git add docs/database-source-to-table-mapping.md
git commit -m "docs: add source to database mapping"
```

### Task 12: 全量验证

**Files:**
- Verify only

- [ ] **Step 1: 跑单元与组件测试**

Run: `uv run --project projects/analytics-db pytest projects/analytics-db/tests -q`
Expected: PASS

- [ ] **Step 2: 跑一次 CLI 全链路**

Run: `uv run --project projects/analytics-db python -m student_behavior_analytics_db.cli`
Expected: 成功创建维度表、事实表和 `student_term_features`

- [ ] **Step 3: 核对数据库核心表存在**

至少核对：
- `students`
- `terms`
- `student_grade_records`
- `student_attendance_records`
- `student_term_features`

- [ ] **Step 4: 核对 `student_term_features` 列完整**

Expected: 至少包含 spec 冻结的 4 个维度所需字段

- [ ] **Step 5: 最终提交**

```bash
git add .
git commit -m "feat: implement v1 analytics database baseline"
```

