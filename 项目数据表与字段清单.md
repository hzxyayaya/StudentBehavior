# StudentBehavior 项目数据表与字段清单

更新时间：2026-04-06

## 1. 文档范围

本文档梳理当前项目中已经定义并使用的数据结构，分为两部分：

1. 数据库层表结构
2. 后端 `demo-api` 直接依赖的数据产物文件

说明：

- 数据库表主要来自 `projects/analytics-db/sql/*.sql`
- 当前演示后端 `projects/demo-api` 实际并不直接查询数据库，而是直接读取 `artifacts/model_stubs` 下的产物文件

## 2. 数据库层表结构

### 2.1 维表

#### 1) `students`

用途：学生基础信息维表。

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `student_id` | `text` | 学生唯一标识，主键 |
| `gender` | `text` | 性别 |
| `ethnicity` | `text` | 民族 |
| `political_status` | `text` | 政治面貌 |
| `major_name` | `text` | 专业名称 |
| `college_name` | `text` | 学院名称 |
| `class_name` | `text` | 班级名称 |
| `enrollment_year` | `integer` | 入学年份 |

#### 2) `terms`

用途：学期维表。

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `term_key` | `text` | 学期标识，主键，如 `2024-2` |
| `school_year` | `text` | 学年 |
| `term_no` | `integer` | 学期序号 |
| `term_name` | `text` | 学期名称 |
| `start_date` | `date` | 开始日期 |
| `end_date` | `date` | 结束日期 |
| `is_analysis_term` | `boolean` | 是否纳入分析范围 |

#### 3) `courses`

用途：课程维表。

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `course_id` | `text` | 课程唯一标识，主键 |
| `course_code` | `text` | 课程编码 |
| `course_name` | `text` | 课程名称 |
| `course_type` | `text` | 课程类型 |
| `credit` | `numeric(6,2)` | 学分 |
| `hours` | `integer` | 学时 |
| `assessment_type` | `text` | 考核方式 |

#### 4) `majors`

用途：专业维表。

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `major_id` | `text` | 专业唯一标识，主键 |
| `major_name` | `text` | 专业名称 |
| `college_name` | `text` | 所属学院 |

### 2.2 事实表

#### 5) `student_course_enrollments`

用途：学生选课记录。

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `enrollment_id` | `bigint` | 主键，自增 |
| `student_id` | `text` | 学生标识 |
| `term_key` | `text` | 学期标识 |
| `course_id` | `text` | 课程标识 |
| `course_code` | `text` | 课程编码 |
| `course_name` | `text` | 课程名称 |
| `source_file` | `text` | 来源文件 |
| `source_row_hash` | `text` | 来源行哈希 |

#### 6) `student_grade_records`

用途：学生成绩记录。

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `grade_record_id` | `bigint` | 主键，自增 |
| `student_id` | `text` | 学生标识 |
| `term_key` | `text` | 学期标识 |
| `course_id` | `text` | 课程标识 |
| `course_name` | `text` | 课程名称 |
| `score` | `numeric(6,2)` | 分数 |
| `gpa` | `numeric(4,2)` | 绩点 |
| `passed` | `boolean` | 是否通过 |
| `source_file` | `text` | 来源文件 |
| `source_row_hash` | `text` | 来源行哈希 |

#### 7) `student_attendance_records`

用途：学生考勤记录。

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `attendance_record_id` | `bigint` | 主键，自增 |
| `student_id` | `text` | 学生标识 |
| `term_key` | `text` | 学期标识 |
| `attendance_status` | `text` | 考勤状态 |
| `attended_at` | `date` | 考勤日期 |
| `source_file` | `text` | 来源文件 |
| `source_row_hash` | `text` | 来源行哈希 |

#### 8) `student_signin_events`

用途：学生签到事件。

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `signin_event_id` | `bigint` | 主键，自增 |
| `student_id` | `text` | 学生标识 |
| `term_key` | `text` | 学期标识 |
| `signed_in_at` | `timestamp` | 签到时间 |
| `source_file` | `text` | 来源文件 |
| `source_row_hash` | `text` | 来源行哈希 |

#### 9) `student_assignment_submissions`

