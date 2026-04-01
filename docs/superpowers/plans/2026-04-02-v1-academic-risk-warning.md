# Academic Risk Warning Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a complete academic-performance-risk warning loop on top of the existing eight-dimension semester profile pipeline, including risk scoring, warning filters, explanations, and intervention views.

**Architecture:** Keep the existing semester-feature pipeline and eight-dimension outputs intact, then layer a mixed risk mechanism on top: academic-result signals produce the base risk score, non-academic dimensions adjust that score, and the final adjusted score maps to four warning levels. Expose the new risk contract through `demo-api`, then rebuild overview, groups, warnings, and student views around the richer warning payload.

**Tech Stack:** Python (`uv`, pytest, FastAPI), Vue 3 + TypeScript + Vite + Vitest, CSV/JSON offline artifacts

---

## File Map

### Risk computation and artifacts

- Modify: `projects/model-stubs/src/student_behavior_model_stubs/scoring.py`
- Create: `projects/model-stubs/src/student_behavior_model_stubs/risk_calibration.py`
- Modify: `projects/model-stubs/src/student_behavior_model_stubs/build_outputs.py`
- Modify: `projects/model-stubs/src/student_behavior_model_stubs/templates.py`
- Test: `projects/model-stubs/tests/test_scoring.py`
- Test: `projects/model-stubs/tests/test_build_outputs.py`
- Test: `projects/model-stubs/tests/test_templates.py`

### API contract and service shaping

- Modify: `projects/demo-api/src/student_behavior_demo_api/services.py`
- Modify: `projects/demo-api/src/student_behavior_demo_api/main.py`
- Test: `projects/demo-api/tests/test_services.py`
- Test: `projects/demo-api/tests/test_main.py`

### Frontend warning experience

- Modify: `projects/demo-web/src/lib/types.ts`
- Modify: `projects/demo-web/src/lib/api.ts`
- Modify: `projects/demo-web/src/features/overview/OverviewPage.vue`
- Modify: `projects/demo-web/src/features/quadrants/QuadrantsPage.vue`
- Modify: `projects/demo-web/src/features/warnings/WarningsPage.vue`
- Modify: `projects/demo-web/src/features/students/StudentPage.vue`
- Test: `projects/demo-web/tests/api.test.ts`
- Test: `projects/demo-web/tests/flow.test.ts`
- Test: `projects/demo-web/tests/warnings-query.test.ts`

## Task 1: Add Risk Calibration Engine

**Files:**
- Create: `projects/model-stubs/src/student_behavior_model_stubs/risk_calibration.py`
- Test: `projects/model-stubs/tests/test_scoring.py`

- [ ] **Step 1: Write failing tests for base-risk, adjustment, and level mapping**

Add tests that assert:
- low GPA / many failed courses produce a high `base_risk_score`
- strong non-academic dimensions can reduce the adjusted score
- weak non-academic dimensions can increase the adjusted score
- final level maps to `高风险 / 较高风险 / 一般风险 / 低风险`

- [ ] **Step 2: Run the targeted tests to confirm failure**

Run:

```powershell
uv run --project projects/model-stubs pytest projects/model-stubs/tests/test_scoring.py -q
```

Expected: FAIL because the academic-risk calibration layer does not exist yet.

- [ ] **Step 3: Implement minimal calibration helpers**

Create `risk_calibration.py` with focused helpers for:
- base academic risk score
- risk adjustment score from non-academic dimensions
- adjusted risk score clamping
- four-level mapping
- risk delta / direction

- [ ] **Step 4: Wire `scoring.py` to use the new calibration helpers**

Extend the scoring payload to include:
- `base_risk_score`
- `risk_adjustment_score`
- `adjusted_risk_score`
- `risk_level`
- `risk_delta`
- `risk_change_direction`

- [ ] **Step 5: Run the targeted tests again**

Run:

```powershell
uv run --project projects/model-stubs pytest projects/model-stubs/tests/test_scoring.py -q
```

Expected: PASS

- [ ] **Step 6: Commit**

```powershell
git add projects/model-stubs/src/student_behavior_model_stubs/risk_calibration.py projects/model-stubs/src/student_behavior_model_stubs/scoring.py projects/model-stubs/tests/test_scoring.py
git commit -m "feat: add academic risk calibration"
```

## Task 2: Emit Richer Warning Artifacts

**Files:**
- Modify: `projects/model-stubs/src/student_behavior_model_stubs/build_outputs.py`
- Modify: `projects/model-stubs/src/student_behavior_model_stubs/templates.py`
- Test: `projects/model-stubs/tests/test_build_outputs.py`
- Test: `projects/model-stubs/tests/test_templates.py`

- [ ] **Step 1: Write failing tests for warning artifact fields**

