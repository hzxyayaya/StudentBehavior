# Real Model Training Chain Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a real, reproducible academic-risk training and evaluation chain that replaces the current static model-summary values with trained metrics and artifacts.

**Architecture:** Keep the current pipeline shape. `analytics-db` becomes responsible for generating explicit supervised labels in the semester feature artifact. `model-stubs` grows a real training/evaluation lane that writes model artifacts and metric summaries, while retaining the current rule-based path as fallback. `demo-api` and `demo-web` then read and display the real model summary instead of the static stub constants.

**Tech Stack:** Python 3.12, uv, pandas, pytest, FastAPI, existing `projects/analytics-db`, `projects/model-stubs`, `projects/demo-api`, `projects/demo-web`

---

## File Structure

### Existing files to modify

- Modify: `projects/analytics-db/src/student_behavior_analytics_db/build_student_term_features.py`
- Modify: `projects/analytics-db/src/student_behavior_analytics_db/build_demo_features_from_excels.py`
- Modify: `projects/analytics-db/tests/test_build_student_term_features.py`
- Modify: `projects/analytics-db/tests/test_build_demo_features_from_excels.py`
- Modify: `projects/model-stubs/src/student_behavior_model_stubs/cli.py`
- Modify: `projects/model-stubs/src/student_behavior_model_stubs/build_outputs.py`
- Modify: `projects/model-stubs/tests/test_build_outputs.py`
- Modify: `projects/demo-api/src/student_behavior_demo_api/services.py`
- Modify: `projects/demo-api/tests/test_services.py`
- Modify: `projects/demo-api/tests/test_api.py`
- Modify: `projects/demo-web/src/features/overview/OverviewPage.vue`
- Modify: `projects/demo-web/tests/flow.test.ts`
- Modify: `projects/demo-web/tests/api.test.ts`

### New files to create

- Create: `projects/model-stubs/src/student_behavior_model_stubs/train_risk_model.py`
- Create: `projects/model-stubs/src/student_behavior_model_stubs/evaluate_risk_model.py`
- Create: `projects/model-stubs/src/student_behavior_model_stubs/model_registry.py`
- Create: `projects/model-stubs/tests/test_train_risk_model.py`
- Create: `projects/model-stubs/tests/test_evaluate_risk_model.py`
- Create: `projects/model-stubs/tests/test_model_registry.py`
- Create: `docs/risk-label-definition-plan.md` (already present; update only if needed)

### Responsibilities

- `build_student_term_features.py`
  - Add explicit supervised risk label fields to the semester feature artifact.
- `build_demo_features_from_excels.py`
  - Ensure the label fields survive the Excel-to-feature pipeline.
- `train_risk_model.py`
  - Train the real risk model from semester features.
- `evaluate_risk_model.py`
  - Compute AUC/accuracy/precision/recall/F1 and serialize metrics.
- `model_registry.py`
  - Centralize model artifact paths and metadata reading.
- `build_outputs.py`
  - Read trained metrics when available and only fallback to stub values when missing.
- `services.py`
  - Return trained model summary fields in API responses.
- `OverviewPage.vue`
  - Render additional real model summary fields without changing core layout.

---

### Task 1: Add Explicit Risk Labels to Semester Features

**Files:**
- Modify: `projects/analytics-db/src/student_behavior_analytics_db/build_student_term_features.py`
- Modify: `projects/analytics-db/src/student_behavior_analytics_db/build_demo_features_from_excels.py`
- Test: `projects/analytics-db/tests/test_build_student_term_features.py`
- Test: `projects/analytics-db/tests/test_build_demo_features_from_excels.py`

- [ ] **Step 1: Write failing analytics-db tests for label fields**

Add tests asserting that the semester feature artifact includes:

- `risk_label_binary`
- `risk_label_level`
- `label_source`
- `label_rule_version`

Also assert at least one realistic row is labeled from grade/evaluation inputs.

- [ ] **Step 2: Run the focused tests to confirm failure**

Run:

```powershell
cd C:\Users\Orion\Desktop\program\StudentBehavior\.worktrees\academic-risk-warning\projects\analytics-db
uv run pytest tests/test_build_student_term_features.py tests/test_build_demo_features_from_excels.py -q
```

Expected:

- FAIL because the label fields do not exist yet

- [ ] **Step 3: Implement the minimal label-generation logic**

Add a deterministic first-pass rule in `build_student_term_features.py` using existing columns such as:

