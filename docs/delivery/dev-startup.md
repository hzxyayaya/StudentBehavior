# Dev Startup

Last Updated: 2026-04-10

## 目标

这份文档用于给新开发者和协作者提供当前仓库的最小可复现启动方式，优先保证能够：

- 理解当前分支与仓库结构
- 跑通验证命令
- 重建学期特征与模型产物
- 启动后端 API 与前端页面

## 当前分支约定

- 主分支：`main`
- 当前最新业务基线曾在：`codex/academic-risk-warning`
- 新任务建议从最新业务基线切出新的 `codex/<task-name>` 分支开发

## 仓库结构

当前工作区内的核心子项目都在 `projects/` 下：

- `projects/semester-etl`
- `projects/analytics-db`
- `projects/model-stubs`
- `projects/demo-api`
- `projects/demo-web`

当前主工作树长期基线曾使用：

- `C:\Users\Orion\Desktop\program\StudentBehavior\.worktrees\academic-risk-warning`

## 启动前提

### 1. Python

推荐使用 `uv` 管理 Python 环境。

### 2. Node.js

前端需要可用的 Node.js 与 npm。

### 3. 原始数据

仓库根目录下需要存在原始 Excel 数据目录。当前逻辑会自动寻找包含 `.xlsx` 文件的数据目录，优先选择名称中含“数据集”的目录。

## 建议顺序

先验证，再启动。

## 一、重建学期特征

工作目录：

- `projects/analytics-db`

命令：

```powershell
cd C:\Users\Orion\Desktop\program\StudentBehavior\projects\analytics-db
uv run python -m student_behavior_analytics_db.cli build-demo-features
```

预期产物：

- `artifacts/semester_features/v1_semester_features.csv`

## 二、重建模型产物

工作目录：

- `projects/model-stubs`

命令：

```powershell
cd C:\Users\Orion\Desktop\program\StudentBehavior\projects\model-stubs
uv run python -m student_behavior_model_stubs.cli build ../../artifacts/semester_features/v1_semester_features.csv
```

预期产物：

- `artifacts/model_stubs/v1_student_results.csv`
- `artifacts/model_stubs/v1_student_reports.jsonl`
- `artifacts/model_stubs/v1_overview_by_term.json`
- `artifacts/model_stubs/v1_model_summary.json`
- `artifacts/model_stubs/v1_warnings.json`

## 三、启动后端

工作目录：

- `projects/demo-api`

命令：

```powershell
cd C:\Users\Orion\Desktop\program\StudentBehavior\projects\demo-api
uv run uvicorn student_behavior_demo_api.main:app --reload --port 8000
```

启动后可访问：

- OpenAPI: [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json)
- Scalar: [http://127.0.0.1:8000/scalar](http://127.0.0.1:8000/scalar)

## SQLite 维护库

当前仓库支持把现有 `semester_features` 与 `model_stubs` 产物同步进本地 SQLite。

命令：

```powershell
cd C:\Users\Orion\Desktop\program\StudentBehavior\projects\analytics-db
uv run analytics-db build-runtime-sqlite
```

生成位置：

- `data/demo.sqlite3`

说明：

- SQLite 文件为本地生成产物，不提交进仓库
- 当前 `demo-api` 已支持优先从 SQLite 读取 `model_summary`

## 四、启动前端

工作目录：

- `projects/demo-web`

首次安装依赖：

```powershell
cd C:\Users\Orion\Desktop\program\StudentBehavior\projects\demo-web
npm install
```

启动命令：

```powershell
npm run dev
```

启动后可访问：

- 前端页面: [http://127.0.0.1:5173](http://127.0.0.1:5173)

## 五、最小验证命令

### semester-etl

```powershell
uv run --project projects/semester-etl pytest projects/semester-etl/tests -q
```

### analytics-db

```powershell
uv run --project projects/analytics-db pytest projects/analytics-db/tests -q
```

### model-stubs

```powershell
uv run --project projects/model-stubs pytest projects/model-stubs/tests -q
```

### demo-api

```powershell
uv run --project projects/demo-api pytest projects/demo-api/tests -q
```

### demo-web

```powershell
cd projects/demo-web
npm run test
npm run build
```

## 六、当前页面入口

- `/risk`
- `/trajectory`
- `/profiles`
- `/development`
- `/students/:studentId`

## 七、开发规则

1. 优先阅读：
   - `docs/handoff.md`
   - `docs/v1-demo-runbook.md`
   - 当前任务相关 spec/plan
2. 新任务单独开 `codex/` 前缀分支
3. 改动前后都跑相关验证
4. 如果改动影响 Demo 口径，需同步更新文档
5. 不提交本地日志、临时产物和工作状态

## 八、当前结论

当前仓库已经是可协作开发状态。新的开发应以仓库内 `projects/*` 为唯一入口，不再依赖仓库外旧项目目录。