Add tests that assert the student artifact rows and report payloads include:
- `base_risk_score`
- `risk_adjustment_score`
- `adjusted_risk_score`
- `risk_delta`
- `risk_change_direction`
- `top_risk_factors`
- `top_protective_factors`
- `base_risk_explanation`
- `behavior_adjustment_explanation`
- `risk_change_explanation`

- [ ] **Step 2: Run the targeted tests to confirm failure**

Run:

```powershell
uv run --project projects/model-stubs pytest projects/model-stubs/tests/test_build_outputs.py projects/model-stubs/tests/test_templates.py -q
```

Expected: FAIL because the richer warning payload is not emitted yet.

- [ ] **Step 3: Update build output assembly**

Modify `build_outputs.py` so warning rows and overview summaries include:
- four-band distribution
- risk trend summary
- top warning factors
- intervention priority summary

- [ ] **Step 4: Update report templates**

Modify `templates.py` to generate:
- base-risk explanation
- behavior-adjustment explanation
- risk-change explanation
- intervention plan text aligned to the four warning levels

- [ ] **Step 5: Rebuild artifacts in the local artifact directory**

Run:

```powershell
uv run --project projects/model-stubs python -c "from pathlib import Path; from student_behavior_model_stubs.cli import run_build; run_build(Path('artifacts/semester_features/v1_semester_features.csv'), Path('artifacts/model_stubs'))"
```

Expected: refreshed `artifacts/model_stubs/*` files with the new warning fields.

- [ ] **Step 6: Run the targeted tests again**

Run:

```powershell
uv run --project projects/model-stubs pytest projects/model-stubs/tests/test_build_outputs.py projects/model-stubs/tests/test_templates.py -q
```

Expected: PASS

- [ ] **Step 7: Commit**

```powershell
git add projects/model-stubs/src/student_behavior_model_stubs/build_outputs.py projects/model-stubs/src/student_behavior_model_stubs/templates.py projects/model-stubs/tests/test_build_outputs.py projects/model-stubs/tests/test_templates.py artifacts/model_stubs
git commit -m "feat: emit academic risk warning artifacts"
```

## Task 3: Expose Warning Contract Through Demo API

**Files:**
- Modify: `projects/demo-api/src/student_behavior_demo_api/services.py`
- Modify: `projects/demo-api/src/student_behavior_demo_api/main.py`
- Test: `projects/demo-api/tests/test_services.py`
- Test: `projects/demo-api/tests/test_main.py`

- [ ] **Step 1: Write failing API tests for the new warning fields**

Add tests that assert:
- `/api/analytics/overview` returns risk-band distribution and risk-factor summary
- `/api/analytics/groups` returns average risk score, average risk level, amplifiers, and protective factors
- `/api/warnings` returns the richer student warning payload
- `/api/students/{id}/profile` and `/report` return risk explanations and trend metadata

- [ ] **Step 2: Run the targeted tests to confirm failure**

Run:

```powershell
uv run --project projects/demo-api pytest projects/demo-api/tests/test_services.py projects/demo-api/tests/test_main.py -q
```

Expected: FAIL because the API still exposes the older warning contract.

- [ ] **Step 3: Extend the service layer to read and shape the richer warning payload**

Modify `services.py` to:
- parse the new warning fields from artifact rows
- expose risk change summaries
- expose risk amplifiers and protective factors
- support `risk_change_direction` filtering

- [ ] **Step 4: Update FastAPI response shapes and route behavior**

Modify `main.py` so response examples, schemas, and route behavior match the richer warning contract.

- [ ] **Step 5: Run the targeted tests again**

Run:

```powershell
uv run --project projects/demo-api pytest projects/demo-api/tests/test_services.py projects/demo-api/tests/test_main.py -q
```

Expected: PASS

- [ ] **Step 6: Smoke-test the running API**

Run:

```powershell
uv run --project projects/demo-api python -c "from fastapi.testclient import TestClient; from student_behavior_demo_api.main import app; client=TestClient(app); print(client.get('/api/analytics/overview?term=2024-2').status_code); print(client.get('/api/warnings?term=2024-2').status_code); print(client.get('/api/students/pjwrqxbj901/report?term=2024-2').status_code)"
```

Expected: `200` for all requests.

- [ ] **Step 7: Commit**

```powershell
git add projects/demo-api/src/student_behavior_demo_api/services.py projects/demo-api/src/student_behavior_demo_api/main.py projects/demo-api/tests
git commit -m "feat: expose academic risk warning api contract"
```

## Task 4: Rebuild Overview and Groups Risk Views

**Files:**
- Modify: `projects/demo-web/src/lib/types.ts`
- Modify: `projects/demo-web/src/lib/api.ts`
- Modify: `projects/demo-web/src/features/overview/OverviewPage.vue`
- Modify: `projects/demo-web/src/features/quadrants/QuadrantsPage.vue`
- Test: `projects/demo-web/tests/api.test.ts`
- Test: `projects/demo-web/tests/flow.test.ts`

