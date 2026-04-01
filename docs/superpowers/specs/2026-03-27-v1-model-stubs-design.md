# V1 Model Stubs 结果层设计

Status: Draft for implementation planning

Last Updated: 2026-03-27

## 1. 文档目的

本文档用于冻结 `V1-IMPL-002` 的离线结果层设计，作为后续 `projects/model-stubs` 实现、`demo-api` 读取以及前端联调的共同基线。

这一步的目标不是训练正式模型，而是：

- 复用已经完成的 `semester-etl` 与 `analytics-db`
- 从 `student_term_features` 稳定生成可展示的分析结果
- 让 P0/P1 主链路先形成“特征 -> 结果 -> 接口 -> 页面”的完整闭环
- 为后续真实 `KMeans / LightGBM / SHAP / LLM` 替换预留边界

## 2. 设计结论

V1 应新增独立子项目 `projects/model-stubs`，职责仅限于：

- 读取离线宽表和必要聚合输入
- 生成风险、分层、解释、建议和总览结果产物
- 明确保留 `stub` 身份
- 不训练正式模型
- 不启动 HTTP 服务
- 不直接承担页面逻辑

因此，`model-stubs` 是结果层，不是数据清洗层，也不是后端服务层。

## 3. 上下游边界

### 3.1 上游输入

`model-stubs` 首版只依赖以下冻结输入：

1. `student_term_features`
2. `students`
3. `terms`

其中核心输入是 `student_term_features`。  
它已经由 `projects/analytics-db` 定义为首版分析 mart 核心宽表，主键为 `student_id + term_key`。

### 3.2 下游输出

`model-stubs` 的输出不直接面向数据库回写，而是面向：

- `demo-api` 读取
- 前端主链路页面联调
- 答辩展示结果说明

因此输出格式优先选择文件制品，而不是在线服务或数据库表。

### 3.3 分层职责

- `projects/semester-etl`：原始 Excel -> 首批学期级特征 CSV
- `projects/analytics-db`：标准化事实/维度 -> `student_term_features`
- `projects/model-stubs`：`student_term_features` -> 风险/分层/解释/建议/总览结果
- `projects/demo-api`：读取 `model-stubs` 产物并按冻结 contract 返回接口

## 4. 为什么当前阶段先做 Stub

当前项目的主阻塞已不在数据接入底座，而在“最终结果层”缺失。

如果直接进入正式模型实现，会同时引入以下不稳定因素：

- 真实聚类方案尚未冻结
- 正式风险模型尚未完成训练与评估闭环
- 解释方法与干预建议尚无稳定 pipeline
- 前后端接口还缺少可持续读取的结果制品

因此 V1 先做 `model-stubs` 的原因是：

- 快速打通 P0 学业风险动态感知与预警闭环
- 顺带支撑 P1 的趋势分析和群体分层展示
- 让接口和页面先围绕稳定字段开发
- 后续只替换内部生成逻辑，不推翻接口和页面

## 5. 项目结构

建议新建：

- `projects/model-stubs/pyproject.toml`
- `projects/model-stubs/src/student_behavior_model_stubs/config.py`
- `projects/model-stubs/src/student_behavior_model_stubs/io.py`
- `projects/model-stubs/src/student_behavior_model_stubs/build_outputs.py`
- `projects/model-stubs/src/student_behavior_model_stubs/templates.py`
- `projects/model-stubs/src/student_behavior_model_stubs/cli.py`
- `projects/model-stubs/tests/...`

默认输出目录建议固定为：

- `artifacts/model_stubs`

## 6. 输入产物约定

首版输入以 `analytics-db` 产出的 DataFrame 或导出文件为准。

为了避免和上一阶段脱节，`model-stubs` 不再直接读取原始 Excel，也不直接依赖 `semester-etl` 的早期 CSV。

首版冻结的最小输入字段如下：