- `avg_gpa`
- `failed_course_count`
- `risk_label` (if already derived from evaluation labels)

Suggested first-pass behavior:

- `risk_label_binary = 1` when GPA/挂科/综合测评 signals cross risk thresholds
- `risk_label_level` maps into `高风险 / 较高风险 / 一般风险 / 低风险`
- `label_source = "academic_rule_v1"`
- `label_rule_version = "2026-04-risk-v1"`

- [ ] **Step 4: Run the focused tests to verify they pass**

Run:

```powershell
cd C:\Users\Orion\Desktop\program\StudentBehavior\.worktrees\academic-risk-warning\projects\analytics-db
uv run pytest tests/test_build_student_term_features.py tests/test_build_demo_features_from_excels.py -q
```

Expected:

- PASS

- [ ] **Step 5: Commit**

```powershell
git add projects/analytics-db/src/student_behavior_analytics_db/build_student_term_features.py projects/analytics-db/src/student_behavior_analytics_db/build_demo_features_from_excels.py projects/analytics-db/tests/test_build_student_term_features.py projects/analytics-db/tests/test_build_demo_features_from_excels.py
git commit -m "feat: add risk labels to semester features"
```

---

### Task 2: Add Trained Model Artifact Registry

**Files:**
- Create: `projects/model-stubs/src/student_behavior_model_stubs/model_registry.py`
- Test: `projects/model-stubs/tests/test_model_registry.py`

- [ ] **Step 1: Write the failing registry test**

Test for:

- default training artifact directory resolution
- `risk_metrics.json` lookup
- optional fallback behavior when metrics are missing

- [ ] **Step 2: Run the focused test to confirm failure**

Run:

```powershell
cd C:\Users\Orion\Desktop\program\StudentBehavior\.worktrees\academic-risk-warning\projects\model-stubs
uv run pytest tests/test_model_registry.py -q
```

Expected:

- FAIL because registry module does not exist

- [ ] **Step 3: Implement minimal registry logic**

Create helpers for:

- model-training artifact root
- metrics path
- model path
- feature importance path
- loading metrics JSON safely

- [ ] **Step 4: Run the focused test to verify it passes**

Run:

```powershell
cd C:\Users\Orion\Desktop\program\StudentBehavior\.worktrees\academic-risk-warning\projects\model-stubs
uv run pytest tests/test_model_registry.py -q
```

Expected:

- PASS

- [ ] **Step 5: Commit**

```powershell
git add projects/model-stubs/src/student_behavior_model_stubs/model_registry.py projects/model-stubs/tests/test_model_registry.py
git commit -m "feat: add model training artifact registry"
```

---

### Task 3: Add Trainable Risk Model Command

**Files:**
- Create: `projects/model-stubs/src/student_behavior_model_stubs/train_risk_model.py`
- Modify: `projects/model-stubs/src/student_behavior_model_stubs/cli.py`
- Test: `projects/model-stubs/tests/test_train_risk_model.py`

- [ ] **Step 1: Write the failing training tests**

Cover:

- reading feature CSV with label columns
- splitting train/valid/test
- training a simple risk model
- writing model artifact + training config

- [ ] **Step 2: Run the focused test to confirm failure**

Run:

```powershell
cd C:\Users\Orion\Desktop\program\StudentBehavior\.worktrees\academic-risk-warning\projects\model-stubs
uv run pytest tests/test_train_risk_model.py -q
```

Expected:

- FAIL because training module/CLI command is missing

- [ ] **Step 3: Implement minimal train command**

Add a CLI subcommand such as:

- `train-risk-model <features_csv> --output-dir <dir>`

Training should:

- load labeled semester features
- choose stable numeric features
- split by `student_id` when possible
- train a first-pass model
- save:
  - model file
  - feature columns
  - training config

- [ ] **Step 4: Run the focused test to verify it passes**

Run:

```powershell
cd C:\Users\Orion\Desktop\program\StudentBehavior\.worktrees\academic-risk-warning\projects\model-stubs
uv run pytest tests/test_train_risk_model.py -q
```

Expected:

- PASS

- [ ] **Step 5: Commit**

```powershell
git add projects/model-stubs/src/student_behavior_model_stubs/train_risk_model.py projects/model-stubs/src/student_behavior_model_stubs/cli.py projects/model-stubs/tests/test_train_risk_model.py
git commit -m "feat: add train risk model command"
```

---

