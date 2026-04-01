# V1 Eight-Dimension Profile Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the current four-dimension scoring and explanation chain with a term-level eight-dimension baseline built from real source tables, then expose the new results across offline artifacts, API payloads, and stage-one UI pages.

**Architecture:** Rebuild the system from the data layer upward. First extend `analytics-db` so it can produce a term-level eight-dimension feature table from the real XLSX sources. Then replace the old scoring and report generation rules in `model-stubs`, update `demo-api` to read the new artifacts, and finally update the frontend to display eight-dimension results clearly on overview, group, student, and methodology pages. Keep `group_segment` as a derived result from the new dimension space.

**Tech Stack:** Python 3.12, pandas, FastAPI, Vue 3, TypeScript, Vite, pytest, vitest

---

### Task 1: Freeze Source Mapping and Metric Names

**Files:**
- Modify: `docs/superpowers/specs/2026-03-31-v1-eight-dimension-profile-design.md`
- Reference: `C:/Users/Orion/Desktop/StudentBehavior/output_schema.txt`
- Reference: `docs/risk-label-and-model-design.md`

- [ ] **Step 1: Add explicit computable-metric tables to the spec**

For each of the 8 dimensions, extend the spec with:

- student key source
- term alignment rule
- concrete metric field names
- blocked/deferred sub-metrics if schema is insufficient

- [ ] **Step 2: Mark schema caveats explicitly in the spec**

Document these as explicit first-stage caveats:

- `上课信息统计表.xlsx` student-level linkage must be verified
- `上网统计.xlsx` does not support true 0:00-6:00 session counts

- [ ] **Step 3: Re-read the spec and confirm no metric claims exceed the real schema**

Run: `rg -n "0:00|6:00|深夜|抬头率|前排率|稳定度" docs/superpowers/specs/2026-03-31-v1-eight-dimension-profile-design.md`

Expected: any risky metric wording is either justified by source fields or clearly marked as caveated/deferred

### Task 2: Build Eight-Dimension Feature Aggregation in analytics-db

**Files:**
- Modify: `projects/analytics-db/src/student_behavior_analytics_db/build_demo_features_from_excels.py`
- Modify: `projects/analytics-db/tests/test_build_demo_features_from_excels.py`
- Reference: `projects/analytics-db/src/student_behavior_analytics_db/normalize_terms.py`

- [ ] **Step 1: Write failing tests for the new eight-dimension columns**

Add tests that expect the build output to contain at least these columns:

- `academic_base_score_raw`
- `class_engagement_score_raw`
- `online_activeness_score_raw`
- `library_immersion_score_raw`
- `network_habits_score_raw`
- `daily_routine_boundary_score_raw`
- `physical_resilience_score_raw`
- `appraisal_status_alert_score_raw`

Also expect per-dimension metric JSON or flattened metric columns where needed.

- [ ] **Step 2: Run the focused analytics-db tests to confirm failure**

Run: `uv run --project projects/analytics-db pytest projects/analytics-db/tests/test_build_demo_features_from_excels.py -q`

Expected: FAIL because the current build pipeline does not emit the frozen eight-dimension output

- [ ] **Step 3: Add student-key normalization helpers for all required source tables**

Implement or extend helpers so the build pipeline can normalize:

- `XH`
- `XSBH`
- `LOGIN_NAME`
- `USERNUM`
- `cardId/cardld`
- `IDSERTAL`

Document any table that cannot yet be mapped deterministically.

- [ ] **Step 4: Implement term alignment rules**

Add term derivation and alignment logic for:

- `KSSJ`
- `TEACH_TIME`
- `CREATE_TIME`
- `UPDATE_TIME`
- `visittime`
- `LOGINTIME`
- `PUNCH_DAY`
- `YDRQ`

Where a source only has school-year style fields, map to `term_key` using the same central normalization utilities.

- [ ] **Step 5: Implement academic-base aggregators**

Compute term-level metrics from `学生成绩.xlsx`:

- `term_gpa`
- `failed_course_count`
- `borderline_course_count`
- `attempted_credit_sum`
- `failed_course_ratio`

Store the raw result set needed for later score normalization.

- [ ] **Step 6: Implement class-engagement aggregators**

Compute term-level metrics from `考勤汇总.xlsx`:

- `attendance_rate`
- `late_count`
- `absence_count`
- `truancy_count`

If `上课信息统计表.xlsx` can be linked to students, also compute:

