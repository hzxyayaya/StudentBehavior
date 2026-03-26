# V1 分析中台数据库设计

Status: Draft for implementation planning

Last Updated: 2026-03-26

## 1. 文档目的

本文档用于冻结当前项目的 V1 分析中台数据库设计方向，作为后续数据接入、标准化处理、特征宽表构建、模型输出和后端接口读取的共同设计基线。

本文档回答的不是“如何把所有 Excel 逐张导入数据库”，而是：

- 当前项目应围绕哪些核心分析维度设计数据库
- 哪些源表应该进入首版核心链路
- 哪些表应先保持 Draft 或排除
- 首版应保留哪些维度表、事实表和分析 mart 表
- `student_term_features` 应该如何作为 V1 核心分析宽表存在

## 2. 设计结论

V1 数据库应设计为 PostgreSQL 风格的分析中台型底座，而不是只服务当前 Demo 的临时轻量库。

但首版落地不应一次建完全量中台，而应遵循：

- 逻辑模型按长期中台思路设计
- 首版物理模型仅实现最小可用子集
- 先围绕 4 个核心识别维度建立稳定链路
- 不要求一次使用全部 27 张源表

## 3. 总体设计原则

### 3.1 分层设计

数据库和数据链路采用三层结构：

1. 原始层
   - 原始 Excel 文件继续保留在文件系统中
   - 首版不要求把所有源表逐张 raw 入 PostgreSQL
   - 原始文件作为事实证据源保留

2. 标准化层
   - 统一学生主键
   - 统一学期主键
   - 统一字段命名和时间格式
   - 将原始表按业务粒度重组为标准化维度表和事实表

3. 分析层
   - 以 `student_term_features` 为首版核心宽表
   - 为画像、分层、风险、趋势、解释等分析结果提供统一输入

### 3.2 主键与时间统一

全库统一采用以下两个核心键：

- `student_id`
- `term_key`

统一规则如下：

- 所有学生标识字段统一归一到 `student_id`
- 所有分析时间统一归一到 `term_key`
- 首版分析粒度以“学期”为主

### 3.3 归一规则边界

标准化层允许“确定性归一”，不允许“猜测性推断”。

允许：

- `XH`、`XSBH`、`LOGIN_NAME`、`USERNUM`、`SID`、`cardld`、`IDSERTAL`、`KS_XH`、`XHHGH` 等字段归一为 `student_id`
- `XN + XQ`、`KKXN + KKXQ`、`2020-2021学年第1学期` 等稳定格式归一为 `term_key`
- 日期、时间戳归一为标准时间字段

不允许：

- 根据模糊日期或月份主观猜测学期
- 未验证的学号候选字段直接强行作为统一主键
- 无稳定学期规则的源表直接并入分析宽表

### 3.4 命名原则

保留“维度表 + 事实表 + mart 表”的建模思想，但不强制使用 `dim_`、`fact_` 前缀。

优先使用业务可读命名：

- `students`
- `terms`
- `courses`
- `majors`
- `student_grade_records`
- `student_attendance_records`
- `student_term_features`

## 4. 核心分析维度

首版数据库围绕以下 4 个核心识别维度设计，不继续扩维：

1. 学业表现
2. 课堂投入
3. 学习行为活跃度
4. 生活规律与资源使用

这 4 个维度已足够支撑当前 V1 的以下目标：

- 学生个体画像
- 学生群体画像
- 4 类行为模式识别
- 综合测评低等级风险预测
- 趋势分析
- 群体对比分析

## 5. 源表归并策略

首版数据库不按 Excel 文件名逐表设计，而是按业务主题域和事实粒度设计。

### 5.1 学生主数据域

主要来源：

- `学生基本信息.xlsx`

用途：

- 生成学生主数据
- 提供学院、专业、班级、性别、民族、政治面貌等基础画像字段

### 5.2 教学与课程域

主要来源：

- `学生选课信息.xlsx`
- `课程信息.xlsx`

用途：

- 构建学生选课事实
- 构建课程维度
- 支撑课程负载、课堂投入和学习活动的关联

说明：

- `上课信息统计表.xlsx` 暂不进入首版核心链路，因为当前缺少稳定学生级主键

### 5.3 学业表现域

主要来源：

- `学生成绩.xlsx`
- `本科生综合测评.xlsx`

用途：

- 产出课程成绩、绩点、失败课程数、专业排名百分位
- 产出综合测评风险标签

### 5.4 课堂投入域

主要来源：

- `考勤汇总.xlsx`
- `学生签到记录.xlsx`
- `学生选课信息.xlsx`

用途：

- 产出到课次数、到课质量、签到活跃度、选课负载

### 5.5 学习行为活跃域