### Task 4: Add Evaluation Command and Real Metrics Output

**Files:**
- Create: `projects/model-stubs/src/student_behavior_model_stubs/evaluate_risk_model.py`
- Modify: `projects/model-stubs/src/student_behavior_model_stubs/cli.py`
- Test: `projects/model-stubs/tests/test_evaluate_risk_model.py`

- [ ] **Step 1: Write the failing evaluation tests**

Cover:

- loading trained model + held-out data
- computing metrics
- writing `risk_metrics.json`

- [ ] **Step 2: Run the focused test to confirm failure**

Run:

```powershell
cd C:\Users\Orion\Desktop\program\StudentBehavior\.worktrees\academic-risk-warning\projects\model-stubs
uv run pytest tests/test_evaluate_risk_model.py -q
```

Expected:

- FAIL because evaluation module/CLI command is missing

- [ ] **Step 3: Implement the minimal evaluation command**

Add a CLI subcommand such as:

- `evaluate-risk-model <features_csv> --model-dir <dir>`

Output:

- `risk_metrics.json`
- `feature_importance.csv` when supported

Metrics must include:

- `auc`
- `accuracy`
- `precision`
- `recall`
- `f1`
- sample counts
- `trained_at`

- [ ] **Step 4: Run the focused test to verify it passes**

Run:

```powershell
cd C:\Users\Orion\Desktop\program\StudentBehavior\.worktrees\academic-risk-warning\projects\model-stubs
uv run pytest tests/test_evaluate_risk_model.py -q
```

Expected:

- PASS

- [ ] **Step 5: Commit**

```powershell
git add projects/model-stubs/src/student_behavior_model_stubs/evaluate_risk_model.py projects/model-stubs/src/student_behavior_model_stubs/cli.py projects/model-stubs/tests/test_evaluate_risk_model.py
git commit -m "feat: add risk model evaluation command"
```

---

### Task 5: Replace Static Model Summary with Trained Metrics

**Files:**
- Modify: `projects/model-stubs/src/student_behavior_model_stubs/build_outputs.py`
- Modify: `projects/model-stubs/tests/test_build_outputs.py`

- [ ] **Step 1: Write the failing model-summary test**

Add a test that:

- places a real `risk_metrics.json` in the training artifact location
- verifies `build_model_summary()` reads trained metrics instead of static constants
- verifies fallback still works when metrics are absent

- [ ] **Step 2: Run the focused test to confirm failure**

Run:

```powershell
cd C:\Users\Orion\Desktop\program\StudentBehavior\.worktrees\academic-risk-warning\projects\model-stubs
uv run pytest tests/test_build_outputs.py -q
```

Expected:

- FAIL on model summary expectations

- [ ] **Step 3: Implement summary fallback layering**

Change `build_outputs.py` so:

- trained metrics are primary
- stub metrics are fallback
- add `source = trained|stub`

- [ ] **Step 4: Run the focused test to verify it passes**

Run:

```powershell
cd C:\Users\Orion\Desktop\program\StudentBehavior\.worktrees\academic-risk-warning\projects\model-stubs
uv run pytest tests/test_build_outputs.py -q
```

Expected:

- PASS

- [ ] **Step 5: Commit**

```powershell
git add projects/model-stubs/src/student_behavior_model_stubs/build_outputs.py projects/model-stubs/tests/test_build_outputs.py
git commit -m "feat: read trained metrics in model summary"
```

---

### Task 6: Expose Trained Metrics Through demo-api

**Files:**
- Modify: `projects/demo-api/src/student_behavior_demo_api/services.py`
- Modify: `projects/demo-api/tests/test_services.py`
- Modify: `projects/demo-api/tests/test_api.py`

- [ ] **Step 1: Write failing API/service tests**

Add tests verifying:

- `/api/models/summary`
- `/api/results/model-summary`

return trained fields such as:

- `auc`
- `accuracy`
- `recall`
- `f1`
- `train_sample_count`
- `test_sample_count`
- `source`

- [ ] **Step 2: Run the focused tests to confirm failure**

Run:

```powershell
cd C:\Users\Orion\Desktop\program\StudentBehavior\.worktrees\academic-risk-warning\projects\demo-api
uv run --all-groups --with pytest --with pandas pytest tests/test_services.py tests/test_api.py -q
```

Expected:

- FAIL because the current service only returns the older summary shape

- [ ] **Step 3: Implement minimal API summary passthrough**

