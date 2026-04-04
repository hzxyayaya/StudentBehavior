# Dev Startup

Last Updated: 2026-04-04

## 目标

这份文档用于说明当前新版演示系统的最小可复现启动方式，包括：

- 重新生成学期特征
- 重新生成模型产物
- 启动后端 API
- 启动前端页面

当前默认工作树:

- `C:\Users\Orion\Desktop\program\StudentBehavior\.worktrees\academic-risk-warning`

## 启动前提

### 1. Python

推荐使用 `uv` 管理 Python 环境。

### 2. Node.js

前端需要可用的 Node.js 和 npm。

### 3. 原始数据

仓库根目录下需要存在原始 Excel 数据目录，当前逻辑会自动寻找包含 `.xlsx` 文件的数据目录，优先选择名称中含“数据集”的目录。

## 一、重建学期特征

工作目录:

- `projects/analytics-db`

命令:

```powershell
cd C:\Users\Orion\Desktop\program\StudentBehavior\.worktrees\academic-risk-warning\projects\analytics-db
uv run python -m student_behavior_analytics_db.cli build-demo-features
```

预期产物:

- `artifacts/semester_features/v1_semester_features.csv`

作用:

- 从 Excel 源表构建学生-学期粒度特征
- 为后续 8 维结果、风险结果和报告结果提供输入

## 二、重建模型产物

工作目录:

- `projects/model-stubs`

命令:

```powershell
cd C:\Users\Orion\Desktop\program\StudentBehavior\.worktrees\academic-risk-warning\projects\model-stubs
uv run python -m student_behavior_model_stubs.cli build ../../artifacts/semester_features/v1_semester_features.csv
```

预期产物:

- `artifacts/model_stubs/v1_student_results.csv`
- `artifacts/model_stubs/v1_student_reports.jsonl`
- `artifacts/model_stubs/v1_overview_by_term.json`
- `artifacts/model_stubs/v1_model_summary.json`
- `artifacts/model_stubs/v1_warnings.json`

作用:

- 生成 8 维结果
- 生成风险概率与风险等级
- 生成群体标签与风险因子
- 生成学生报告与总览数据

## 三、启动后端

工作目录:

- `projects/demo-api`

命令:

```powershell
cd C:\Users\Orion\Desktop\program\StudentBehavior\.worktrees\academic-risk-warning\projects\demo-api
uv run uvicorn student_behavior_demo_api.main:app --reload --port 8000
```

启动后可访问:

- OpenAPI: [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json)
- Scalar: [http://127.0.0.1:8000/scalar](http://127.0.0.1:8000/scalar)

## 四、启动前端

工作目录:

- `projects/demo-web`

首次安装依赖:

```powershell
cd C:\Users\Orion\Desktop\program\StudentBehavior\.worktrees\academic-risk-warning\projects\demo-web
npm install
```

启动命令:

```powershell
npm run dev
```

启动后可访问:

- 前端页面: [http://127.0.0.1:5173](http://127.0.0.1:5173)

## 五、最小验证命令

### model-stubs

```powershell
cd C:\Users\Orion\Desktop\program\StudentBehavior\.worktrees\academic-risk-warning\projects\model-stubs
uv run pytest
```

### demo-api

```powershell
cd C:\Users\Orion\Desktop\program\StudentBehavior\.worktrees\academic-risk-warning\projects\demo-api
uv run --all-groups --with pytest --with pandas pytest
```

### demo-web

```powershell
cd C:\Users\Orion\Desktop\program\StudentBehavior\.worktrees\academic-risk-warning\projects\demo-web
npm run test
npm run build
```

## 六、当前页面入口

- `/risk`
- `/trajectory`
- `/profiles`
- `/development`
- `/students/:studentId`

## 七、常见情况

### 1. 同步了代码但页面结果和别人不一致

常见原因:

- 你没有重新生成 `artifacts/model_stubs/*`
- 你当前使用的数据目录不同
- 你拉到的是代码最新状态，但不是别人本地尚未提交的产物状态

### 2. 页面显示“当前学期无有效数据”

这通常不是前端报错，而是当前学期对应维度在源表中没有可用覆盖，或者该维度的学期特征还没有接入完成。

### 3. 后端能起但接口报产物缺失

说明：

- `demo-api` 当前依赖 `artifacts/model_stubs/*`
- 需要先完成前两个步骤，生成产物

## 当前结论

当前项目的可复现链路是：

1. 原始 Excel
2. 学期特征
3. 模型产物
4. API
5. 前端页面

如果只拉代码不重建产物，可以同步代码进度；如果要同步最新展示结果，需要同时重建产物。
