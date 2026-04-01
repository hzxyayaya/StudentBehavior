# V1 Demo Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

> **Note (2026-03-28):** 本文是历史收口计划。文中的 `.worktrees/v1-demo-api` 路径保留当时执行上下文；当前运行入口请以 `projects/demo-api` 和 `docs/v1-demo-runbook.md` 为准。

**Goal:** 对当前 V1 Demo 主链路做一次问题收口，解决 `demo-api` 的真实行为偏差、清理联调残留、统一 `model-stubs` 的主线状态，并补一份可复现的运行说明，让项目前后端可以在稳定边界上继续开发。

**Architecture:** 本轮不新增业务能力，不扩新数据源，不改 API contract。本轮只做“收口”工作：修正 `demo-api` 对真实离线产物的读取行为，清理工作树与运行态残留，明确 `model-stubs` 的代码归属和交付状态，并把当前 Demo 的运行顺序、真实 term、真实 student_id 与 stub 边界写成文档。

**Tech Stack:** Python 3.12+, `uv`, `fastapi`, `pytest`, `git`, PowerShell

---

## 实施前文件地图

### 重点修改范围

- `C:\Users\Orion\Desktop\StudentBehavior\.worktrees\v1-demo-api\projects\demo-api\src\student_behavior_demo_api\services.py`
- `C:\Users\Orion\Desktop\StudentBehavior\.worktrees\v1-demo-api\projects\demo-api\tests\test_services.py`
- `C:\Users\Orion\Desktop\StudentBehavior\.worktrees\v1-demo-api\projects\demo-api\tests\test_api.py`
- `C:\Users\Orion\Desktop\StudentBehavior\projects\model-stubs\...`
- `C:\Users\Orion\Desktop\StudentBehavior\docs\...`

### 运行与验证会涉及的路径