用途：作业提交记录。

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `assignment_submission_id` | `bigint` | 主键，自增 |
| `student_id` | `text` | 学生标识 |
| `term_key` | `text` | 学期标识 |
| `assignment_name` | `text` | 作业名称 |
| `submitted_at` | `timestamp` | 提交时间 |
| `submission_status` | `text` | 提交状态 |
| `score` | `numeric(6,2)` | 作业得分 |
| `source_file` | `text` | 来源文件 |
| `source_row_hash` | `text` | 来源行哈希 |

#### 10) `student_exam_submissions`

用途：考试提交或考试结果记录。

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `exam_submission_id` | `bigint` | 主键，自增 |
| `student_id` | `text` | 学生标识 |
| `term_key` | `text` | 学期标识 |
| `exam_name` | `text` | 考试名称 |
| `submitted_at` | `timestamp` | 提交时间 |
| `score` | `numeric(6,2)` | 考试得分 |
| `source_file` | `text` | 来源文件 |
| `source_row_hash` | `text` | 来源行哈希 |

#### 11) `student_task_participation`

用途：任务参与记录。

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `task_participation_id` | `bigint` | 主键，自增 |
| `student_id` | `text` | 学生标识 |
| `term_key` | `text` | 学期标识 |
| `task_name` | `text` | 任务名称 |
| `participated_at` | `timestamp` | 参与时间 |
| `participation_status` | `text` | 参与状态 |
| `source_file` | `text` | 来源文件 |
| `source_row_hash` | `text` | 来源行哈希 |

#### 12) `student_discussion_events`

用途：讨论区互动记录。

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `discussion_event_id` | `bigint` | 主键，自增 |
| `student_id` | `text` | 学生标识 |
| `term_key` | `text` | 学期标识 |
| `discussion_topic` | `text` | 讨论主题 |
| `replied_at` | `timestamp` | 回复时间 |
| `reply_count` | `integer` | 回复次数 |
| `source_file` | `text` | 来源文件 |
| `source_row_hash` | `text` | 来源行哈希 |

#### 13) `student_library_visits`

用途：图书馆访问记录。

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `library_visit_id` | `bigint` | 主键，自增 |
| `student_id` | `text` | 学生标识 |
| `term_key` | `text` | 学期标识 |
| `visited_at` | `timestamp` | 到馆时间 |
| `visit_date` | `date` | 到馆日期 |
| `source_file` | `text` | 来源文件 |
| `source_row_hash` | `text` | 来源行哈希 |

#### 14) `student_running_events`

用途：跑步或运动打卡记录。

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `running_event_id` | `bigint` | 主键，自增 |
| `student_id` | `text` | 学生标识 |
| `term_key` | `text` | 学期标识 |
| `ran_at` | `timestamp` | 跑步时间 |
| `run_date` | `date` | 跑步日期 |
| `distance_km` | `numeric(6,2)` | 跑步距离，公里 |
| `source_file` | `text` | 来源文件 |
| `source_row_hash` | `text` | 来源行哈希 |

#### 15) `student_evaluation_labels`

用途：学生评价标签或风险标签记录。

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `evaluation_label_id` | `bigint` | 主键，自增 |
| `student_id` | `text` | 学生标识 |
| `term_key` | `text` | 学期标识 |
| `risk_label` | `text` | 风险标签 |
| `evaluation_source` | `text` | 标签来源 |
| `source_file` | `text` | 来源文件 |
| `source_row_hash` | `text` | 来源行哈希 |

### 2.3 汇总特征表

#### 16) `student_term_features`