- `student_id`
- `term_key`
- `major_name`
- `college_name`
- `avg_course_score`
- `failed_course_count`
- `avg_gpa`
- `major_rank_pct`
- `risk_label`
- `attendance_record_count`
- `attendance_normal_rate`
- `selected_course_count`
- `sign_event_count`
- `assignment_submit_count`
- `exam_submit_count`
- `task_participation_rate`
- `discussion_reply_count`
- `library_visit_count`
- `library_active_days`
- `running_punch_count`
- `morning_activity_rate`

其中：

- `risk_label` 是监督标签，不是预测结果
- `major_rank_pct` 当前允许为空
- Task 7 Draft source 相关字段允许为空，不补假值

## 7. 输出产物设计

首版固定输出 4 份核心结果文件。

### 7.1 学生学期结果表

路径：

- `artifacts/model_stubs/v1_student_results.csv`

最小字段：

- `student_id`
- `term_key`
- `student_name`
- `major_name`
- `quadrant_label`
- `risk_probability`
- `risk_level`
- `dimension_scores_json`

用途：

- 支撑 `/api/warnings`
- 支撑 `/api/students/{student_id}/profile`
- 作为总览聚合的底表

### 7.2 学生报告结果表

路径：

- `artifacts/model_stubs/v1_student_reports.jsonl`

每行一个 `student_id + term_key` 结果对象。

最小字段：

- `student_id`
- `term_key`
- `top_factors`
- `intervention_advice`
- `report_text`

用途：

- 支撑 `/api/students/{student_id}/report`

### 7.3 学期总览聚合结果

路径：

- `artifacts/model_stubs/v1_overview_by_term.json`

每个 `term_key` 至少包含：

- `student_count`
- `risk_distribution`
- `quadrant_distribution`
- `major_risk_summary`
- `trend_summary`

用途：

- 支撑 `/api/analytics/overview`
- 支撑 `/api/analytics/quadrants` 的聚合输入

### 7.4 模型摘要结果

路径：

- `artifacts/model_stubs/v1_model_summary.json`

最小字段：

- `cluster_method`
- `risk_model`
- `target_label`
- `auc`
- `updated_at`

用途：

- 支撑 `/api/models/summary`

## 8. 与 API Contract 的映射要求

输出字段必须优先贴合冻结的 `v1-api-contract.md`，避免后续 `demo-api` 再做一层重命名翻译。

冻结要求如下：

- `risk_level` 枚举固定为 `high`、`medium`、`low`
- `quadrant_label` 枚举固定为 `自律共鸣型`、`被动守纪型`、`脱节离散型`、`情绪驱动型`
- `top_factors` 数组结构与 `/api/students/{student_id}/report` 一致
- `intervention_advice` 为字符串数组
- `dimension_scores_json` 可先用 JSON 字符串承载，后续由 `demo-api` 解包为 `dimension_scores`

## 9. Stub 生成规则

首版生成逻辑必须满足两个条件：

1. 同一输入反复运行得到同一输出
2. 输出看起来像真实分析结果，但不能伪装成正式模型

### 9.1 风险概率 `risk_probability`

首版按“确定性规则 + 稳定扰动”生成。

建议构成：

- 基础风险：来自 `risk_label`、`failed_course_count`、`avg_course_score`、`attendance_normal_rate`
- 稳定扰动：来自 `student_id + term_key` 的哈希扰动

冻结要求：

- 输出范围限制在 `0.05 ~ 0.95`
- 输出保留两位小数
- 若 `risk_label = 1`，风险概率整体应偏高
- 不得声称这是正式模型推理概率

### 9.2 风险等级 `risk_level`

由 `risk_probability` 直接映射：

- `>= 0.75` -> `high`
- `>= 0.45 and < 0.75` -> `medium`
- `< 0.45` -> `low`

### 9.3 四象限 `quadrant_label`

首版四象限是规则型 stub，不宣称为正式聚类结果。

建议使用两条 stub 轴：

