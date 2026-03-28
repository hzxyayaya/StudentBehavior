# V1 Demo 运行说明

本文档只描述当前 V1 Demo 主链路如何运行、如何联调、哪些值是当前真实可用的，方便后续前端和联调直接按步骤执行。

## 1. 主链路顺序

当前 Demo 主链路按下面顺序理解和运行：

1. `semester-etl`
2. `analytics-db`
3. `model-stubs`
4. `demo-api`

每一层的作用如下：

- `semester-etl`：读取原始 Excel，生成学期宽表 `v1_semester_features.csv`
- `analytics-db`：把标准化事实和维度整理成分析底座，并生成 `student_term_features`
- `model-stubs`：基于 `student_term_features` 生成离线结果文件，供 Demo 展示和 API 读取
- `demo-api`：只读这些离线结果文件，对外提供总览、群体、预警、个体画像、个体报告和模型摘要接口

## 2. 当前真实联调值

当前 Demo 联调不要再使用旧示例值，真实可用值是：

- `term`：`2023-2`、`2024-1`、`2024-2`
- 示例学生：`pjwrqxbj901`

旧示例当前不可用：

- `2023-1` 不可用，是因为当前真实离线产物里没有覆盖这个 term，API 会按“不存在该 term”处理
- `20230001` 不可用，是因为当前真实离线产物里的学生主键不是这个值，API 会按“不存在该学生”处理

## 3. 仍然是 Stub 或规则版的字段

当前 V1 里，下面这些字段仍然属于 stub 或规则版，不要把它们当成正式模型输出：

- `risk_probability`
- `risk_level`
- `quadrant_label`
- `top_factors`
- `intervention_advice`
- `report_text`

另外，模型摘要中的这些字段也是 stub 口径：

- `cluster_method`
- `risk_model`
- `target_label`

`updated_at` 和 `generated_at` 这类时间字段是运行时生成值，不要手写成占位符。

## 4. 最小测试命令

如果要检查各层是否可用，最小测试命令如下：

```powershell
uv run --project projects/semester-etl semester-features build
uv run --project projects/analytics-db analytics-db bootstrap
uv run --project .worktrees/v1-model-stubs/projects/model-stubs student-behavior-stubs build
uv run --project projects/semester-etl pytest projects/semester-etl/tests -q
uv run --project projects/analytics-db pytest projects/analytics-db/tests -q
uv run --project .worktrees/v1-model-stubs/projects/model-stubs pytest .worktrees/v1-model-stubs/projects/model-stubs/tests -q
uv run --project .worktrees/v1-demo-api/projects/demo-api pytest .worktrees/v1-demo-api/projects/demo-api/tests -q
```

说明：

- `semester-etl` 和 `analytics-db` 的主线代码在仓库主工作区
- `model-stubs` 和 `demo-api` 的可运行实现当前保留在各自 worktree 中
- 主工作区里的 `projects/model-stubs` 目前仍不是完整可执行状态，不能把它当成最终运行入口
- `analytics-db bootstrap` 目前只负责初始化/校验主线入口，不要把它理解成完整数据仓库重建命令

## 5. API 启动命令

当前可用的 `demo-api` 启动方式如下：

```powershell
uv run --project .worktrees/v1-demo-api/projects/demo-api uvicorn student_behavior_demo_api.main:app --reload
```

如果不需要热重载，也可以直接去掉 `--reload`。

## 6. 联调前需要准备的产物

联调前至少要准备好下面 5 个结果文件：

- `artifacts/model_stubs/v1_student_results.csv`
- `artifacts/model_stubs/v1_student_reports.jsonl`
- `artifacts/model_stubs/v1_overview_by_term.json`
- `artifacts/model_stubs/v1_model_summary.json`
- `artifacts/model_stubs/v1_warnings.json`

这些文件是 `demo-api` 当前的唯一数据来源。

如果要重新生成它们，应使用当前可运行的 `model-stubs` 实现所在 worktree；如果只是做前后端联调，直接保留这些产物即可。

## 7. 当前 Demo 的实际使用方式

推荐的实际联调顺序是：

1. 先确保 `semester-etl` 产出学期宽表
2. 再确保 `analytics-db` 产出分析底座
3. 用 `model-stubs` 生成或保留 Demo 结果文件
4. 启动 `demo-api`
5. 前端只消费 `demo-api`，不要直接读原始 Excel

## 8. 当前结论

当前 Demo 主链路已经能支撑真实联调，但它不是“所有层都在主工作区完整收口”的状态。

最重要的边界是：

- `demo-api` 依赖的是离线结果文件
- `risk_probability`、`quadrant_label`、`top_factors`、`intervention_advice` 仍是 stub/规则版
- 联调时必须使用当前真实 term 和真实学生主键
- 旧示例值不要继续沿用