用途：学生学期级别特征汇总表，作为模型和后续产物生成的核心输入。

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `student_id` | `text` | 学生标识，联合主键 |
| `term_key` | `text` | 学期标识，联合主键 |
| `major_name` | `text` | 专业名称 |
| `college_name` | `text` | 学院名称 |
| `avg_course_score` | `numeric(6,2)` | 平均课程成绩 |
| `failed_course_count` | `integer` | 不及格课程数 |
| `avg_gpa` | `numeric(4,2)` | 平均绩点 |
| `major_rank_pct` | `numeric(6,2)` | 专业内排名百分位 |
| `risk_label` | `text` | 风险标签 |
| `attendance_record_count` | `integer` | 考勤记录数 |
| `attendance_normal_rate` | `numeric(6,4)` | 正常考勤率 |
| `selected_course_count` | `integer` | 选课门数 |
| `sign_event_count` | `integer` | 签到事件数 |
| `assignment_submit_count` | `integer` | 作业提交次数 |
| `exam_submit_count` | `integer` | 考试提交次数 |
| `task_participation_rate` | `numeric(6,4)` | 任务参与率 |
| `discussion_reply_count` | `integer` | 讨论回复次数 |
| `library_visit_count` | `integer` | 图书馆访问次数 |
| `library_active_days` | `integer` | 图书馆活跃天数 |
| `running_punch_count` | `integer` | 跑步打卡次数 |
| `morning_activity_rate` | `numeric(6,4)` | 早间活动率 |

## 3. 后端 `demo-api` 直接依赖的数据产物文件

说明：下面这些不是数据库表，但它们是当前后端接口直接读取的核心“数据源”。

### 3.1 `v1_student_results.csv`

用途：学生学期级风险与画像结果主表。

主要字段：

| 字段名 | 说明 |
| --- | --- |
| `student_id` | 学生标识 |
| `term_key` | 学期标识 |
| `student_name` | 学生名称 |
| `major_name` | 专业名称 |
| `group_segment` | 分群标签 |
| `risk_probability` | 风险概率 |
| `base_risk_score` | 基础风险分 |
| `risk_adjustment_score` | 行为修正分 |
| `adjusted_risk_score` | 调整后风险分 |
| `risk_level` | 风险等级 |
| `risk_delta` | 风险变化值 |
| `risk_change_direction` | 风险变化方向 |
| `dimension_scores_json` | 八维度结果 JSON |
| `top_risk_factors_json` | 主要风险因子 JSON |
| `top_protective_factors_json` | 主要保护因子 JSON |
| `base_risk_explanation` | 基础风险解释 |
| `behavior_adjustment_explanation` | 行为修正解释 |
| `risk_change_explanation` | 风险变化解释 |

### 3.2 `v1_student_reports.jsonl`

用途：学生个体报告结果文件。

常见字段：

| 字段名 | 说明 |
| --- | --- |
| `student_id` | 学生标识 |
| `term_key` | 学期标识 |
| `top_factors` | 主要因子 |
| `intervention_advice` | 干预建议 |
| `report_text` | 报告正文 |
| `base_risk_explanation` | 基础风险解释 |
| `behavior_adjustment_explanation` | 行为修正解释 |
| `risk_change_explanation` | 风险变化解释 |
| `intervention_plan` | 干预计划 |

### 3.3 `v1_overview_by_term.json`

用途：学期总览结果文件。

核心字段：

| 字段名 | 说明 |
| --- | --- |
| `term_buckets` | 各学期总览桶 |
| `student_count` | 学生数 |
| `risk_distribution` | 风险分布 |
| `group_distribution` | 群体分布 |
| `major_risk_summary` | 专业风险摘要 |
| `trend_summary` | 趋势摘要 |

### 3.4 `v1_model_summary.json`

用途：模型摘要文件。

字段：

| 字段名 | 说明 |
| --- | --- |
| `cluster_method` | 聚类方法 |
| `risk_model` | 风险模型 |
| `target_label` | 目标标签 |
| `auc` | 模型指标 |
| `updated_at` | 更新时间 |

### 3.5 `v1_warnings.json`

用途：产物构建过程的预警或统计摘要文件。

当前可见字段：

| 字段名 | 说明 |
| --- | --- |
| `generated_at` | 生成时间 |
| `input_row_count` | 输入行数 |
| `output_row_count` | 输出行数 |
| `dropped_row_count` | 丢弃行数 |
| `null_metric_summary` | 空指标统计 |
| `notes` | 备注信息 |

## 4. 当前结论

当前项目定义的数据库表共 16 张：

- 4 张维表
- 11 张事实表
- 1 张学期特征汇总表

当前已运行的演示后端主要直接消费 `artifacts/model_stubs` 下的产物文件，而不是直接查询上述数据库表。