主要来源：

- `学生作业提交记录.xlsx`
- `考试提交记录.xlsx`
- `课堂任务参与.xlsx`
- `讨论记录.xlsx`

用途：

- 产出作业、考试、课堂任务、讨论互动等学习行为指标

### 5.6 生活规律与资源使用域

主要来源：

- `图书馆打卡记录.xlsx`
- `跑步打卡.xlsx`

用途：

- 产出图书馆到访、活跃天数、跑步打卡和晨间活动等规律性指标

## 6. 首版排除和 Draft 边界

以下源表暂不进入首版核心识别链路：

- `上网统计.xlsx`
- `门禁数据.xlsx`
- `毕业去向.xlsx`
- `奖学金获奖.xlsx`
- `学籍异动.xlsx`

排除原因：

- 当前无法稳定归一到 `student_id + term_key`
- 当前更适合作为增强结果域，而不是 4 个核心识别维度的主输入
- 接入这些表会显著增加首版数据库复杂度

这些表不代表无价值，而是当前应保持 Draft，等待后续单独验证接入规则。

## 7. 首版逻辑模型

### 7.1 维度表

首版建议保留以下维度表：

#### `students`

建议最小字段：

- `student_id`
- `gender`
- `ethnicity`
- `political_status`
- `major_name`
- `college_name`
- `class_name`
- `enrollment_year`

#### `terms`

建议最小字段：

- `term_key`
- `school_year`
- `term_no`
- `term_name`
- `start_date`
- `end_date`
- `is_analysis_term`

首版最关键的是：

- `term_key`
- `school_year`
- `term_no`
- `term_name`

#### `courses`

建议最小字段：

- `course_id`
- `course_code`
- `course_name`
- `course_type`
- `credit`
- `hours`
- `assessment_type`

#### `majors`

建议最小字段：

- `major_id`
- `major_name`
- `college_name`

### 7.2 事实表

首版建议保留以下标准化事实表：

- `student_course_enrollments`
- `student_grade_records`
- `student_attendance_records`
- `student_signin_events`
- `student_assignment_submissions`
- `student_exam_submissions`
- `student_task_participation`
- `student_discussion_events`
- `student_library_visits`
- `student_running_events`
- `student_evaluation_labels`

事实表设计原则：

- 每张事实表按业务粒度建模，而不是按 Excel 文件名照搬
- 每张事实表保留统一键：`student_id`、`term_key`
- 每张事实表保留追溯字段：`source_file`、`source_row_hash`
- 事件级事实表使用业务主键或代理主键，不强行以 `student_id + term_key` 作为唯一键

### 7.3 分析 mart 表

首版只保留一张核心分析宽表：

- `student_term_features`

主键：

- `student_id`
- `term_key`

职责：

- 汇总 4 个核心识别维度的学期级指标
- 作为聚类、风险预测、画像、群体分析和趋势分析的统一输入表

## 8. `student_term_features` 首版字段建议

首版字段数控制在 16 到 20 个核心字段左右。

建议结构如下：

### 8.1 主键与基础信息

- `student_id`
- `term_key`
- `major_name`
- `college_name`

### 8.2 学业表现

- `avg_course_score`
- `failed_course_count`
- `avg_gpa`
- `major_rank_pct`
- `risk_label`

### 8.3 课堂投入

- `attendance_record_count`
- `attendance_normal_rate`
- `selected_course_count`
- `sign_event_count`

### 8.4 学习行为活跃度

- `assignment_submit_count`
- `exam_submit_count`
- `task_participation_rate`
- `discussion_reply_count`

### 8.5 生活规律与资源使用

- `library_visit_count`
- `library_active_days`
- `running_punch_count`
- `morning_activity_rate`

## 9. 不做的事情

首版数据库设计明确不做以下事项：

- 不要求接入全部 27 张表
- 不要求把所有原始 Excel 逐张 raw 入 PostgreSQL
- 不要求首版建设通用特征注册中心
- 不要求一次性覆盖体测、奖学金、异动、毕业去向等全部增强域
- 不要求首版直接实现全量模型链路

## 10. 设计价值

该设计的价值在于：

- 保证数据库结构围绕分析目标，而不是围绕文件名堆砌
- 保证首版复杂度可控
- 保证后续可以稳定扩展到更多源表和更多分析维度
- 保证 V1 主链路先围绕 4 个核心识别维度打通

## 11. 下一步

基于本文档，下一阶段应继续产出：

1. 首版数据库 implementation plan
2. 表级字段映射清单
3. 每张事实表对应的源表字段归一规则
4. `student_term_features` 的指标计算规则

在 implementation plan 写出之前，不应直接进入数据库建表或全量接入实现。