- `avg_head_up_rate`
- `avg_front_row_rate`
- `avg_bowing_rate`

If not, record those metrics as unavailable and keep the caveat visible in the build output metadata.

- [ ] **Step 7: Implement online-activeness aggregators**

Compute term-level metrics from:

- `课堂任务参与.xlsx`
- `线上学习（综合表现）.xlsx`

Include:

- `video_completion_rate`
- `video_watch_time_sum`
- `online_test_avg_score`
- `online_work_avg_score`
- `online_exam_avg_score`
- `forum_interaction_total`
- `platform_engagement_score`

- [ ] **Step 8: Implement library-immersion aggregators**

Compute term-level metrics from `图书馆打卡记录.xlsx`:

- `library_visit_count`
- `weekly_library_visit_avg`
- `avg_library_stay_minutes`
- `library_stay_duration_std`
- `weekday_library_ratio`

Use explicit in/out pairing rules and filter obviously invalid durations.

- [ ] **Step 9: Implement network-habits aggregators**

Compute term-level metrics from `上网统计.xlsx`:

- `monthly_online_duration_avg`
- `term_online_duration_sum`
- `online_duration_vs_school_avg_gap`

Do not fabricate deep-night metrics.

- [ ] **Step 10: Implement daily-routine-boundary aggregators**

Compute term-level metrics from `门禁数据.xlsx`:

- `first_daily_access_time_avg`
- `first_daily_access_time_std`
- `late_return_count`
- `late_return_ratio`
- `daily_access_time_variability`

- [ ] **Step 11: Implement physical-resilience aggregators**

Compute term-level metrics from:

- `体测数据.xlsx`
- `跑步打卡.xlsx`
- `日常锻炼.xlsx`

Include:

- `physical_test_avg_score`
- `physical_test_pass_flag`
- `weekly_running_count_avg`
- `weekly_exercise_count_avg`
- `exercise_habit_stability`

- [ ] **Step 12: Implement appraisal-status-alert aggregators**

Compute term-level metrics from:

- `奖学金获奖.xlsx`
- `学籍异动.xlsx`

Include:

- `scholarship_amount_sum`
- `scholarship_level_score`
- `status_change_count`
- `negative_status_alert_flag`

- [ ] **Step 13: Add raw-dimension outputs to the build result**

Emit all 8 raw dimension metric groups into the build output artifact so downstream code does not need to re-open XLSX files.

- [ ] **Step 14: Run focused analytics-db tests**

Run: `uv run --project projects/analytics-db pytest projects/analytics-db/tests/test_build_demo_features_from_excels.py -q`

Expected: PASS

- [ ] **Step 15: Run relevant analytics-db regression tests**

Run: `uv run --project projects/analytics-db pytest projects/analytics-db/tests/test_build_demo_features_from_excels.py projects/analytics-db/tests/test_cli.py -q`

Expected: PASS

### Task 3: Replace Four-Dimension Scoring in model-stubs

**Files:**
- Modify: `projects/model-stubs/src/student_behavior_model_stubs/scoring.py`
- Modify: `projects/model-stubs/src/student_behavior_model_stubs/build_outputs.py`
- Modify: `projects/model-stubs/src/student_behavior_model_stubs/templates.py`
- Modify: `projects/model-stubs/tests/test_scoring.py`
- Modify: `projects/model-stubs/tests/test_build_outputs.py`
- Modify: `projects/model-stubs/tests/test_templates.py`
- Modify: `projects/model-stubs/tests/test_cli.py`

- [ ] **Step 1: Write failing tests for eight-dimension score output**

Add tests that expect:

- `build_dimension_scores()` returns 8 dimensions
- dimension names exactly match the frozen 8 labels
- no legacy 4-dimension-only assumptions remain in report text

- [ ] **Step 2: Run focused model-stubs tests to confirm failure**

Run: `uv run --project projects/model-stubs pytest projects/model-stubs/tests/test_scoring.py projects/model-stubs/tests/test_build_outputs.py projects/model-stubs/tests/test_templates.py -q`

Expected: FAIL because the current implementation still returns the old 4-dimension chain

- [ ] **Step 3: Implement the new eight-dimension score builder**

Refactor `build_dimension_scores()` so it:

- reads the new raw metric columns or metric payloads emitted by analytics-db
- produces 8 normalized dimension scores
- preserves stable ordering and display labels

- [ ] **Step 4: Replace group-segment derivation to use the eight-dimension space**

Refactor `compute_group_segment()` so it derives labels from the new 8 scores rather than the old 4-score logic.

