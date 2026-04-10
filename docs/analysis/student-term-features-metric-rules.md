# student_term_features 指标规则

## 1. 目标

`student_term_features` 是首版分析 mart 的核心宽表，主键为 `student_id + term_key`。  
它只汇总当前已经冻结、且能够稳定对齐到学期粒度的来源，不引入猜测性推断。

## 2. 输入来源

### 2.1 维度输入

- `students`
- `terms`

### 2.2 事实输入

- `student_grade_records`
- `student_attendance_records`
- `student_course_enrollments`
- `student_signin_events`
- `student_assignment_submissions`
- `student_exam_submissions`
- `student_task_participation`
- `student_discussion_events`
- `student_library_visits`
- `student_running_events`
- `student_evaluation_labels`

### 2.3 Draft source 处理

`student_assignment_submissions`、`student_exam_submissions`、`student_task_participation`、`student_discussion_events` 当前在 Task 7 里按 `Draft source` 处理。  
宽表构建器只在这些事实表已经被显式喂入、且能稳定匹配到 `student_id + term_key` 时才使用它们；如果输入为空，相关指标保持 `null`，不补假值。

## 3. 字段规则

| 字段 | 来源 | 聚合公式 | 空值处理 |
|---|---|---|---|
| `major_name` | `students` | 按 `student_id` 取首个非空值 | 无匹配则 `null` |
| `college_name` | `students` | 按 `student_id` 取首个非空值 | 无匹配则 `null` |
| `avg_course_score` | `student_grade_records` | 同一 `student_id + term_key` 下 `score` 的算术平均 | 无成绩则 `null` |
| `failed_course_count` | `student_grade_records` | `passed = false` 的条数；若 `passed` 缺失，则退回 `score < 60` | 无成绩则 `null` |
| `avg_gpa` | `student_grade_records` | 同一学期 `gpa` 的算术平均 | 无成绩则 `null` |
| `major_rank_pct` | 预留字段 | 当前冻结 loader 未保留原始名次百分比，先不造值 | 统一输出 `null` |
| `risk_label` | `student_evaluation_labels` | 同一学期取最大值，表示是否存在风险标签 | 无标签则 `null` |
| `attendance_record_count` | `student_attendance_records` | 同一学期记录条数 | 无记录则 `null` |
| `attendance_normal_rate` | `student_attendance_records` | `present/normal/on_time/出勤/正常` 条数 ÷ 总条数 | 无记录则 `null` |
| `selected_course_count` | `student_course_enrollments` | 同一学期选课条数 | 无记录则 `null` |
| `sign_event_count` | `student_signin_events` | 同一学期签到条数 | 无记录则 `null` |
| `assignment_submit_count` | `student_assignment_submissions` | 同一学期作业提交条数 | 无记录则 `null` |
| `exam_submit_count` | `student_exam_submissions` | 同一学期考试提交条数 | 无记录则 `null` |
| `task_participation_rate` | `student_task_participation` | 同一学期 `task_rate` 的算术平均 | 无记录则 `null` |
| `discussion_reply_count` | `student_discussion_events` | 同一学期回复条数 | 无记录则 `null` |
| `library_visit_count` | `student_library_visits` | 同一学期进馆条数 | 无记录则 `null` |
| `library_active_days` | `student_library_visits` | 同一学期按 `visit_date` 去重后的天数 | 无记录则 `null` |
| `running_punch_count` | `student_running_events` | 同一学期跑步打卡条数 | 无记录则 `null` |
| `morning_activity_rate` | `student_running_events` | `ran_at` 早于 `07:00:00` 的条数 ÷ 跑步条数 | 无记录则 `null` |

## 4. 排除规则

- 不使用模糊日期、月份或周次反推学期。
- 不使用未冻结的 `TERM_ID -> term_key` 或其它外部映射表。
- Task 7 的 Draft source 为空时，不补零值假装存在真实事件。
- 若某个事实表没有落到 `student_id + term_key`，该表不参与该学期的指标计算。

## 5. 口径说明

- `major_rank_pct` 在当前版本保留为可空字段，仅用于后续如果补齐原始测评名次信息时直接接入。
- `risk_label` 不是模型预测结果，而是来自 `student_evaluation_labels` 的监督标签。
- 所有聚合都以学期为粒度，输出行只代表一个 `student_id + term_key`。
