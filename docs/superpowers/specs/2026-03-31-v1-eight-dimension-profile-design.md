# V1 Eight-Dimension Profile Design

Status: Draft for user review

Last Updated: 2026-03-31

## 1. Purpose

This document freezes the first-stage redesign that replaces the current four-dimension scoring and explanation chain with a strict eight-dimension, term-level analysis baseline built from real source tables.

This stage does **not** yet reorganize the whole system around the four upper-level analysis tasks. The first goal is narrower:

- replace the old four-dimension scoring chain
- build a real eight-dimension term-level profile baseline
- expose the new results across offline artifacts, API responses, and frontend pages

Only after this baseline is stable should the system be reorganized into:

1. 学业风险动态感知与预警
2. 学业轨迹演化与关键行为分析
3. 学生个体画像与群体分层分析
4. 发展方向与去向关联分析

## 2. Frozen Scope

The first-stage redesign is frozen to the following rules:

1. The core scoring and explanation chain must be rebuilt around exactly eight dimensions.
2. The analysis grain is fixed to `student_id + term_key`.
3. Dimension scores must come from real source tables listed in the competition schema. No approximate reuse of the old four-dimension outputs is allowed.
4. `group_segment` remains in the system, but it becomes a derived result built from the new eight-dimension baseline.
5. The frontend must focus on showing the eight-dimension results clearly before expanding the higher-level task narrative.

This stage must **not**:

- retain the old four-dimension scoring chain as a primary output
- mix old four-dimension wording with the new eight-dimension wording in the same page or API payload
- expand prematurely into many new business pages for the four upper-level tasks

## 3. Eight Frozen Dimensions

The system must standardize on the following eight dimensions:

1. 学业基础表现 (`academic_base`)
2. 课堂学习投入 (`class_engagement`)
3. 在线学习积极性 (`online_activeness`)
4. 图书馆沉浸度 (`library_immersion`)
5. 网络作息自律指数 (`network_habits`)
6. 早晚生活作息规律 (`daily_routine_boundary`)
7. 体质及运动状况 (`physical_resilience`)
8. 综合荣誉与异动预警 (`appraisal_status_alert`)

Each dimension must produce:

- one normalized dimension score
- one level label (`high`, `medium`, `low`)
- a stable set of term-level sub-metrics
- explanation-ready evidence for reports and UI presentation
- explicit metric values in UI-facing payloads, not just abstract labels

## 4. Source-Schema Feasibility

The source schema in `C:/Users/Orion/Desktop/StudentBehavior/output_schema.txt` is sufficient to support the overall eight-dimension baseline, but not every natural-language indicator is directly available as-is.

The implementation must distinguish between:

- **dimension definition**: frozen and unchanged
- **computable metrics**: strictly derived from real fields that actually exist

This means some dimensions require metric rewording to match the real schema, and some tempting indicators must be explicitly deferred instead of overstated.

### 4.1 Dimensions that are directly feasible

The following dimensions are directly feasible from the provided schema:

- 学业基础表现
- 在线学习积极性
- 图书馆沉浸度
- 早晚生活作息规律
- 体质及运动状况
- 综合荣誉与异动预警

### 4.2 Dimensions with schema caveats

The following dimensions are still part of the frozen design, but their sub-metrics must respect schema limitations:

- 课堂学习投入
  - `上课信息统计表.xlsx` contains classroom/session-level fields such as `HEAD_UP_RATE`, `FRONT_ROW_RATE`, and `BOWING_RATE`, but the schema does not expose a guaranteed student key.
  - Student-level linkage must be verified before any attention-related metric is treated as a student attribute.
  - If linkage cannot be proven, the dimension must fall back to attendance-derived term metrics and mark attention metrics as deferred.

- 网络作息自律指数
  - `上网统计.xlsx` provides monthly/term aggregated usage statistics such as `SWLJSC`, `XXPJZ`, `XN`, `XQ`, and `TJNY`.
  - The schema does not expose session-hour detail, so the first-stage implementation cannot claim true `0:00-6:00` or "深夜上网天数" metrics.
  - The dimension definition stays frozen, but the first computable metric set must use only the real aggregate network-usage fields.

### 4.3 Canonical student-id crosswalk policy

The canonical `student_id` for stage one is the normalized official student number, meaning:

- prefer `XH` wherever it exists
- treat any other source identifier as an alias that must be crosswalked to `XH`
- store the resolved canonical value in every student-level artifact and API payload as `student_id`

Crosswalk priority:

1. `XH` and `XSBH`
2. `IDSERTAL`
3. `cardId` / `cardld`
4. `USERNUM`
5. `LOGIN_NAME`