Update `services.py` and any related loaders so the new trained metric fields are surfaced to API consumers while preserving backward compatibility.

- [ ] **Step 4: Run the focused tests to verify they pass**

Run:

```powershell
cd C:\Users\Orion\Desktop\program\StudentBehavior\.worktrees\academic-risk-warning\projects\demo-api
uv run --all-groups --with pytest --with pandas pytest tests/test_services.py tests/test_api.py -q
```

Expected:

- PASS

- [ ] **Step 5: Commit**

```powershell
git add projects/demo-api/src/student_behavior_demo_api/services.py projects/demo-api/tests/test_services.py projects/demo-api/tests/test_api.py
git commit -m "feat: expose trained model metrics via api"
```

---

### Task 7: Update Frontend Model Summary Rendering

**Files:**
- Modify: `projects/demo-web/src/features/overview/OverviewPage.vue`
- Modify: `projects/demo-web/tests/flow.test.ts`
- Modify: `projects/demo-web/tests/api.test.ts`

- [ ] **Step 1: Write failing frontend tests**

Add coverage that the overview/model-summary UI can display:

- real AUC
- extra metrics such as accuracy/recall/f1 when present
- model source (`trained` or `stub`)

- [ ] **Step 2: Run the focused tests to confirm failure**

Run:

```powershell
cd C:\Users\Orion\Desktop\program\StudentBehavior\.worktrees\academic-risk-warning\projects\demo-web
npm run test -- tests/api.test.ts tests/flow.test.ts
```

Expected:

- FAIL because the current page/test baseline does not cover the new summary fields

- [ ] **Step 3: Implement minimal UI support**

Update the model summary card so it can show additional trained fields without redesigning the page.

- [ ] **Step 4: Run the focused tests to verify they pass**

Run:

```powershell
cd C:\Users\Orion\Desktop\program\StudentBehavior\.worktrees\academic-risk-warning\projects\demo-web
npm run test -- tests/api.test.ts tests/flow.test.ts
```

Expected:

- PASS

- [ ] **Step 5: Run build to verify end-to-end frontend health**

Run:

```powershell
cd C:\Users\Orion\Desktop\program\StudentBehavior\.worktrees\academic-risk-warning\projects\demo-web
npm run build
```

Expected:

- PASS

- [ ] **Step 6: Commit**

```powershell
git add projects/demo-web/src/features/overview/OverviewPage.vue projects/demo-web/tests/flow.test.ts projects/demo-web/tests/api.test.ts
git commit -m "feat: render trained model summary in frontend"
```

---

### Task 8: Run Full Regression and Refresh Docs

**Files:**
- Modify: `docs/real-model-training-plan.md`
- Modify: `docs/risk-label-definition-plan.md`
- Modify: `docs/implementation-priority-roadmap.md`

- [ ] **Step 1: Run backend and training suites**

Run:

```powershell
cd C:\Users\Orion\Desktop\program\StudentBehavior\.worktrees\academic-risk-warning\projects\analytics-db
uv run pytest -q

cd C:\Users\Orion\Desktop\program\StudentBehavior\.worktrees\academic-risk-warning\projects\model-stubs
uv run pytest -q

cd C:\Users\Orion\Desktop\program\StudentBehavior\.worktrees\academic-risk-warning\projects\demo-api
uv run --all-groups --with pytest --with pandas pytest -q

cd C:\Users\Orion\Desktop\program\StudentBehavior\.worktrees\academic-risk-warning\projects\demo-web
npm run test
npm run build
```

Expected:

- All relevant suites pass

- [ ] **Step 2: Refresh docs to reflect the real trained path**

Update the docs so they clearly distinguish:

- trained path
- fallback stub path
- label version
- metric source

- [ ] **Step 3: Commit**

```powershell
git add docs/real-model-training-plan.md docs/risk-label-definition-plan.md docs/implementation-priority-roadmap.md
git commit -m "docs: finalize real model training chain docs"
```

---

## Verification Checklist

- [ ] Semester features include explicit risk labels
- [ ] A real train command exists
- [ ] A real evaluate command exists
- [ ] `risk_metrics.json` is generated
- [ ] `build_model_summary` prefers trained metrics
- [ ] API exposes trained summary fields
- [ ] Frontend model info card displays trained summary fields
- [ ] Core tests pass
- [ ] Build passes

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-04-08-real-model-training-chain.md`. Two execution options:

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

Which approach?