- 参与轴：由 `attendance_normal_rate`、`sign_event_count`、`selected_course_count` 综合得到
- 稳定轴：由 `avg_course_score`、`failed_course_count`、`library_visit_count` 与稳定扰动综合得到

映射固定为：

- 高参与 + 高稳定 -> `自律共鸣型`
- 低参与 + 高稳定 -> `被动守纪型`
- 低参与 + 低稳定 -> `脱节离散型`
- 高参与 + 低稳定 -> `情绪驱动型`

### 9.4 维度评分 `dimension_scores_json`

首版不直接承诺完整 8 维雷达图，而是先输出最小可扩展版本。

建议先固定 4 个维度：

- `学业基础表现`
- `课堂学习投入`
- `学习行为活跃度`
- `生活规律与资源使用`

每个维度分数：

- 取值范围 `0 ~ 1`
- 保留两位小数
- 由宽表指标和稳定规则映射得到

### 9.5 学生姓名 `student_name`

如果当前结果层拿不到真实姓名，首版允许占位。

冻结规则：

- 优先使用上游 `students` 的姓名字段
- 若上游未提供，允许 `student_name = student_id`
- 必须在实现和文档中标明其为 `stub placeholder`

### 9.6 个体解释与建议

`top_factors`、`intervention_advice`、`report_text` 首版采用模板驱动生成。

输入依据：

- `risk_level`
- `quadrant_label`
- 4 个维度评分

冻结规则：

- `top_factors` 固定 2 到 3 条
- `intervention_advice` 固定 2 条
- `report_text` 为 1 段摘要
- 字段结构必须贴 API contract
- 文案允许是 stub，但必须可读、稳定、可答辩解释

### 9.7 模型摘要

`v1_model_summary.json` 首版必须显式保留 stub 身份。

建议值：

- `cluster_method = "stub-quadrant-rules"`
- `risk_model = "stub-risk-rules"`
- `target_label = "综合测评低等级风险"`
- `auc` 为固定演示占位值
- `updated_at` 运行时生成

其中 `updated_at` 不允许保留占位符字符串，必须在每次构建时写入真实时间戳。

## 10. 容错和告警规则

首版应尽量产出，同时保留明确告警。

冻结规则：

- 缺少关键输入列时，构建失败
- 单行异常值尽量跳过，不阻断整次产出
- 某些特征字段为 `null` 时，允许回退到较弱规则，但必须保持输出可解释
- 若某个学生学期行缺少足够输入，仍可产出结果，但应在 warnings 中可追踪

建议同时输出：

- `artifacts/model_stubs/v1_warnings.json`

最小字段：

- `generated_at`
- `input_row_count`
- `output_row_count`
- `dropped_row_count`
- `null_metric_summary`
- `notes`

## 11. 首版不做的内容

以下内容明确不属于 `V1-IMPL-002`：

- 正式聚类训练与评估
- 正式风险模型训练与调参
- SHAP 或同等级真实解释框架
- LLM 实时生成个性化报告
- 在线推理服务
- 结果回写数据库

这些内容后续可以替换当前 stub 逻辑，但不影响结果文件结构。

## 12. 验收标准

首版完成时，至少满足：

1. `projects/model-stubs` 可通过 `uv` 安装和运行
2. 可从当前 `student_term_features` 输入稳定生成 4 份核心结果文件
3. 输出字段命名与 `v1-api-contract.md` 对齐
4. 同一输入多次运行，结果稳定一致
5. `updated_at` 与 warnings 中的 `generated_at` 为真实运行时间
6. `risk_probability`、`risk_level`、`quadrant_label` 分布可解释且非全常量
7. 测试覆盖结果生成、模板输出、聚合结果与容错逻辑

## 13. 下一步

本 spec 冻结后，下一步应进入 implementation plan，拆解为：

1. 项目骨架与 CLI
2. 输入读取与规范化
3. 风险/分层 stub 规则实现
4. 报告与建议模板实现
5. 总览与模型摘要产物实现
6. warnings 与测试收尾