Mapping rules:

- `XH` maps directly to canonical `student_id`
- `XSBH` maps directly when it is the same official student number value as `XH`, otherwise it must be resolved through the roster crosswalk
- `IDSERTAL` maps to canonical `student_id` only after a unique one-to-one lookup against the official roster or a verified door-access identity map
- `cardId` and `cardld` are the same logical library-card identifier; normalize the column name to `cardId` in the build pipeline, then crosswalk to canonical `student_id`
- `USERNUM` maps to canonical `student_id` only when the running roster yields exactly one student match
- `LOGIN_NAME` maps to canonical `student_id` only when the online-learning roster yields exactly one student match

Crosswalk-source requirements:

- `LOGIN_NAME` is only considered usable for student-level output when a deterministic online-learning crosswalk exists in the delivered dataset bundle or a checked-in derived artifact built from that bundle
- `USERNUM` is only considered usable for student-level output when a deterministic running crosswalk exists in the delivered dataset bundle or a checked-in derived artifact built from that bundle
- if one of these crosswalk sources is absent, the affected source rows may still contribute QA counts, but the corresponding student-term metrics must remain null or deferred instead of being guessed

Partial, missing, or ambiguous mappings:

- if a source identifier cannot be mapped uniquely to one canonical `student_id`, do not guess
- unresolved rows may still be counted in source-level QA summaries, but they must not be assigned to a student-level profile
- student-level aggregates use only rows with an exact canonical match
- ambiguous identifiers should be recorded as unresolved in build metadata so the loss is visible

### 4.4 Stage-one deterministic metric rules

Where a metric is ambiguous, stage one must use one deterministic default rather than leaving the definition open-ended.

- `failed_course_count`
  - default rule: count rows whose normalized course score is strictly below `60`
  - if a course row only has grade-letter data, convert it through the shared grade normalization table first, then apply the same `60` threshold
  - blank or unparseable scores are excluded from the denominator and reported separately in metadata

- `borderline_course_count`
  - default rule: count rows whose normalized course score is greater than or equal to `60` and less than `70`
  - this is a stage-one buffer band, not a final pedagogical judgment

- `late_return_count`
  - default rule: count `LOGINSIGN = 1` records whose `LOGINTIME` falls in the late-night window `22:00:00` to `05:59:59`
  - if only one side of the door event is present, use that single record as the source of truth for the late-return count

- `platform_engagement_score`
  - default rule: normalize each available component to `0-100`, then compute an equal-weight average across non-missing components
  - stage-one components are `video_completion_rate`, `video_watch_time_sum`, `online_test_avg_score`, `online_work_avg_score`, `online_exam_avg_score`, and `forum_interaction_total`
  - missing components are ignored only if at least one component remains; otherwise the score is null

- `scholarship_level_score`
  - default rule: map award level to a deterministic ordinal score
  - suggested stage-one ladder: `国家级/特等=100`, `一等奖/一等=90`, `二等奖/二等=80`, `三等奖/三等=70`, other recognized awards `=60`, unknown or blank `=0`
  - if both `PDDJ` and `JLJB` exist, use the higher-priority field documented by the build pipeline and note the fallback in metadata

- `negative_status_alert_flag`
  - default rule: emit `true` only when a status field explicitly maps to a non-normal category such as leave, transfer out, suspension, withdrawal, or not-in-school
  - unknown codes must not be escalated into alerts; they remain `false` unless the code table explicitly marks them as negative
  - if `SFZX` is present and clearly indicates not-in-school, the flag is `true`

## 5. Field-Level Computable Metric Tables

Each dimension below records the source table, student key source, term-alignment rule, computable metrics, and the metrics that must remain caveated or deferred in stage one.

### 5.1 学业基础表现

**Source tables**

- `学生成绩.xlsx`

**Student key**

- `XH`

**Time alignment**

- derive `term_key` from `KSSJ` using the shared term normalization utility

**Primary raw fields**

- `JDCJ`
- `KCCJ`
- `DJCJ`
- `XF`
- `KSLXDM`
- `CXBKBZ`

**Computable metric table**

| Metric | Source field(s) | Computation | Status |
| --- | --- | --- | --- |
| `term_gpa` | `JDCJ`, `XF` | Credit-weighted term average over valid grade rows | Computable |
| `failed_course_count` | `KCCJ`, `DJCJ`, `KSLXDM` | Count rows below the stage-one pass threshold from section 4.4 | Computable |
| `borderline_course_count` | `KCCJ`, `DJCJ` | Count rows in the stage-one 60-69 band from section 4.4 | Computable with threshold normalization |
| `attempted_credit_sum` | `XF`, `CXBKBZ` | Sum attempted credits for included rows | Computable |
| `failed_course_ratio` | derived from the above | `failed_course_count / included_course_count` | Computable |

