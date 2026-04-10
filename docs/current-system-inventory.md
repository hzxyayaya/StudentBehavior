# Current System Inventory

Last Updated: 2026-04-04

## 当前工作树

- `C:\Users\Orion\Desktop\program\StudentBehavior\.worktrees\academic-risk-warning`

## 当前主项目

### 1. `projects/analytics-db`

职责:

- 从 Excel 源表构建学生-学期粒度特征
- 做学号、学期和字段标准化
- 产出 `v1_semester_features.csv`

关键入口:

- `src/student_behavior_analytics_db/build_demo_features_from_excels.py`
- `src/student_behavior_analytics_db/build_student_term_features.py`

### 2. `projects/model-stubs`

职责:

- 基于学期特征构建 8 维分数
- 计算学业风险概率、风险等级和变化方向
- 生成学生结果、报告、总览和预警产物

关键入口:

- `src/student_behavior_model_stubs/build_outputs.py`
- `src/student_behavior_model_stubs/scoring.py`
- `src/student_behavior_model_stubs/templates.py`

### 3. `projects/demo-api`

职责:

- 读取 `artifacts/model_stubs` 产物
- 聚合成总览、群体、轨迹、发展、学生画像、学生报告、预警等接口
- 提供 OpenAPI 和 Scalar 文档

关键入口:

- `src/student_behavior_demo_api/main.py`
- `src/student_behavior_demo_api/services.py`
- `src/student_behavior_demo_api/loaders.py`

### 4. `projects/demo-web`

职责:

- 按四类分析任务组织前端页面
- 调用 `demo-api` 展示风险、轨迹、画像、发展分析和学生详情

关键入口:

- `src/app/router.ts`
- `src/lib/api.ts`
- `src/components/layout/AppShell.vue`

## 当前前端任务页

- `/risk`
- `/trajectory`
- `/profiles`
- `/development`
- `/students/:studentId`

## 当前后端接口

- `POST /api/auth/demo-login`
- `GET /api/analytics/overview`
- `GET /api/analytics/groups`
- `GET /api/analytics/trajectory`
- `GET /api/analytics/development`
- `GET /api/models/summary`
- `GET /api/students/{student_id}/profile`
- `GET /api/students/{student_id}/report`
- `GET /api/warnings`
- `GET /scalar`
- `GET /openapi.json`

## 当前核心产物

### 学期特征产物

- `artifacts/semester_features/v1_semester_features.csv`

### 规则结果产物

- `artifacts/model_stubs/v1_student_results.csv`
- `artifacts/model_stubs/v1_student_reports.jsonl`
- `artifacts/model_stubs/v1_overview_by_term.json`
- `artifacts/model_stubs/v1_model_summary.json`
- `artifacts/model_stubs/v1_warnings.json`

## 当前稳定主链路

1. Excel 源表进入 `analytics-db`
2. 构建学生-学期特征表
3. 特征表进入 `model-stubs`
4. 生成风险、画像、报告和总览产物
5. `demo-api` 读取产物并包装接口
6. `demo-web` 消费接口并展示四类任务

## 当前系统基线文档

详见:

- `docs/architecture-baseline.md`
