# V1 Eight-Dimension Calibration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Calibrate the existing eight-dimension term-level profile pipeline so each dimension yields a business-usable score, `high/medium/low` level, Chinese label, explanation sentence, and visible metric evidence.

**Architecture:** Keep the current stage-one data pipeline and UI structure, but insert a configuration-driven calibration layer into `model-stubs`. `analytics-db` remains responsible for term-level raw sub-metrics, `model-stubs` maps those sub-metrics into calibrated dimension objects, `demo-api` returns those richer objects directly, and the frontend updates existing cards/charts to show the calibrated labels and metric values instead of raw score-only output.

**Tech Stack:** Python 3.12, pandas, FastAPI, Vue 3, TypeScript, Vite, pytest, vitest

---

### Task 1: Freeze Calibration Contract in the Spec

**Files:**
- Modify: `docs/superpowers/specs/2026-03-31-v1-eight-dimension-profile-design.md`
- Reference: `C:/Users/Orion/Desktop/StudentBehavior/output_schema.txt`

- [ ] **Step 1: Add the calibrated payload contract to the spec**

Document one canonical dimension object with these fields:

- `dimension`
- `score`
- `level`
- `label`
- `metrics`
- `explanation`

- [ ] **Step 2: Add the first-pass field-level calibration table to the spec**

Freeze the current stage-two mapping for:

- `academic_base`
- `class_engagement`
- `online_activeness`
- `library_immersion`
- `network_habits`
- `daily_routine_boundary`
- `physical_resilience`
- `appraisal_status_alert`

Each mapping must state:

- raw fields
- threshold strategy (`fixed`, `quantile`, or `hybrid`)
- display metrics
- caveats for unavailable source granularity

- [ ] **Step 3: Re-read the spec for overclaims**

Run: `rg -n "深夜|0:00|6:00|直接.*学生级专注度|只显示标签|只显示 high|只显示 medium|只显示 low" docs/superpowers/specs/2026-03-31-v1-eight-dimension-profile-design.md`

Expected: risky wording is either removed or clearly caveated

### Task 2: Add Calibration Configuration to model-stubs

**Files:**
- Create: `projects/model-stubs/src/student_behavior_model_stubs/calibration.py`
- Modify: `projects/model-stubs/tests/test_config.py`
- Test: `projects/model-stubs/tests/test_scoring.py`

- [ ] **Step 1: Write the failing tests for calibration configuration loading**

Add tests that assert:

- all 8 dimensions are present in calibration config
- each dimension has at least one metric entry
- each dimension defines a `level` label map
- `network_habits` and `class_engagement` preserve the known caveats

- [ ] **Step 2: Run the focused config test and verify failure**

Run: `uv run --project projects/model-stubs pytest projects/model-stubs/tests/test_config.py -q`

Expected: FAIL because `calibration.py` and the new config contract do not exist yet

- [ ] **Step 3: Create the calibration configuration module**

Implement a focused module that exports:

- the ordered list of 8 calibrated dimensions
- metric-level rule declarations
- threshold strategy metadata
- Chinese `label` text for `high`, `medium`, `low`
- metric display metadata for UI/report output

Keep configuration data declarative; avoid mixing scoring logic into the configuration module.

- [ ] **Step 4: Re-run the focused config test**

Run: `uv run --project projects/model-stubs pytest projects/model-stubs/tests/test_config.py -q`

Expected: PASS

### Task 3: Calibrate Dimension Scores in model-stubs

**Files:**
- Modify: `projects/model-stubs/src/student_behavior_model_stubs/scoring.py`
- Modify: `projects/model-stubs/tests/test_scoring.py`

- [ ] **Step 1: Write the failing tests for calibrated dimension objects**

Add tests that expect `build_dimension_scores()` to return 8 entries where each entry contains:

- `dimension`
- `score`
- `level`
- `label`
- `metrics`
- `explanation`

Also assert that:

- `academic_base` uses the GPA / failed-course inputs
- `network_habits` does not fabricate deep-night metrics
- score values are in `0-1`
- labels are Chinese business labels, not just the raw level string

- [ ] **Step 2: Run the focused scoring tests and verify failure**

Run: `uv run --project projects/model-stubs pytest projects/model-stubs/tests/test_scoring.py -q`

Expected: FAIL because `build_dimension_scores()` still returns score-only objects

- [ ] **Step 3: Add metric normalization helpers**

Implement minimal helpers in `scoring.py` for:

- fixed-threshold bucket scoring
- quantile-derived scoring from the current frame or provided distribution context
- hybrid metric scoring
- safe float coercion and clamping

Keep helpers file-local unless multiple modules need them immediately.

- [ ] **Step 4: Implement the 8 calibrated dimension builders**

Refactor `build_dimension_scores()` so each dimension:

- reads the frozen raw fields
- computes a calibrated numeric score
- assigns `high/medium/low`
- resolves a Chinese business label
- emits visible metric values
- emits one business explanation sentence

- [ ] **Step 5: Keep group derivation on the new calibrated outputs**

Update `compute_group_segment()` only if needed so it uses the calibrated dimension space consistently, while preserving readable business group names.

- [ ] **Step 6: Re-run the focused scoring tests**

Run: `uv run --project projects/model-stubs pytest projects/model-stubs/tests/test_scoring.py -q`

Expected: PASS

### Task 4: Rebuild Reports and Overview Artifacts Around Calibrated Dimensions

**Files:**
- Modify: `projects/model-stubs/src/student_behavior_model_stubs/build_outputs.py`
- Modify: `projects/model-stubs/src/student_behavior_model_stubs/templates.py`
- Modify: `projects/model-stubs/tests/test_build_outputs.py`
- Modify: `projects/model-stubs/tests/test_templates.py`
- Modify: `projects/model-stubs/tests/test_cli.py`

- [ ] **Step 1: Write failing tests for calibrated artifact payloads**

Add tests that expect:

- `dimension_scores_json` contains calibrated objects, not score-only objects
- student reports reference metric-backed explanations
- overview payload includes dimension summary entries derived from calibrated scores
- group payloads preserve average calibrated score summaries

- [ ] **Step 2: Run the focused artifact tests and verify failure**

Run: `uv run --project projects/model-stubs pytest projects/model-stubs/tests/test_build_outputs.py projects/model-stubs/tests/test_templates.py projects/model-stubs/tests/test_cli.py -q`

Expected: FAIL because artifacts still assume the old simplified dimension structure

- [ ] **Step 3: Update artifact builders to serialize calibrated dimension objects**

Modify `build_outputs.py` so:

- `build_student_results()` stores the richer dimension objects
- `build_overview_by_term()` averages calibrated scores safely
- `build_student_reports()` passes calibrated dimension objects into report generation

- [ ] **Step 4: Update report templates to use labels, explanations, and metrics**

Modify `templates.py` so:

- top factors are chosen from calibrated dimensions
- factor explanations reuse the stored explanation text
- intervention advice still remains concise and deterministic
- report text reflects the new business semantics instead of score-only wording

- [ ] **Step 5: Re-run the focused artifact tests**

Run: `uv run --project projects/model-stubs pytest projects/model-stubs/tests/test_build_outputs.py projects/model-stubs/tests/test_templates.py projects/model-stubs/tests/test_cli.py -q`

Expected: PASS

### Task 5: Make demo-api Return the Calibrated Contract

**Files:**
- Modify: `projects/demo-api/src/student_behavior_demo_api/services.py`
- Modify: `projects/demo-api/tests/test_services.py`
- Modify: `projects/demo-api/tests/test_api.py`

- [ ] **Step 1: Write failing API/service tests for calibrated dimension payloads**

Add tests that expect:

- `get_student_profile()` returns calibrated dimension objects with metrics and explanations
- `get_groups()` preserves average score arrays and can surface representative top factors
- `get_overview()` keeps dimension summary available when artifacts are current

- [ ] **Step 2: Run the focused demo-api tests and verify failure**

Run: `uv run --project projects/demo-api pytest projects/demo-api/tests/test_services.py projects/demo-api/tests/test_api.py -q`

Expected: FAIL because current types still assume score-only dimension items

- [ ] **Step 3: Update API payload shaping**

Modify `services.py` so:

- profile responses pass calibrated dimension objects through unchanged
- trend rows preserve the calibrated dimension object structure
- group and overview aggregation logic continues to average only numeric `score` fields
- top factor extraction remains compatible with the richer report payload

- [ ] **Step 4: Re-run the focused demo-api tests**

Run: `uv run --project projects/demo-api pytest projects/demo-api/tests/test_services.py projects/demo-api/tests/test_api.py -q`

Expected: PASS

### Task 6: Update Frontend Types and Student/Group/Overview Displays

**Files:**
- Modify: `.worktrees/v1-demo-web/projects/demo-web/src/lib/types.ts`
- Modify: `.worktrees/v1-demo-web/projects/demo-web/src/lib/api.ts`
- Modify: `.worktrees/v1-demo-web/projects/demo-web/src/features/overview/OverviewPage.vue`
- Modify: `.worktrees/v1-demo-web/projects/demo-web/src/features/quadrants/QuadrantsPage.vue`
- Modify: `.worktrees/v1-demo-web/projects/demo-web/src/features/students/StudentPage.vue`
- Test: `.worktrees/v1-demo-web/projects/demo-web/src/features/warnings/query.ts`

- [ ] **Step 1: Write the failing frontend tests or type expectations**

If existing vitest coverage already touches these payloads, extend it to assert that a dimension entry now includes:

- `level`
- `label`
- `metrics`
- `explanation`

If no direct test exists, add one focused component or API-shape test instead of relying on runtime inspection only.

- [ ] **Step 2: Run the frontend tests to verify failure**

From `.worktrees/v1-demo-web/projects/demo-web`, run: `npm run test`

Expected: FAIL in the frontend worktree because the type contract and rendered fields do not yet match the richer API shape

- [ ] **Step 3: Update shared frontend types**

Modify `types.ts` and `api.ts` so `dimension_scores` are modeled as richer calibrated objects instead of score-only objects.

- [ ] **Step 4: Update the student page to show metric values**

Modify `StudentPage.vue` so each dimension card shows:

- numeric score
- Chinese label
- explanation
- 2-4 visible metric/value rows

Do not regress the current trend chart or group/risk header tags.

- [ ] **Step 5: Update overview and group views to use calibrated wording**

Modify `OverviewPage.vue` and `QuadrantsPage.vue` so:

- summary cards keep using numeric scores
- labels and factor wording are compatible with the new calibrated outputs
- where helpful, metric-backed explanations are visible without making the page noisy

- [ ] **Step 6: Re-run the frontend tests**

From `.worktrees/v1-demo-web/projects/demo-web`, run: `npm run test`

Expected: PASS

- [ ] **Step 7: Run the frontend build**

From `.worktrees/v1-demo-web/projects/demo-web`, run: `npm run build`

Expected: PASS

### Task 7: Rebuild Artifacts and Run End-to-End Verification

**Files:**
- Modify: `artifacts/model_stubs/v1_student_results.csv`
- Modify: `artifacts/model_stubs/v1_student_reports.jsonl`
- Modify: `artifacts/model_stubs/v1_overview_by_term.json`
- Modify: `artifacts/model_stubs/v1_model_summary.json`

- [ ] **Step 1: Rebuild the model-stubs artifacts**

Run:

```powershell
uv run --project projects/model-stubs python -c "from pathlib import Path; from student_behavior_model_stubs.cli import run_build; run_build(Path('artifacts/semester_features/v1_semester_features.csv'), Path('artifacts/model_stubs'))"
```

Expected: updated model-stub artifacts with calibrated dimension payloads

- [ ] **Step 2: Run the full Python regression suite**

Run:

```powershell
uv run --project projects/model-stubs pytest projects/model-stubs/tests -q
uv run --project projects/demo-api pytest projects/demo-api/tests -q
uv run --project projects/analytics-db pytest projects/analytics-db/tests/test_build_demo_features_from_excels.py projects/analytics-db/tests/test_cli.py -q
```

Expected: PASS for all listed suites

- [ ] **Step 3: Run API-level verification against real artifacts**

From `projects/demo-api`, run:

```powershell
$env:PYTHONPATH='src'
uv run python -c "from fastapi.testclient import TestClient; from student_behavior_demo_api.main import app; client=TestClient(app); paths=['/api/analytics/overview?term=2024-2','/api/analytics/groups?term=2024-2','/api/students/pjwrqxbj901/profile?term=2024-2','/api/students/pjwrqxbj901/report?term=2024-2']; [print(p, client.get(p).status_code) for p in paths]"
```

Expected: all listed endpoints return `200`

- [ ] **Step 4: Run the frontend verification suite**

From `.worktrees/v1-demo-web/projects/demo-web`, run:

```powershell
npm run test
npm run build
```

Expected: PASS

- [ ] **Step 5: Spot-check one calibrated student payload**

Inspect one real profile payload and confirm at least one dimension object includes:

- `score`
- `level`
- `label`
- non-empty `metrics`
- non-empty `explanation`

### Task 8: Review, Summarize, and Commit

**Files:**
- Reference: `docs/superpowers/specs/2026-03-31-v1-eight-dimension-profile-design.md`
- Reference: `docs/superpowers/plans/2026-04-01-v1-eight-dimension-calibration.md`

- [ ] **Step 1: Review the diff for scope drift**

Run: `git diff -- docs/superpowers/specs/2026-03-31-v1-eight-dimension-profile-design.md projects/model-stubs projects/demo-api .worktrees/v1-demo-web/projects/demo-web`

Expected: changes are limited to calibration, payload shaping, and UI display updates

- [ ] **Step 2: Summarize residual limitations**

Record any remaining caveats, especially:

- no real deep-night network metric
- classroom attention metrics still deferred unless linkage was proven

- [ ] **Step 3: Commit**

```bash
git add docs/superpowers/specs/2026-03-31-v1-eight-dimension-profile-design.md docs/superpowers/plans/2026-04-01-v1-eight-dimension-calibration.md projects/model-stubs projects/demo-api .worktrees/v1-demo-web/projects/demo-web artifacts/model_stubs
git commit -m "feat: calibrate eight-dimension profile outputs"
```