### 5.2 课堂学习投入

**Source tables**

- `考勤汇总.xlsx`
- `上课信息统计表.xlsx`

**Student key**

- `XH` from `考勤汇总.xlsx`
- `上课信息统计表.xlsx` linkage must be validated before student-level use

**Time alignment**

- attendance: derive `term_key` from `XN` + `XQ` + `RQ`
- class stats: derive `term_key` from `TEACH_TIME` only after verifying record-to-term mapping

**Primary raw fields**

- attendance:
  - `ZTDM`
  - `ZT`
  - `DKSJ`
- class stats:
  - `HEAD_UP_RATE`
  - `FRONT_ROW_RATE`
  - `BOWING_RATE`
  - `COURSE_CODE`

**Computable metric table**

| Metric | Source field(s) | Computation | Status |
| --- | --- | --- | --- |
| `attendance_rate` | `ZTDM`, `ZT` | Attendance rate over the term | Computable |
| `late_count` | `ZTDM`, `ZT`, `DKSJ` | Count late arrival records in the term | Computable |
| `absence_count` | `ZTDM`, `ZT` | Count absence records in the term | Computable |
| `truancy_count` | `ZTDM`, `ZT` | Count truancy records in the term | Computable |
| `avg_head_up_rate` | `HEAD_UP_RATE` | Term average only if student linkage is proven | Caveated, deferred until linkage is verified |
| `avg_front_row_rate` | `FRONT_ROW_RATE` | Term average only if student linkage is proven | Caveated, deferred until linkage is verified |
| `avg_bowing_rate` | `BOWING_RATE` | Term average only if student linkage is proven | Caveated, deferred until linkage is verified |

### 5.3 在线学习积极性

**Source tables**

- `课堂任务参与.xlsx`
- `线上学习（综合表现）.xlsx`

**Student key**

- `LOGIN_NAME`

**Time alignment**

- derive `term_key` from `SCHOOL_YEAR` or `CREATE_TIME` / `UPDATE_TIME` using the shared term normalization utility
- `线上学习（综合表现）.xlsx` should be aligned through `LOGIN_NAME` and any available term metadata from the build pipeline

**Primary raw fields**

- `VIDEOJOB_RATE`
- `VIDEOJOB_TIME`
- `TEST_AVGSCORE`
- `WORK_AVGSCORE`
- `EXAM_AVGSCORE`
- `BBS_NUM`
- `TOPIC_NUM`
- `REPLY_NUM`
- `PV`
- `BFB`

**Computable metric table**

| Metric | Source field(s) | Computation | Status |
| --- | --- | --- | --- |
| `video_completion_rate` | `VIDEOJOB_RATE` | Term average completion rate | Computable |
| `video_watch_time_sum` | `VIDEOJOB_TIME` | Sum of valid watch time | Computable |
| `online_test_avg_score` | `TEST_AVGSCORE` | Term average test score | Computable |
| `online_work_avg_score` | `WORK_AVGSCORE` | Term average work score | Computable |
| `online_exam_avg_score` | `EXAM_AVGSCORE` | Term average exam score | Computable |
| `forum_topic_count` | `TOPIC_NUM` | Count forum topics | Computable |
| `forum_reply_count` | `REPLY_NUM` | Count forum replies | Computable |
| `forum_interaction_total` | `BBS_NUM`, `TOPIC_NUM`, `REPLY_NUM` | Combined discussion activity count | Computable |
| `platform_engagement_score` | `BFB`, task fields above | Project-defined normalized blend | Computable |

### 5.4 图书馆沉浸度

**Source tables**

- `图书馆打卡记录.xlsx`

**Student key**

- normalize `cardId` / `cardld` to the canonical source-column name `cardId`, then crosswalk to `student_id`

**Time alignment**

- derive `term_key` from `visittime` using the shared term normalization utility

**Primary raw fields**

- `visittime`
- `direction`
- `gateno`

**Computable metric table**

| Metric | Source field(s) | Computation | Status |
| --- | --- | --- | --- |
| `library_visit_count` | `visittime`, `direction`, `gateno` | Count completed library visits, not raw gate events | Computable |
| `weekly_library_visit_avg` | `visittime` | Term visits divided by active weeks | Computable |
| `avg_library_stay_minutes` | `visittime`, `direction` | Paired in/out duration average | Computable only when in/out pairing is valid |
| `library_stay_duration_std` | `visittime`, `direction` | Std dev of paired stay durations | Computable only when in/out pairing is valid |
| `weekday_library_ratio` | `visittime` | Weekday visits / total visits | Computable |