- `C:\Users\Orion\Desktop\StudentBehavior\.worktrees\v1-demo-api\artifacts\model_stubs\`
- `C:\Users\Orion\Desktop\StudentBehavior\.worktrees\v1-model-stubs\artifacts\model_stubs\`
- `C:\Users\Orion\Desktop\StudentBehavior\artifacts\model_stubs\`

## 全局约束

- 本轮只做收口，不新增接口，不扩新字段，不改 contract。
- 优先修正“真实产物能表达，但 API 当前读不出来”的问题。
- 清理联调残留时，不删除任何应纳入版本控制的源码文件。
- 不把临时复制的真实产物误提交进代码分支。
- `model-stubs` 若仍暂不合并，也必须把其当前状态整理到“可说明、可测试、可提交”。
- 所有“完成”结论必须带验证命令和结果。

### Task 1: 修正 `overview` 的多学期支持

**Files:**
- Update: `C:\Users\Orion\Desktop\StudentBehavior\.worktrees\v1-demo-api\projects\demo-api\src\student_behavior_demo_api\services.py`
- Update: `C:\Users\Orion\Desktop\StudentBehavior\.worktrees\v1-demo-api\projects\demo-api\tests\test_services.py`
- Update: `C:\Users\Orion\Desktop\StudentBehavior\.worktrees\v1-demo-api\projects\demo-api\tests\test_api.py`

- [ ] **Step 1: 先写失败测试，锁定多学期行为**

新增测试覆盖：
- `get_overview("2023-2")` 可返回
- `get_overview("2024-1")` 可返回
- `get_overview("2024-2")` 可返回
- 未知 term 仍返回 `404`

- [ ] **Step 2: 运行局部测试确认当前实现失败**

Run:
`uv run --project .worktrees/v1-demo-api/projects/demo-api pytest .worktrees/v1-demo-api/projects/demo-api/tests/test_services.py -k overview -v`

Expected:
至少有一条较早学期 overview 测试失败，证明当前逻辑仍只认一个 term。

- [ ] **Step 3: 调整 `DemoApiStore.get_overview` 逻辑**

实现要求：
- 不再把 overview 绑定到单一推断 term
- 对真实 `v1_overview_by_term.json` 结构做兼容读取
- 若产物只有一份全局总览，也至少要基于 `trend_summary.terms` 识别有效 term
- 只有真正不存在的 term 才返回 `KeyError(term)`

- [ ] **Step 4: 补 API 级测试**

新增 `GET /api/analytics/overview?term=2023-2`、`2024-1`、`2024-2` 的成功断言。

- [ ] **Step 5: 跑 `demo-api` 全量测试**

Run:
`uv run --project .worktrees/v1-demo-api/projects/demo-api pytest .worktrees/v1-demo-api/projects/demo-api/tests -q`

Expected:
全绿。

### Task 2: 清理 `demo-api` 联调残留与运行态污染

**Files:**
- No tracked code changes expected by default
- May remove temporary runtime artifacts under:
  - `C:\Users\Orion\Desktop\StudentBehavior\.worktrees\v1-demo-api\artifacts\`
  - `C:\Users\Orion\Desktop\StudentBehavior\.worktrees\v1-demo-api\projects\demo-api\uv.lock`

- [ ] **Step 1: 盘点当前 worktree 脏状态**

Run:
- `git -C .worktrees/v1-demo-api status --short`
- 记录未跟踪的 `artifacts/`、`uv.lock`、`__pycache__` 等内容

- [ ] **Step 2: 结束残留联调进程**

Run:
- 检查仍在运行的 `uv` / `uvicorn` 进程
- 停掉只用于本轮联调的残留进程

Expected:
不再有本轮残留的 API 进程长期占端口。

- [ ] **Step 3: 清理临时联调产物**

要求：
- 删除仅为真实联调复制进 worktree 的 `artifacts/model_stubs`
- 删除生成型残留如 `uv.lock`、`__pycache__`、`.egg-info`（若存在）
- 不删除应保留的源码或测试文件

- [ ] **Step 4: 复核 worktree 状态**

Run:
`git -C .worktrees/v1-demo-api status --short`

Expected:
worktree 恢复到干净或仅保留你明确允许的内容。

### Task 3: 统一 `model-stubs` 的主线状态

**Files:**
- `C:\Users\Orion\Desktop\StudentBehavior\projects\model-stubs\...`
- `C:\Users\Orion\Desktop\StudentBehavior\docs\superpowers\specs\2026-03-27-v1-model-stubs-design.md`
- `C:\Users\Orion\Desktop\StudentBehavior\docs\superpowers\plans\2026-03-27-v1-model-stubs.md`

- [ ] **Step 1: 盘点 `main` 下 `model-stubs` 当前真实状态**

Run:
- `git status --short`
- `uv run --project projects/model-stubs pytest projects/model-stubs/tests -q`

记录：
- 哪些文件还是未跟踪
- 哪些是源码
- 哪些是运行残留

- [ ] **Step 2: 清理不该进入交付面的文件**

目标：
- 清掉 `.venv`、`.pytest_cache`、`__pycache__` 等运行型目录
- 保留源码、测试、`pyproject.toml`、`uv.lock`

- [ ] **Step 3: 明确 `model-stubs` 是否已达到“可提交状态”**

输出结论必须包含：
- 是否代码完整
- 是否测试通过
- 是否仍依赖 worktree 内临时产物
- 当前为什么还没并回 `main`

- [ ] **Step 4: 若仍暂不合并，补状态说明**

至少在当前沟通或文档中明确：
- `model-stubs` 是有效实现，不是草稿
- 当前主工作区为何出现未跟踪状态
- 后续合并前还差什么

### Task 4: 补一份当前 Demo 主链路运行说明

**Files:**
- Create: `C:\Users\Orion\Desktop\StudentBehavior\docs\v1-demo-runbook.md`

- [ ] **Step 1: 写运行顺序**

必须写清：
- `projects/semester-etl`
- `projects/analytics-db`
- `projects/model-stubs`
- `projects/demo-api`

各自的作用和先后关系。

- [ ] **Step 2: 写当前真实联调值**

必须写清：
- 可用 term：`2023-2`、`2024-1`、`2024-2`
- 示例学生：`pjwrqxbj901`
- 旧示例 `2023-1` / `20230001` 当前为什么不可用

- [ ] **Step 3: 写 stub 边界**

必须明确说明当前仍是 stub/规则版的字段：
- `risk_probability`
- `risk_level`
- `quadrant_label`
- `top_factors`
- `intervention_advice`

- [ ] **Step 4: 写最小运行命令**

至少包含：
- 测试命令
- API 启动命令
- 联调前需要准备哪些产物

### Task 5: 统一收尾验证

**Files:**
- No code changes required by default

- [ ] **Step 1: 验证 `demo-api`**

Run:
`uv run --project .worktrees/v1-demo-api/projects/demo-api pytest .worktrees/v1-demo-api/projects/demo-api/tests -q`

- [ ] **Step 2: 验证 `model-stubs`**

Run:
`uv run --project projects/model-stubs pytest projects/model-stubs/tests -q`

- [ ] **Step 3: 用真实产物做 6 个核心接口联调**

至少验证：
- `POST /api/auth/demo-login`
- `GET /api/analytics/overview`
- `GET /api/analytics/quadrants`
- `GET /api/warnings`
- `GET /api/students/{student_id}/profile`
- `GET /api/students/{student_id}/report`
- `GET /api/models/summary`

使用当前真实存在的 term 和 student_id。

- [ ] **Step 4: 记录最终状态**

必须明确：
- `main` 是否干净
- `codex/v1-demo-api` 是否干净
- `projects/model-stubs` 是否已收成可交付状态
- 当前是否适合进入前端联调

## 完成定义

本轮只有在以下条件全部满足时才算完成：

- `overview` 不再错误拒绝真实已存在的较早学期
- `demo-api` worktree 不再残留本轮临时联调污染
- `model-stubs` 状态明确，不再处于“代码存在但主线状态模糊”
- 运行说明文档已落地
- `demo-api` 与 `model-stubs` 测试都通过
- 真实产物联调命令已记录且可复现

## 推荐执行方式

优先使用 `subagent-driven-development`。

执行顺序建议固定为：
1. Task 1
2. Task 2
3. Task 3
4. Task 4
5. Task 5

不要并行修改 `demo-api` 和 `model-stubs` 的同一交付状态说明，避免再次出现“代码状态与主线认知不一致”。
