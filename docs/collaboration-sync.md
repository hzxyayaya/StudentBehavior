# Collaboration Sync Guide

Last Updated: 2026-04-04

## 目标

这份文档用于发给协作同学，帮助他们快速同步当前项目进度，并理解“代码进度”和“本地产物进度”的区别。

## 一、先同步代码

```powershell
git fetch origin
git checkout codex/academic-risk-warning
git pull
```

当前主要开发分支:

- `codex/academic-risk-warning`

## 二、拉下来之后能拿到什么

### 可以同步到的内容

- 最新前端代码
- 最新后端代码
- 最新四类任务页面结构
- 最新 Scalar 接口文档
- 最新项目架构文档

### 默认同步不到的内容

如果没有提交 `artifacts`，则默认同步不到本地重新生成的结果产物，例如：

- `artifacts/model_stubs/v1_student_results.csv`
- `artifacts/model_stubs/v1_student_reports.jsonl`
- `artifacts/model_stubs/v1_overview_by_term.json`
- `artifacts/model_stubs/v1_model_summary.json`
- `artifacts/model_stubs/v1_warnings.json`

## 三、如果想看到接近最新的实际效果

需要在本地自己重建产物。

### 步骤 1：生成学期特征

```powershell
cd C:\Users\Orion\Desktop\program\StudentBehavior\.worktrees\academic-risk-warning\projects\analytics-db
uv run python -m student_behavior_analytics_db.cli build-demo-features
```

### 步骤 2：生成模型产物

```powershell
cd C:\Users\Orion\Desktop\program\StudentBehavior\.worktrees\academic-risk-warning\projects\model-stubs
uv run python -m student_behavior_model_stubs.cli build ../../artifacts/semester_features/v1_semester_features.csv
```

### 步骤 3：启动后端

```powershell
cd C:\Users\Orion\Desktop\program\StudentBehavior\.worktrees\academic-risk-warning\projects\demo-api
uv run uvicorn student_behavior_demo_api.main:app --reload --port 8000
```

### 步骤 4：启动前端

```powershell
cd C:\Users\Orion\Desktop\program\StudentBehavior\.worktrees\academic-risk-warning\projects\demo-web
npm install
npm run dev
```

## 四、访问地址

- 前端: [http://127.0.0.1:5173](http://127.0.0.1:5173)
- Scalar: [http://127.0.0.1:8000/scalar](http://127.0.0.1:8000/scalar)
- OpenAPI: [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json)

## 五、推荐先看的文档

- [architecture-baseline.md](/C:/Users/Orion/Desktop/program/StudentBehavior/.worktrees/academic-risk-warning/docs/architecture-baseline.md)
- [current-system-inventory.md](/C:/Users/Orion/Desktop/program/StudentBehavior/.worktrees/academic-risk-warning/docs/current-system-inventory.md)
- [dev-startup.md](/C:/Users/Orion/Desktop/program/StudentBehavior/.worktrees/academic-risk-warning/docs/dev-startup.md)

## 六、协作时需要注意

### 1. 不要默认把 artifacts 当成代码基线

当前项目区分两类状态：

- 代码状态
- 本地生成产物状态

很多页面内容依赖产物文件，所以“代码一致”不一定等于“展示效果完全一致”。

### 2. 如果要复现同样页面结果，优先统一数据目录

因为当前产物链路依赖本地 Excel 数据目录，数据目录不一致会导致最终结果存在差异。

### 3. 如果要继续开发，优先改三层

优先级通常是：

1. `projects/analytics-db`
2. `projects/model-stubs`
3. `projects/demo-api`

前端通常是最后一层消费方。

## 七、一句话说明当前项目

当前项目是：

- Excel 源表
- 学期特征构建
- 规则产物生成
- API 包装
- 四类任务前端展示

这是一条完整的离线产物驱动演示链路，不是实时数据库查询系统。