### 5.5 网络作息自律指数

**Source tables**

- `上网统计.xlsx`

**Student key**

- `XSBH`

**Time alignment**

- derive `term_key` from `TJNY`, `XN`, and `XQ` using the shared term normalization utility

**Primary raw fields**

- `SWLJSC`
- `TJNY`
- `XN`
- `XQ`
- `XXPJZ`

**Computable metric table**

| Metric | Source field(s) | Computation | Status |
| --- | --- | --- | --- |
| `monthly_online_duration_avg` | `SWLJSC` | Average monthly online duration within the term window | Computable |
| `term_online_duration_sum` | `SWLJSC` | Sum of monthly online duration across the term | Computable |
| `online_duration_vs_school_avg_gap` | `SWLJSC`, `XXPJZ` | Student minus school-average gap | Computable |

**Caveat**

The first-stage implementation must not claim true `0:00-6:00` counts or "深夜上网天数" because the available schema is monthly aggregate only. Only aggregate usage intensity and school-average comparison are allowed in stage one.

### 5.6 早晚生活作息规律

**Source tables**

- `门禁数据.xlsx`

**Student key**

- `IDSERTAL`

**Time alignment**

- derive `term_key` from `LOGINTIME` using the shared term normalization utility

**Primary raw fields**

- `LOGINTIME`
- `LOGINSIGN`
- `LOGINADDRESS`

**Computable metric table**

| Metric | Source field(s) | Computation | Status |
| --- | --- | --- | --- |
| `first_daily_access_time_avg` | `LOGINTIME`, `LOGINSIGN` | Average first entry time per day across the term | Computable |
| `first_daily_access_time_std` | `LOGINTIME`, `LOGINSIGN` | Std dev of the first daily access time across days | Computable |
| `late_return_count` | `LOGINTIME`, `LOGINSIGN` | Count late-night exits or returns using the stage-one rule in section 4.4 | Computable with rule normalization |
| `late_return_ratio` | `LOGINTIME`, `LOGINSIGN` | Late returns / total events | Computable with rule normalization |
| `daily_access_time_variability` | `LOGINTIME` | Average within-day access span across days, separate from first-entry std dev | Computable |

### 5.7 体质及运动状况

**Source tables**

- `体测数据.xlsx`
- `跑步打卡.xlsx`
- `日常锻炼.xlsx`
- optional enrichment: `学生体能考核.xlsx`

**Student key**

- `XH`
- `USERNUM`

**Time alignment**

- `TCNF` for `体测数据.xlsx`
- derive `term_key` from `PUNCH_DAY`, `WEEKNUM`, and `XQ` using the shared term normalization utility
- use `USERNUM` only where it can be deterministically mapped back to `XH`

**Primary raw fields**

- `ZF`
- `BMI`
- `FHL`
- `WS`
- `LDTY`
- `PUNCH_DAY`
- `DKCS`

**Computable metric table**

| Metric | Source field(s) | Computation | Status |
| --- | --- | --- | --- |
| `physical_test_avg_score` | `ZF`, `TCNF` | Term average physical test score | Computable |
| `physical_test_pass_flag` | `ZF` | Pass flag from physical test score threshold | Computable |
| `weekly_running_count_avg` | `PUNCH_DAY`, `WEEKNUM` | Average weekly running punch count | Computable |
| `weekly_exercise_count_avg` | `DKCS`, `ZC`, `XQ` | Average weekly exercise punch count | Computable |
| `exercise_habit_stability` | `DKCS`, `PUNCH_DAY`, `WEEKNUM` | Variability / stability derived from repeated weekly counts | Computable as a variability proxy |

### 5.8 综合荣誉与异动预警

**Source tables**

- `奖学金获奖.xlsx`
- `学籍异动.xlsx`
- optional enrichment: `本科生综合测评.xlsx`

**Student key**

- `XSBH`
- `XH`

**Time alignment**

- derive `term_key` from `PDXN` and `YDRQ` using the shared term normalization utility

**Primary raw fields**

- scholarships:
  - `JXJMC`
  - `PDDJ`
  - `JLJB`
  - `FFJE`
- status changes:
  - `YDLBDM`
  - `YDYYDM`
  - `YDRQ`
  - `SFZX`

**Computable metric table**

