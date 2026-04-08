# Dev Startup

Last Updated: 2026-04-08

## 目标

给新开发者一个基于当前仓库的最小启动入口，优先保证能读懂结构、跑通验证命令、启动演示链路。

## 当前分支约定

- 稳定主线分支：`main`
- 当前最新演示开发分支：`codex/academic-risk-warning`
- 新任务不要直接在 `main` 上开发；从最新业务分支切出自己的 `codex/<task-name>` 分支，完成后通过 PR 合回目标分支

## 仓库结构

当前工作区内的核心子项目都在 `projects/` 下：

- `projects/semester-etl`：从原始 Excel 生成学期宽表
- `projects/analytics-db`：构建分析底座与 demo 特征
- `projects/model-stubs`：把特征转换为可演示的规则版结果
- `projects/demo-api`：读取离线结果文件并提供只读 API
- `projects/demo-web`：当前前端 Demo

## 建议启动顺序

先验证，再启动：

```powershell
uv run --project projects/semester-etl pytest projects/semester-etl/tests -q
uv run --project projects/analytics-db pytest projects/analytics-db/tests -q
uv run --project projects/model-stubs pytest projects/model-stubs/tests -q
uv run --project projects/demo-api pytest projects/demo-api/tests -q
cd projects/demo-web
npm install
npm run test
npm run build
```

如果只想快速跑通当前 Demo 主链路，按下面顺序：

```powershell
uv run --project projects/analytics-db analytics-db build-demo-features
uv run --project projects/model-stubs student-behavior-stubs build artifacts/semester_features/v1_semester_features.csv --output-dir artifacts/model_stubs
uv run --project projects/demo-api uvicorn student_behavior_demo_api.main:app --reload
cd projects/demo-web
npm install
npm run dev
```

## 当前联调口径

- 可用 `term`：`2023-2`、`2024-1`、`2024-2`
- 默认学期：`2024-2`
- 示例学生：`pjwrqxbj901`
- `demo-api` 只读取 `artifacts/model_stubs/` 下的离线结果文件

## 开发规则

1. 先读 `docs/handoff.md`、`docs/v1-demo-runbook.md`、相关 spec 和 plan，再动代码。
2. 每个任务单独开 `codex/` 前缀分支，不直接把实验改动堆到 `main`。
3. 先跑相关测试或构建，锁定现状；改完后再跑一次验证。
4. 如果改动涉及 demo 口径，必须同步更新文档，至少包括 `docs/handoff.md` 或 `docs/v1-demo-runbook.md`。
5. 不要提交本地运行状态、工作日志和临时产物；`.omx/`、本地日志、临时 CSV 应保持未跟踪。

## 推荐接手顺序

1. 阅读 `docs/handoff.md`
2. 阅读 `docs/v1-demo-runbook.md`
3. 查看 `docs/superpowers/specs/` 和 `docs/superpowers/plans/` 中与当前任务最相关的文档
4. 运行本轮要触达子项目的测试或构建命令
5. 再开始编码

## 当前结论

当前仓库已经是可协作开发状态，不再依赖仓库外的旧前后端目录。新开发者应以本仓库内的 `projects/*` 为唯一开发入口，并以 `codex/academic-risk-warning` 作为当前最新业务实现基线。
