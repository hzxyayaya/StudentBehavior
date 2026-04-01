# V1 Academic Risk Warning Design

## Status

Draft

## Goal

在现有 8 维学期级画像底座上，落地“学业风险动态感知与预警”这一条完整分析任务闭环，使系统能够围绕学业表现风险进行分层、筛查、解释和干预。

## Scope

本 spec 只覆盖四类分析任务中的第 1 类：

1. 学业风险动态感知与预警

本 spec 不覆盖：

- 学业轨迹演化与关键行为分析的完整独立模块
- 学生个体画像与群体分层分析的整体重组
- 发展方向与去向关联分析

这些内容将在后续子项目中推进。

## Business Semantics

### Risk Target

本阶段的主风险语义从“综合测评低等级风险”切换为“学业表现风险”。

学业表现风险由以下核心学业信号主导：

- 学期 GPA
- 挂科课程数
- 及格边缘课程数
- 挂科课程占比

综合测评结果、群体标签和其他行为特征可作为辅助参考，但不再作为本阶段的主监督语义。

### Risk Levels

系统固定输出四档学业风险：

- 高风险
- 较高风险
- 一般风险
- 低风险

### Risk Construction Strategy

风险结果采用“基础风险盘 + 行为修正项”的混合机制：

1. 先由学业结果生成基础风险盘
2. 再由 8 维中的非学业维度对风险进行上调或下调
3. 最后把修正后的风险映射为四档风险

## Architecture

本阶段沿用现有链路：

1. `analytics-db` 继续提供学生-学期级原始指标
2. `model-stubs` 负责学业风险计算、风险解释和干预建议生成
3. `demo-api` 负责对外输出风险结果与筛选接口
4. `demo-web` 负责在总览、群体、预警、个体页面展示结果

本阶段不新增新的训练服务或独立后台。

## Risk Model Design

### Base Risk Score

新增 `base_risk_score`，范围为 `0-100`，仅由学业表现信号生成。

建议主输入字段：

- `avg_gpa_metric`
- `failed_course_count`
- `borderline_course_count`
- `failed_course_ratio`

解释要求：

- `base_risk_score` 只回答“如果只看学业结果，这个学生的风险底盘有多高”
- 不在这一层混入作息、在线学习或运动等行为维度

### Risk Adjustment Score

新增 `risk_adjustment_score`，表示非学业维度对基础风险盘的修正量。

优先纳入修正的维度：

- 课堂学习投入
- 在线学习积极性
- 图书馆沉浸度
- 网络作息自律指数
- 早晚生活作息规律
- 体质及运动状况
- 综合荣誉与异动预警

规则要求：

- 明显负向行为维度可上调风险
- 明显正向行为维度可下调风险
- 中性维度不做或只做轻微修正
- `学业基础表现` 不再作为主修正维度，避免与基础风险盘重复计入

### Adjusted Risk Score

新增 `adjusted_risk_score`，范围为 `0-100`，表示修正后的最终学业风险分。

最终风险档位以 `adjusted_risk_score` 映射：

- `>= 80` -> 高风险
- `65-79` -> 较高风险
- `45-64` -> 一般风险
- `< 45` -> 低风险

### Dynamic Change

新增 `risk_delta` 与 `risk_change_direction`：

- `risk_delta`：当前学期相对上一学期的风险分变化值
- `risk_change_direction`：`rising` / `steady` / `falling`

动态感知至少体现：

- 当前学期与上一学期的风险变化
- 主要触发变化的维度或学业信号

## Explanation Design

风险解释固定拆成三层：

1. 基础风险原因
2. 行为放大因素
3. 保护性因素

新增或强化以下结果字段：

- `base_risk_explanation`
- `behavior_adjustment_explanation`
- `top_risk_factors`
- `top_protective_factors`
- `risk_change_explanation`

解释要求：

- 必须可追溯到已存在的学期级指标和 8 维结果
- 不允许只输出抽象标签，不给证据
- 每个风险结论都应能够说明“为什么”

## Intervention Design

新增或强化面向预警场景的干预输出：

- `intervention_priority`
- `intervention_plan`
- `priority_interventions`

干预建议应按风险档位和触发维度分层输出：

- 高风险：优先级最高，建议更具体
- 较高风险：聚焦重点薄弱维度
- 一般风险：轻量提醒与过程跟踪
- 低风险：维持性建议

## API Changes

### `GET /api/analytics/overview`

新增或强化：

- `risk_band_distribution`
- `risk_trend_summary`
- `risk_factor_summary`
- `priority_interventions`

### `GET /api/analytics/groups`

每个群体新增或强化：

- `avg_risk_score`
- `avg_risk_level`
- `risk_change_summary`
- `risk_amplifiers`
- `protective_factors`

### `GET /api/warnings`

每个学生项新增或强化：

- `base_risk_score`
- `risk_adjustment_score`
- `adjusted_risk_score`
- `risk_level`
- `risk_delta`
- `risk_change_direction`
- `top_risk_factors`
- `top_protective_factors`

并支持以下筛选项：

- `risk_level`
- `major_name`
- `group_segment`
- `risk_change_direction`

### `GET /api/students/{id}/profile`

新增或强化：

- 当前风险分
- 当前风险档位
- 风险变化趋势
- 基础风险盘摘要

### `GET /api/students/{id}/report`

新增或强化：

- `base_risk_explanation`
- `behavior_adjustment_explanation`
- `risk_change_explanation`
- `intervention_plan`

## Frontend Changes

### Overview Page

新增或强化区块：

- 学业风险四档分布
- 风险变化趋势
- 高风险专业/学院摘要
- 风险触发因素 Top 列表
- 干预优先级摘要

### Groups Page

新增或强化：

- 群体平均风险分与风险档位
- 群体主要风险放大因素
- 群体保护性因素
- 群体风险变化方向

### Warnings Page

升级为本子项目主页面，支持：

- 四档风险筛选
- 学期筛选
- 专业/学院筛选
- 群体标签筛选
- 风险变化方向筛选
- 风险学生列表排序与下钻

### Student Page

新增或强化：

- 当前风险档位与风险分
- 基础风险盘解释
- 行为修正项解释
- 风险变化趋势
- 分层干预建议

## Files Expected To Change

### `projects/model-stubs`

- `src/student_behavior_model_stubs/scoring.py`
- `src/student_behavior_model_stubs/build_outputs.py`
- `src/student_behavior_model_stubs/templates.py`
- 可新增：`src/student_behavior_model_stubs/risk_calibration.py`

### `projects/demo-api`

- `src/student_behavior_demo_api/services.py`
- `src/student_behavior_demo_api/main.py`
- `tests/...`

### `projects/demo-web`

- `src/features/overview/OverviewPage.vue`
- `src/features/quadrants/QuadrantsPage.vue`
- `src/features/warnings/WarningsPage.vue`
- `src/features/students/StudentPage.vue`
- `src/lib/api.ts`
- `src/lib/types.ts`

## Acceptance Criteria

本子项目完成后，必须满足：

- 风险主语义切换为学业表现风险
- 风险结果为四档分层
- 风险来源于“基础风险盘 + 行为修正项”
- `/warnings` 页面可按四档风险筛查
- 学生页能解释“为什么被预警”
- 总览页能展示整体风险状态与重点群体

## Non-Goals

本阶段不做：

- 新的模型训练管理页面
- 实时 SHAP 在线计算
- 发展方向与去向关联分析联动
- 新角色权限系统