| Metric | Source field(s) | Computation | Status |
| --- | --- | --- | --- |
| `scholarship_amount_sum` | `FFJE` | Sum of scholarship amounts within the term | Computable |
| `scholarship_level_score` | `PDDJ`, `JLJB` | Normalized award-level score using the deterministic ladder in section 4.4 | Computable |
| `status_change_count` | `YDLBDM`, `YDYYDM`, `YDRQ` | Count of status changes within the term | Computable |
| `negative_status_alert_flag` | `SFZX`, `YDLBDM`, `YDYYDM` | Alert flag for explicit negative status categories only | Computable |

## 6. Output Structure

The new eight-dimension baseline must not continue to rely on a single old-style `dimension_scores_json` field as the only foundation for the system.

The output structure must be logically split into:

1. student-term summary results
2. student-term-dimension details
3. student-term explanation/report results
4. term-level group results
5. term-level overview results

### 6.1 Student-term summary output

Recommended artifact:

- `artifacts/model_stubs/v2_student_results.csv`

Required fields:

- `student_id`
- `student_name`
- `major_name`
- `college_name` or `department_name`
- `term_key`
- `academic_base_score`
- `class_engagement_score`
- `online_activeness_score`
- `library_immersion_score`
- `network_habits_score`
- `daily_routine_boundary_score`
- `physical_resilience_score`
- `appraisal_status_alert_score`
- `profile_total_score`
- `risk_probability`
- `risk_level`
- `group_segment`

### 6.2 Student-term-dimension detail output

Recommended artifact:

- `artifacts/model_stubs/v2_student_dimension_details.jsonl`

Each record should contain:

- `student_id`
- `term_key`
- `dimension_code`
- `dimension_name`
- `dimension_score`
- `dimension_level`
- `dimension_label`
- `dimension_explanation`
- `metric_count`
- `metrics_json`
- `evidence_summary`

`metrics_json` minimum shape:

```json
[
  {
    "metric_code": "failed_course_count",
    "metric_name": "挂科门数",
    "value": 2,
    "source_fields": ["KCCJ", "DJCJ"],
    "aggregation_rule": "normalized_score < 60",
    "caveat_status": "computable"
  }
]
```

`metrics_json` must preserve the raw metric values that drive the dimension judgment so the frontend can display:

- the metric name
- the metric value
- the direction of influence when relevant
- a short note or caveat when the metric is deferred or schema-limited

### 6.3 Student-term explanation output

Recommended artifact:

- `artifacts/model_stubs/v2_student_reports.jsonl`

Each record should contain:

- `student_id`
- `term_key`
- `top_factors_json`
- `intervention_advice_json`
- `report_text`
- `report_version`

`top_factors_json` minimum shape:

```json
[
  {
    "dimension_code": "academic_base",
    "dimension_name": "学业基础表现",
    "factor_code": "failed_course_count",
    "factor_name": "挂科门数",
    "direction": "negative",
    "contribution_score": 0.28,
    "evidence_summary": "本学期不及格课程数偏高"
  }
]
```

`intervention_advice_json` minimum shape:

```json
[
  {
    "dimension_code": "class_engagement",
    "advice_title": "提高课堂投入",
    "advice_text": "优先减少迟到和缺勤；课堂注意力相关指标仅在学生级链路已验证时再纳入。",
    "priority": 1,
    "trigger_reason": "attendance_rate low"
  }
]
```

### 6.4 Group profile output

Recommended artifact:

- `artifacts/model_stubs/v2_group_profiles.json`

Required payload structure:

- `term_key`
- `group_segment`
- `student_count`
- `avg_risk_probability`
- `avg_dimension_scores_json`
- `top_factors_json`

`avg_dimension_scores_json` minimum shape:

```json
{
  "academic_base": 74.2,
  "class_engagement": 68.5,
  "online_activeness": 81.0,
  "library_immersion": 52.4,
  "network_habits": 63.1,
  "daily_routine_boundary": 70.0,
  "physical_resilience": 77.8,
  "appraisal_status_alert": 88.0
}
```

### 6.5 Overview output

Recommended artifact:

- `artifacts/model_stubs/v2_overview_by_term.json`

Required result areas:

- risk distribution
- group distribution
- global eight-dimension average profile
- major/college comparison
- term trends
- model summary references

Minimum overview payload shapes:

- `risk_distribution`
  ```json
  [
    { "risk_level": "high", "student_count": 12, "ratio": 0.08 },
    { "risk_level": "medium", "student_count": 31, "ratio": 0.21 },
    { "risk_level": "low", "student_count": 105, "ratio": 0.71 }
  ]
  ```