Do not change the fact that a readable business label is returned.

- [ ] **Step 5: Rewrite report factor selection**

Ensure `top_factors` are selected from the frozen 8 dimensions and no old 4-dimension wording survives.

- [ ] **Step 6: Rewrite intervention advice generation**

Make advice generation dimension-driven:

- weak dimensions drive intervention suggestions
- report text must explicitly name the new dimensions

- [ ] **Step 7: Add the new artifact outputs**

Extend build outputs to generate:

- `v2_student_results.csv`
- `v2_student_dimension_details.jsonl`
- `v2_student_reports.jsonl`
- `v2_group_profiles.json`
- `v2_overview_by_term.json`

Keep old artifact names only if one-cycle compatibility is needed, but the new files must be the primary targets.

- [ ] **Step 8: Run focused model-stubs tests**

Run: `uv run --project projects/model-stubs pytest projects/model-stubs/tests/test_scoring.py projects/model-stubs/tests/test_build_outputs.py projects/model-stubs/tests/test_templates.py -q`

Expected: PASS

- [ ] **Step 9: Run the full model-stubs suite**

Run: `uv run --project projects/model-stubs pytest projects/model-stubs/tests -q`

Expected: PASS

### Task 4: Update demo-api to Serve Eight-Dimension Results

**Files:**
- Modify: `projects/demo-api/src/student_behavior_demo_api/loaders.py`
- Modify: `projects/demo-api/src/student_behavior_demo_api/services.py`
- Modify: `projects/demo-api/src/student_behavior_demo_api/main.py`
- Modify: `projects/demo-api/tests/test_loaders.py`
- Modify: `projects/demo-api/tests/test_services.py`
- Modify: `projects/demo-api/tests/test_api.py`
- Modify: `projects/demo-api/tests/conftest.py`

- [ ] **Step 1: Write failing tests for eight-dimension profile payloads**

Add or update tests so they expect:

- `profile.dimension_scores` length is 8
- `groups` payload contains average 8-dimension summaries or factor references aligned to 8 dimensions
- `overview` includes the global 8-dimension summary payload

- [ ] **Step 2: Run focused demo-api tests to confirm failure**

Run: `uv run --project projects/demo-api pytest projects/demo-api/tests/test_loaders.py projects/demo-api/tests/test_services.py projects/demo-api/tests/test_api.py -q`

Expected: FAIL because current payloads only support the old dimension baseline

- [ ] **Step 3: Update artifact loaders**

Teach loaders to read the new primary artifacts:

- `v2_student_results.csv`
- `v2_student_dimension_details.jsonl`
- `v2_student_reports.jsonl`
- `v2_group_profiles.json`
- `v2_overview_by_term.json`

- [ ] **Step 4: Update profile service output**

Return:

- student header info
- risk fields
- `group_segment`
- 8-dimension score array
- term trend built from the new baseline

- [ ] **Step 5: Update report service output**

Return top factors and intervention advice referencing the 8 new dimensions only.

- [ ] **Step 6: Update groups service output**

Return per-group summaries that include:

- `group_segment`
- `student_count`
- `avg_risk_probability`
- 8-dimension average summary or equivalent explanation-friendly representation

- [ ] **Step 7: Update overview service output**

Add:

- global average 8-dimension profile
- risk distribution
- group distribution
- major/college comparison
- term summary

- [ ] **Step 8: Run focused demo-api tests**

Run: `uv run --project projects/demo-api pytest projects/demo-api/tests/test_loaders.py projects/demo-api/tests/test_services.py projects/demo-api/tests/test_api.py -q`

Expected: PASS

- [ ] **Step 9: Run the full demo-api suite**

Run: `uv run --project projects/demo-api pytest projects/demo-api/tests -q`

Expected: PASS

### Task 5: Rebuild Stage-One Frontend Pages Around Eight Dimensions

**Files:**
- Modify: `.worktrees/v1-demo-web/projects/demo-web/src/lib/types.ts`
- Modify: `.worktrees/v1-demo-web/projects/demo-web/src/lib/api.ts`
- Modify: `.worktrees/v1-demo-web/projects/demo-web/src/features/overview/OverviewPage.vue`
- Modify: `.worktrees/v1-demo-web/projects/demo-web/src/features/quadrants/QuadrantsPage.vue`
- Modify: `.worktrees/v1-demo-web/projects/demo-web/src/features/students/StudentPage.vue`
- Modify: `.worktrees/v1-demo-web/projects/demo-web/src/features/warnings/WarningsPage.vue` if needed
- Modify: `.worktrees/v1-demo-web/projects/demo-web/src/app/router.ts`
- Create: `.worktrees/v1-demo-web/projects/demo-web/src/features/methodology/MethodologyPage.vue`
- Modify tests under `.worktrees/v1-demo-web/projects/demo-web/tests/`

