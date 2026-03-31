# V1 Demo 运行说明

Last Updated: 2026-03-31

## 0. Real-Data Build Path

当前推荐的真实数据构建路径是：

```powershell
uv run --project projects/analytics-db analytics-db build-demo-features
uv run --project projects/model-stubs student-behavior-stubs build artifacts/semester_features/v1_semester_features.csv --output-dir artifacts/model_stubs
```

说明：

- `analytics-db build-demo-features` 会直接读取仓库根目录下的真实 Excel 数据源
- 默认纳入的真实源是 `学生基本信息.xlsx`、`学生成绩.xlsx`、`考勤汇总.xlsx`、`本科生综合测评.xlsx`、`学生选课信息.xlsx`
- 该默认集合是为了在“真实数据覆盖”和“可接受构建时间”之间折中
- `model-stubs` 仍然只负责把这些真实特征转换成 Demo 可展示的规则版结果

当前仓库内已重建好的真实特征规模：

- `artifacts/semester_features/v1_semester_features.csv`
- `2905` 行
- 学期分布：`2023-2 / 2024-1 / 2024-2`

本文档只描述当前 V1 Demo 主链路如何运行、如何联调、哪些值是当前真实可用的，以及前端如何接入当前只读 API。

当前推荐的对外业务口径为：

- 4 类分析任务
- 10 个系统输出
- 群体分析采用“行为模式识别 / 群体分层”表达

历史实现中的“四象限”命名仍可能存在于少量兼容路径中，但当前主线结果和接口已经优先使用 `group_segment` 与 `/api/analytics/groups`。

## 1. 主链路顺序

当前 Demo 主链路按下面顺序理解和运行：

1. `semester-etl`
2. `analytics-db`
3. `model-stubs`
4. `demo-api`
5. `demo-web`（当前仍在独立分支）

每一层的作用如下：

- `semester-etl`：读取原始 Excel，生成学期宽表 `v1_semester_features.csv`
- `analytics-db`：把标准化事实和维度整理成分析底座，并生成 `student_term_features`
- `model-stubs`：基于 `student_term_features` 生成离线结果文件，供 Demo 展示和 API 读取
- `demo-api`：只读这些离线结果文件，对外提供总览、群体、预警、个体画像、个体报告和模型摘要接口
- `demo-web`：消费 `demo-api`，串联总览、群体分层、风险预警和学生个体主链路

## 2. 当前真实联调值

当前 Demo 联调不要再使用旧示例值，真实可用值是：

- `term`：`2023-2`、`2024-1`、`2024-2`
- 默认学期：`2024-2`
- 示例学生：`pjwrqxbj901`

旧示例当前不可用：

- `2023-1` 不可用，因为当前离线产物没有覆盖这个 term
- `20230001` 不可用，因为当前真实产物中的学生主键不是这个值

## 3. 仍然是 Stub 或规则版的字段

当前 V1 里，下面这些字段仍然属于 stub 或规则版，不要把它们当成正式模型输出：

- `risk_probability`
- `risk_level`
- `group_segment`
- `top_factors`
- `intervention_advice`
- `report_text`

另外，模型摘要中的这些字段也是 stub 口径：

- `cluster_method`
- `risk_model`
- `target_label`

如果现有接口或结果文件中仍出现 `quadrant_label`，应将其理解为历史兼容字段，而不是当前推荐的对外表达。

## 4. 最小验证命令

如果要检查主工作区各层是否可用，最小验证命令如下：

```powershell
uv run --project projects/semester-etl pytest projects/semester-etl/tests -q
uv run --project projects/analytics-db pytest projects/analytics-db/tests -q
uv run --project projects/model-stubs pytest projects/model-stubs/tests -q
uv run --project projects/demo-api pytest projects/demo-api/tests -q
```

如果要重新生成离线产物，可运行：

```powershell
uv run --project projects/analytics-db analytics-db build-demo-features
uv run --project projects/model-stubs student-behavior-stubs build artifacts/semester_features/v1_semester_features.csv --output-dir artifacts/model_stubs
```

## 5. API 启动命令

当前可用的 `demo-api` 启动方式如下：

```powershell
uv run --project projects/demo-api uvicorn student_behavior_demo_api.main:app --reload
```

如果不需要热重载，也可以去掉 `--reload`。

## 6. 前端启动方式

前端尚未合并到 `main`，当前开发分支为 `codex/v1-demo-web`。

在当前 Codex 工作区中，对应目录为：

- `.worktrees/v1-demo-web/projects/demo-web`

前端启动命令：

```powershell
cd .worktrees/v1-demo-web/projects/demo-web
npm install
npm run test
npm run build
npm run dev
```

前端默认使用：

- `VITE_API_BASE_URL=/api`

如果前端与后端不是通过同域代理联调，可以显式设置 `VITE_API_BASE_URL` 指向目标 API 前缀。

## 7. 联调前需要准备的产物

联调前至少要准备好下面 5 个结果文件：

- `artifacts/model_stubs/v1_student_results.csv`
- `artifacts/model_stubs/v1_student_reports.jsonl`
- `artifacts/model_stubs/v1_overview_by_term.json`
- `artifacts/model_stubs/v1_model_summary.json`
- `artifacts/model_stubs/v1_warnings.json`

这些文件是 `demo-api` 当前的唯一数据来源。

如果要重新生成它们，应使用主工作区中的 `projects/model-stubs`；如果只是做前后端联调，直接保留这些产物即可。

## 8. 当前 Demo 的实际使用方式

推荐的实际联调顺序是：

1. 先确保 `semester-etl` 产出学期宽表
2. 再确保 `analytics-db` 产出分析底座
3. 用 `model-stubs` 生成或保留 Demo 结果文件
4. 启动 `demo-api`
5. 前端只消费 `demo-api`，不要直接读原始 Excel、数据库或 `artifacts/`

## 9. 当前前端演示链路

`codex/v1-demo-web` 当前已经具备的主要联调链路：

1. 登录页调用 `POST /api/auth/demo-login`
2. 总览页展示 `overview` 和 `models/summary`
3. 总览页专业高风险摘要可直接下钻到预警页
4. 群体分层页通过 `/api/analytics/groups` 获取重点群体，并可带着 `term` 和 `group_segment` 下钻到预警页
5. 预警页支持 `term`、`risk_level`、`group_segment`、`major_name` 筛选，并将状态写回 URL
6. 学生页支持返回预警列表，并保留原有筛选上下文
7. 全局 `DemoStatusBar` 统一提示真实 API、默认学期和 stub 边界

## 10. 当前结论

当前 Demo 主链路已经能支撑真实联调，但前端仍处于独立分支阶段，仓库尚未完全收口。

最重要的边界是：

- `demo-api` 依赖的是离线结果文件
- 联调时必须使用当前真实 `term` 和真实学生主键
- 前端只消费 `demo-api`
- `risk_probability`、`group_segment`、`top_factors`、`intervention_advice`、`cluster_method`、`risk_model` 仍是 stub/规则版

若仍存在 `quadrant_label`，应视为待迁移的历史字段，不再作为新的对外业务表达。