- `major_college_comparison`
  ```json
  [
    {
      "college_name": "计算机学院",
      "major_name": "软件工程",
      "student_count": 42,
      "avg_risk_probability": 0.34,
      "avg_dimension_scores_json": {
        "academic_base": 76.1,
        "class_engagement": 69.8
      }
    }
  ]
  ```

- `group_distribution`
  ```json
  [
    {
      "group_segment": "稳健型",
      "student_count": 58,
      "ratio": 0.39,
      "avg_risk_probability": 0.19
    }
  ]
  ```

### 6.6 Minimum payload contract

The stage-one payloads must treat the above JSON snippets as minimum shapes, not optional extras:

- arrays must always be arrays, even when empty
- dimension-score objects must use the frozen eight dimension codes as keys
- any missing evidence must be represented by empty arrays or null fields, not by inventing synthetic values
- `top_factors_json` and `intervention_advice_json` must be ordered by descending priority or contribution

## 7. API Implications

The API layer remains read-only but must be rebuilt around the new result artifacts.

### 7.1 Required API behavior changes

- `GET /api/students/{id}/profile`
  - must return eight dimension result objects, not the old four-dimension structure
  - each dimension object must include score, level, label, explanation, and metrics

- `GET /api/students/{id}/report`
  - explanations and advice must reference the eight frozen dimensions

- `GET /api/analytics/groups`
  - must expose group-level average eight-dimension profiles
  - group payloads must include representative metric summaries for each dimension where feasible

- `GET /api/analytics/overview`
  - must expose the global eight-dimension summary and organization comparison
  - overview payloads must include a visible dimension summary, not only risk/group counts

- `GET /api/models/summary`
  - may remain stub-based for now, but must explicitly describe the eight-dimension result baseline

### 7.2 Frozen nested payload shapes

The API layer must freeze the nested dimension payloads so backend and frontend can implement against one contract.

- `GET /api/students/{id}/profile`
  ```json
  {
    "student_id": "20240001",
    "student_name": "张三",
    "major_name": "软件工程",
    "group_segment": "学习投入稳定组",
    "risk_level": "medium",
    "risk_probability": 0.42,
    "dimension_scores": [
      {
        "dimension": "academic_base",
        "score": 72,
        "level": "medium",
        "label": "基础一般但可维持",
        "metrics": [
          {
            "metric": "学期GPA",
            "value": 2.9,
            "source_fields": ["JDCJ", "XF"],
            "direction": "positive",
            "caveat": null
          }
        ],
        "explanation": "该生当前学业基础总体稳定，但仍存在边缘课程和少量挂科风险。"
      }
    ],
    "trend": [
      {
        "term": "2024-2",
        "risk_probability": 0.42,
        "dimension_scores": []
      }
    ]
  }
  ```

- `GET /api/analytics/groups`
  ```json
  {
    "groups": [
      {
        "group_segment": "学习投入稳定组",
        "student_count": 58,
        "avg_risk_probability": 0.19,
        "avg_dimension_scores": [
          {
            "dimension": "academic_base",
            "score": 76.1
          }
        ],
        "representative_metrics": {
          "academic_base": [
            { "metric": "学期GPA", "value": 3.2 }
          ]
        },
        "top_factors": []
      }
    ]
  }
  ```

- `GET /api/analytics/overview`
  ```json
  {
    "student_count": 148,
    "risk_distribution": [],
    "group_distribution": [],
    "dimension_summary": [
      {
        "dimension": "academic_base",
        "score": 76.1,
        "representative_metrics": [
          { "metric": "学期GPA", "value": 3.05 }
        ]
      }
    ],
    "major_risk_summary": [],
    "trend_summary": { "terms": [] }
  }
  ```

Rules:

- nested `dimension_scores` objects must use the calibrated contract from section 11.2
- group and overview payloads may summarize metrics, but they must preserve actual numeric values rather than only textual labels
- if representative metrics cannot be computed safely for a dimension, return an empty array for that dimension instead of synthesizing a value

## 8. Frontend Implications

The first-stage frontend should be organized around visible results, not yet around the four upper-level tasks.

### 8.1 Required pages for stage one

1. `/overview`
2. `/groups`
3. `/students/:studentId`
4. `/about-results` or `/methodology`

### 8.2 Page responsibilities

**Overview**

- global eight-dimension average profile
- risk distribution
- group distribution
- major/college comparison
- model summary notes
- visible dimension metrics for the current term average profile

**Groups**

- group cards
- group counts
- average risk probability
- average eight-dimension profile
- group strong/weak dimensions
- representative dimension metrics, not just factor labels

**Student**