- [ ] **Step 1: Write failing frontend tests for eight-dimension results**

Update tests to expect:

- overview receives and displays 8-dimension global summary
- student profile displays 8 dimensions, not 4
- groups page reflects 8-dimension group summaries
- methodology page exists and is routable

- [ ] **Step 2: Run frontend tests to confirm failure**

Run: `npm run test`

Expected: FAIL because the current UI still assumes the old dimension shape

- [ ] **Step 3: Update frontend API normalization types**

Refactor TypeScript types and normalizers so they support:

- global 8-dimension summary
- group-level 8-dimension summaries
- student-level 8-dimension detail blocks

- [ ] **Step 4: Rebuild overview page**

Show:

- global 8-dimension average profile
- risk distribution
- group distribution
- major/college comparison
- model summary note

- [ ] **Step 5: Rebuild groups page**

Show:

- group cards
- student counts
- average risk
- strong/weak dimensions
- group comparison visualization

- [ ] **Step 6: Rebuild student page**

Show:

- header with risk + group
- 8-dimension radar or bar chart
- dimension detail cards
- top-factor explanations
- intervention advice
- term trend

- [ ] **Step 7: Add methodology page**

Create a page that explains:

- the 8 dimensions
- source tables
- metric definitions
- current stub boundaries

- [ ] **Step 8: Wire the new route**

Add `/about-results` or `/methodology` to the router and navigation.

- [ ] **Step 9: Run frontend tests**

Run: `npm run test`

Expected: PASS

- [ ] **Step 10: Run frontend build**

Run: `npm run build`

Expected: PASS

### Task 6: End-to-End Rebuild and Verification

**Files:**
- Verify only

- [ ] **Step 1: Rebuild the eight-dimension feature artifact**

Run the updated analytics-db build command that emits the new term-level feature output.

Expected: artifact generated successfully with 8-dimension raw metrics

- [ ] **Step 2: Rebuild the new model-stubs artifacts**

Run the updated `student-behavior-stubs build` command against the new feature artifact.

Expected: all `v2_*` result artifacts generated

- [ ] **Step 3: Start demo-api locally**

Run from `projects/demo-api` with any required `PYTHONPATH` setup so the app imports correctly.

Expected: server starts and `/api/analytics/groups` returns 200

- [ ] **Step 4: Start demo-web locally**

Run from `.worktrees/v1-demo-web/projects/demo-web`.

Expected: Vite server starts on the requested port

- [ ] **Step 5: Verify key requests**

Check:

- `GET /api/analytics/overview?term=...`
- `GET /api/analytics/groups?term=...`
- `GET /api/students/{id}/profile?term=...`
- `GET /api/students/{id}/report?term=...`

Expected: all return 200 and reflect the 8-dimension baseline

- [ ] **Step 6: Verify key pages**

Check:

- overview page shows the global 8-dimension profile
- groups page shows group cards with 8-dimension evidence
- student page shows 8-dimension profile and advice
- methodology page explains the 8-dimension source mapping

### Task 7: Final Documentation and Handoff

**Files:**
- Modify: `docs/handoff.md`
- Modify: `docs/v1-demo-runbook.md`
- Modify: `docs/session-progress.md`

- [ ] **Step 1: Record the eight-dimension migration**

Document:

- old 4-dimension chain replaced
- new 8-dimension baseline introduced
- new or primary artifacts
- current frontend stage-one page layout

- [ ] **Step 2: Record known residual risks**

Explicitly note:

- class-stat student linkage caveat
- network-stat late-night metric caveat
- any remaining stub elements in risk/advice/model summary

- [ ] **Step 3: Run final repository checks**

Run:

- `uv run --project projects/analytics-db pytest projects/analytics-db/tests/test_build_demo_features_from_excels.py projects/analytics-db/tests/test_cli.py -q`
- `uv run --project projects/model-stubs pytest projects/model-stubs/tests -q`
- `uv run --project projects/demo-api pytest projects/demo-api/tests -q`
- `npm run test`
- `npm run build`

Expected: all pass