- [ ] **Step 1: Write failing frontend tests for overview/groups risk UI**

Add tests that assert the overview and groups pages can render:
- four-band risk distribution
- risk trend summary
- top warning factors
- group-level average risk score and level
- group amplifiers and protective factors

- [ ] **Step 2: Run the targeted tests to confirm failure**

Run:

```powershell
npm run test -- --run tests/api.test.ts tests/flow.test.ts
```

Expected: FAIL because the UI still targets the older warning summary shape.

- [ ] **Step 3: Update shared frontend types and API mappers**

Modify:
- `src/lib/types.ts`
- `src/lib/api.ts`

so the app can consume the richer warning payload without type gaps.

- [ ] **Step 4: Update overview and groups pages**

Modify:
- `OverviewPage.vue`
- `QuadrantsPage.vue`

to display the new risk summaries, amplifiers, protective factors, and group warning comparisons.

- [ ] **Step 5: Run the targeted tests again**

Run:

```powershell
npm run test -- --run tests/api.test.ts tests/flow.test.ts
```

Expected: PASS

- [ ] **Step 6: Commit**

```powershell
git add projects/demo-web/src/lib/types.ts projects/demo-web/src/lib/api.ts projects/demo-web/src/features/overview/OverviewPage.vue projects/demo-web/src/features/quadrants/QuadrantsPage.vue projects/demo-web/tests/api.test.ts projects/demo-web/tests/flow.test.ts
git commit -m "feat: add academic risk summary views"
```

## Task 5: Upgrade Warning List and Student Drilldown

**Files:**
- Modify: `projects/demo-web/src/features/warnings/WarningsPage.vue`
- Modify: `projects/demo-web/src/features/students/StudentPage.vue`
- Modify: `projects/demo-web/src/lib/types.ts`
- Modify: `projects/demo-web/src/lib/api.ts`
- Test: `projects/demo-web/tests/warnings-query.test.ts`
- Test: `projects/demo-web/tests/flow.test.ts`

- [ ] **Step 1: Write failing tests for warning list filters and student risk drilldown**

Add tests that assert:
- warnings page can filter by four warning levels and risk change direction
- warning rows render risk score, delta, top risk factors, and protective factors
- student page renders base risk explanation, behavior adjustment explanation, and intervention plan

- [ ] **Step 2: Run the targeted tests to confirm failure**

Run:

```powershell
npm run test -- --run tests/warnings-query.test.ts tests/flow.test.ts
```

Expected: FAIL because the warning list and student page do not yet consume the richer risk contract.

- [ ] **Step 3: Update warnings page and student page**

Modify:
- `WarningsPage.vue`
- `StudentPage.vue`

to expose:
- richer warning list cards
- four-level warning filters
- risk change badges
- explanation sections
- intervention plan sections

- [ ] **Step 4: Run the targeted tests again**

Run:

```powershell
npm run test -- --run tests/warnings-query.test.ts tests/flow.test.ts
```

Expected: PASS

- [ ] **Step 5: Run full frontend verification**

Run:

```powershell
npm run test
npm run build
```

Expected: PASS

- [ ] **Step 6: Commit**

```powershell
git add projects/demo-web/src/features/warnings/WarningsPage.vue projects/demo-web/src/features/students/StudentPage.vue projects/demo-web/src/lib/types.ts projects/demo-web/src/lib/api.ts projects/demo-web/tests/warnings-query.test.ts projects/demo-web/tests/flow.test.ts
git commit -m "feat: complete academic risk warning drilldown"
```

## Task 6: End-to-End Verification

**Files:**
- Modify only if verification reveals issues

- [ ] **Step 1: Run backend verification**

Run:

```powershell
uv run --project projects/model-stubs pytest projects/model-stubs/tests -q
uv run --project projects/demo-api pytest projects/demo-api/tests -q
uv run --project projects/analytics-db pytest projects/analytics-db/tests/test_build_demo_features_from_excels.py projects/analytics-db/tests/test_cli.py -q
```

Expected: PASS

- [ ] **Step 2: Run frontend verification**

Run:

```powershell
cd projects/demo-web
npm run test
npm run build
```

Expected: PASS

- [ ] **Step 3: Run API smoke checks**

Run:

```powershell
uv run --project projects/demo-api python -c "from fastapi.testclient import TestClient; from student_behavior_demo_api.main import app; client=TestClient(app); print(client.get('/api/analytics/overview?term=2024-2').status_code); print(client.get('/api/analytics/groups?term=2024-2').status_code); print(client.get('/api/warnings?term=2024-2').status_code); print(client.get('/api/students/pjwrqxbj901/profile?term=2024-2').status_code); print(client.get('/api/students/pjwrqxbj901/report?term=2024-2').status_code)"
```

Expected: five `200` values

- [ ] **Step 4: Commit any final fixes**

```powershell
git add -A
git commit -m "fix: finalize academic risk warning integration"
```