- individual eight-dimension profile
- dimension detail cards
- top factors
- intervention advice
- term trend
- explicit metric values for each dimension card

**Results/Methodology**

- eight dimension definitions
- source-table mapping
- metric definitions
- current stub boundaries

## 9. Derived Group Segment Policy

`group_segment` remains a required output, but it is no longer the semantic source of the system.

Instead:

- the eight-dimension baseline is primary
- `group_segment` is derived from the eight-dimension results
- explanations must flow from dimension evidence first, then summarize the derived group label

The implementation may keep readable business labels, but the grouping logic must be redesigned around the new eight-dimension space.

## 10. Delivery Strategy

The first-stage implementation order is frozen as follows:

1. freeze the eight-dimension design and field mapping
2. rebuild the `analytics-db` term-level feature baseline
3. rebuild `model-stubs` around eight dimensions
4. update `demo-api` to serve the new artifacts
5. update the frontend pages to show the new results

This stage must **not** simultaneously attempt:

- full four-task narrative restructuring
- formal model upgrade beyond current stub boundaries
- broad new page expansion unrelated to eight-dimension result visibility

## 11. Second-Stage Calibration Rules

After the first-stage eight-dimension baseline is visible across data, API, and UI, the next required step is dimension calibration.

The second-stage objective is not just to avoid zero-heavy scores. It must make every dimension business-interpretable by producing:

1. a numeric score
2. a level label (`high`, `medium`, `low`)
3. a human-readable business label
4. a business explanation sentence
5. explicit supporting metric values

### 11.1 Calibration policy

The frozen calibration strategy is a hybrid threshold system:

- use fixed thresholds where the metric has obvious pedagogical semantics
- use quantile thresholds where the metric is population-relative or strongly skewed
- avoid pure quantile-only dimensions when the result must be defendable in a competition presentation

Recommended dimension strategy split:

- fixed-threshold dominant
  - `academic_base`
  - `class_engagement`
  - `online_activeness`
  - `appraisal_status_alert`
- hybrid threshold
  - `library_immersion`
  - `network_habits`
  - `daily_routine_boundary`
  - `physical_resilience`

### 11.2 Required calibrated payload shape

Each dimension result must be able to support a UI payload shaped like:

```json
{
  "dimension": "学业基础表现",
  "score": 72,
  "level": "medium",
  "label": "基础一般但可维持",
  "metrics": [
    { "metric": "学期GPA", "value": 2.9 },
    { "metric": "挂科课程数", "value": 1 },
    { "metric": "及格边缘课程数", "value": 2 }
  ],
  "explanation": "该生当前学业基础总体稳定，但仍存在边缘课程和少量挂科风险。"
}
```

This shape is not optional. Second-stage implementation must not collapse the dimension back into a score-only or label-only result, and the UI must render the actual metric values rather than only the `high`/`medium`/`low` summary.

Canonical dimension object contract:

- `dimension`
  - stable dimension code or name, depending on the payload layer
- `score`
  - normalized numeric score in the `0-100` presentation range or the project-defined normalized range used by the layer
- `level`
  - one of `high`, `medium`, `low`
- `label`
  - business-facing Chinese label that explains the score in plain language
- `metrics`
  - array of display metric objects
  - each entry must expose the metric name and its actual value
  - metric entries may also include source fields, units, influence direction, and caveats when the source granularity is limited
- `explanation`
  - one sentence of business-facing explanation grounded in the displayed metrics

Minimum metric entry shape:

```json
{
  "metric": "学期GPA",
  "value": 2.9,
  "source_fields": ["JDCJ", "XF"],
  "direction": "positive",
  "caveat": null
}
```

The payload contract must preserve numeric evidence even when a dimension resolves to a simple level label.

### 11.3 Field-level calibration rule table

The following table freezes the first calibration draft for each dimension. Thresholds may be tuned later, but the raw field set, threshold strategy, and visible metrics should remain stable unless the schema proves insufficient.

| Dimension | Raw fields | Threshold strategy | Display metrics | Caveats for unavailable source granularity |
| --- | --- | --- | --- | --- |
| 学业基础表现 | `JDCJ`, `KCCJ`, `DJCJ`, `XF`, `KSLXDM`, `CXBKBZ` | Fixed thresholds | 学期GPA, 挂科门数, 边缘课程数, 挂科占比 | None; all metrics come from term-grade rows already available in the schema. |
| 课堂学习投入 | `ZTDM`, `ZT`, `DKSJ`; deferred only if validated later: `HEAD_UP_RATE`, `FRONT_ROW_RATE`, `BOWING_RATE`, `COURSE_CODE` | Fixed thresholds | 出勤率, 迟到次数, 旷课次数, 缺勤次数 | Classroom attention metrics are deferred until student-level linkage is proven; if linkage is absent, the dimension must rely on attendance-derived metrics only. |
| 在线学习积极性 | `VIDEOJOB_RATE`, `VIDEOJOB_TIME`, `TEST_AVGSCORE`, `WORK_AVGSCORE`, `EXAM_AVGSCORE`, `BBS_NUM`, `TOPIC_NUM`, `REPLY_NUM`, `PV`, `BFB` | Fixed + quantile hybrid | 视频完成率, 测验均分, 作业均分, 考试均分, 平台活跃度 | Student-level metrics require a deterministic `LOGIN_NAME -> student_id` crosswalk. If that crosswalk is unavailable, online-learning metrics must stay deferred rather than guessed. |
| 图书馆沉浸度 | `visittime`, `direction`, `gateno` | Hybrid | 入馆次数, 平均停留时长, 周均入馆次数 | Stay-duration metrics require valid in/out pairing; if pairing is incomplete, display visit-count metrics and clearly mark duration as unavailable. |
| 网络作息自律指数 | `SWLJSC`, `TJNY`, `XN`, `XQ`, `XXPJZ` | Hybrid, population-relative | 月均上网时长, 学期总上网时长, 相对学校平均值偏差 | Do not surface any deep-night or `0:00-6:00` session metric; the schema only supports aggregate usage intensity. |
| 早晚生活作息规律 | `LOGINTIME`, `LOGINSIGN`, `LOGINADDRESS` | Hybrid | 首次进出平均时间, 时间波动, 晚归次数, 晚归比例 | Late-return logic is allowed, but the metric must be derived from actual door records and not generalized into broader sleep claims. |
| 体质及运动状况 | `ZF`, `BMI`, `FHL`, `WS`, `LDTY`, `PUNCH_DAY`, `DKCS`; optional enrichment: `TCNF`, `ZC`, `XQ` | Hybrid | 体测均分, 是否达标, 周均跑步次数, 周均锻炼次数 | Running-derived metrics require a deterministic `USERNUM -> student_id` crosswalk. If that crosswalk is unavailable, keep the running metrics deferred and rely only on directly mapped physical-test/exercise metrics. |
| 综合荣誉与异动预警 | `FFJE`, `PDDJ`, `JLJB`, `YDLBDM`, `YDYYDM`, `YDRQ`, `SFZX` | Fixed-threshold dominant | 奖学金金额, 奖学金等级, 是否存在异动预警, 异动次数 | Negative status signals dominate when explicitly present; scholarship signals support the score but do not override a confirmed negative status. |

### 11.4 Dimension-specific first-pass calibration notes

- `academic_base`
  - fixed-threshold dominant because GPA and failure counts are directly interpretable
- `class_engagement`
  - fixed-threshold dominant until attention metrics are truly linked at student level; attendance-derived metrics remain the first-pass basis
- `online_activeness`
  - direct score thresholds for completion/performance, quantile support for engagement intensity
- `library_immersion`
  - visit count should be treated as distribution-relative; stay duration can use a fixed reasonable interval
- `network_habits`
  - cannot claim deep-night behavior from the current schema; calibration must stay grounded in aggregate usage intensity and school-average gap only
- `daily_routine_boundary`
  - late-return metrics use fixed thresholds, while stability/variability metrics use quantile support
- `physical_resilience`
  - physical test pass/fail remains fixed; sustained exercise behavior may need quantile support
- `appraisal_status_alert`
  - negative status signals must dominate the final score when present, even if scholarship signals are positive
## 12. Residual Risks

The following risks are known and acceptable at design time:

1. Some natural-language indicators must be rewritten into schema-accurate computable metrics.
2. `上课信息统计表.xlsx` may not support direct student-level attention linkage, so classroom attention metrics must remain deferred until a proven student key exists.
3. `上网统计.xlsx` may not support true late-night session metrics, so `0:00-6:00` and "深夜" day counts must remain blocked rather than approximated; only aggregate usage intensity is permitted.
4. Risk probability, risk level, explanation text, and model summary may remain partially stub-based in the first implementation round even after the eight-dimension migration.

## 13. Final Design Decision

The project will move to a strict, term-level, real-source-based eight-dimension baseline before any broader analysis-task reorganization.

Stage one success means:

- the old four-dimension chain is no longer the system's primary backbone
- the eight dimensions are visible and traceable in data, API, and UI
- group segmentation, explanations, and reports are all driven from the new eight-dimension baseline
