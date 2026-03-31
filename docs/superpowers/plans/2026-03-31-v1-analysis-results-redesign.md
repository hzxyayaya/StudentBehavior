# V1 Analysis Results Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the current quadrant-heavy V1 business framing with a unified four-task, ten-result analysis framing across docs, API contracts, result-layer outputs, and the demo web UI.

**Architecture:** Keep the existing multi-project data pipeline intact and change the system from the top down. First rewrite the frozen docs and API contract, then migrate result-layer field semantics from `quadrant_label` to a general behavior-pattern grouping, then update API endpoints and the demo web UI to consume the new business language.

**Tech Stack:** Markdown docs, Python 3.12, FastAPI, pandas, Vue 3, TypeScript, Vite, pytest, vitest

---

### Task 1: Freeze New Business Baseline

**Files:**
- Modify: `docs/v1-frozen-baseline.md`
- Modify: `docs/handoff.md`
- Modify: `docs/v1-demo-runbook.md`
- Reference: `docs/superpowers/specs/2026-03-31-v1-analysis-results-redesign.md`

- [ ] **Step 1: Rewrite frozen goals and analysis scope**

Replace the old “8 个分析成果 + 四象限” wording with:

- 4 类分析任务
- 10 个系统输出
- 行为模式识别 / 群体分层

- [ ] **Step 2: Remove quadrant-specific business semantics from baseline docs**

Delete or rewrite:

- “投入度 × 稳定性四象限”
- `quadrant_label` as business-first output
- “群体页 = 四象限页”

- [ ] **Step 3: Update handoff and runbook narrative**

Ensure the docs consistently say:

- current system centers on academic-risk analysis
- grouping is expressed as behavior patterns / group segmentation
- quadrant language is historical, not frozen

- [ ] **Step 4: Run text verification**

Run: `rg -n "四象限|quadrant_label|quadrants" docs/v1-frozen-baseline.md docs/handoff.md docs/v1-demo-runbook.md`

Expected: only historical compatibility mentions remain, no frozen-business wording

### Task 2: Redesign API Contract

**Files:**
- Modify: `docs/v1-api-contract.md`
- Reference: `projects/demo-api/src/student_behavior_demo_api/main.py`
- Reference: `projects/demo-api/src/student_behavior_demo_api/services.py`

- [ ] **Step 1: Rewrite shared enums and top-level endpoint list**

Remove the contract-level requirement that `quadrant_label` is a shared enum.

Introduce one unified grouping field:

- `group_segment` or `behavior_pattern`

Recommendation: use `group_segment` in API payloads.

- [ ] **Step 2: Replace `/api/analytics/quadrants` with `/api/analytics/groups` in the contract**

Document the new endpoint shape:

```json
{
  "groups": [
    {
      "group_segment": "作息失衡风险组",
      "student_count": 39,
      "avg_risk_probability": 0.81,
      "top_factors": []
    }
  ]
}
```

- [ ] **Step 3: Update warning/profile contract examples**

Replace example fields:

- `quadrant_label` -> `group_segment`

- [ ] **Step 4: Add contract notes for future endpoints**

Document planned analytics endpoints:

- `/api/analytics/groups`
- `/api/analytics/trends`
- `/api/analytics/majors`
- `/api/analytics/directions`

- [ ] **Step 5: Run text verification**

Run: `rg -n "quadrant_label|/api/analytics/quadrants|quadrant_distribution" docs/v1-api-contract.md`

Expected: only explicitly marked historical-compatibility notes remain

### Task 3: Migrate Result-Layer Semantics

**Files:**
- Modify: `projects/model-stubs/src/student_behavior_model_stubs/scoring.py`
- Modify: `projects/model-stubs/src/student_behavior_model_stubs/templates.py`
- Modify: `projects/model-stubs/src/student_behavior_model_stubs/build_outputs.py`
- Modify: `projects/model-stubs/tests/test_scoring.py`
- Modify: `projects/model-stubs/tests/test_templates.py`
- Modify: `projects/model-stubs/tests/test_build_outputs.py`

- [ ] **Step 1: Write failing tests for new grouping field**

Add tests that expect:

- `group_segment` field exists
- output no longer requires `quadrant_label`

- [ ] **Step 2: Run focused tests and confirm failure**

Run: `uv run --project projects/model-stubs pytest projects/model-stubs/tests/test_scoring.py projects/model-stubs/tests/test_templates.py projects/model-stubs/tests/test_build_outputs.py -q`

Expected: FAIL due to old quadrant-based assumptions

- [ ] **Step 3: Implement minimal grouping migration**

Refactor result building so that:

- group label generation returns `group_segment`
- report templates say “行为模式/群体标签”
- outputs remain compatible with current risk fields

- [ ] **Step 4: Run focused tests and make them pass**

Run: `uv run --project projects/model-stubs pytest projects/model-stubs/tests/test_scoring.py projects/model-stubs/tests/test_templates.py projects/model-stubs/tests/test_build_outputs.py -q`

Expected: PASS

- [ ] **Step 5: Run full model-stubs test suite**

Run: `uv run --project projects/model-stubs pytest projects/model-stubs/tests -q`

Expected: PASS

### Task 4: Migrate Demo API from Quadrants to Groups

**Files:**
- Modify: `projects/demo-api/src/student_behavior_demo_api/loaders.py`
- Modify: `projects/demo-api/src/student_behavior_demo_api/services.py`
- Modify: `projects/demo-api/src/student_behavior_demo_api/main.py`
- Modify: `projects/demo-api/tests/test_api.py`
- Modify: `projects/demo-api/tests/test_services.py`

- [ ] **Step 1: Write failing tests for `/api/analytics/groups`**

Add tests that expect:

- `/api/analytics/groups` returns `groups`
- payload items contain `group_segment`
- warning filtering accepts `group_segment`

- [ ] **Step 2: Run focused API tests and confirm failure**

Run: `uv run --project projects/demo-api pytest projects/demo-api/tests/test_api.py projects/demo-api/tests/test_services.py -q`

Expected: FAIL because current implementation still uses quadrants

- [ ] **Step 3: Implement endpoint and field migration**

Update API code so that:

- `/api/analytics/groups` is the primary endpoint
- `quadrant_label` filters are replaced by `group_segment`
- loaders and services validate the new field shape

- [ ] **Step 4: Decide compatibility strategy**

Choose one:

- keep `/api/analytics/quadrants` as deprecated alias for one iteration, or
- remove it immediately and update all consumers

Recommendation: keep one-cycle compatibility alias if it does not complicate logic.

- [ ] **Step 5: Run focused API tests**

Run: `uv run --project projects/demo-api pytest projects/demo-api/tests/test_api.py projects/demo-api/tests/test_services.py -q`

Expected: PASS

- [ ] **Step 6: Run full demo-api test suite**

Run: `uv run --project projects/demo-api pytest projects/demo-api/tests -q`

Expected: PASS

### Task 5: Rewrite Demo Web Grouping and Filters

**Files:**
- Modify: `.worktrees/v1-demo-web/projects/demo-web/src/lib/types.ts`
- Modify: `.worktrees/v1-demo-web/projects/demo-web/src/lib/api.ts`
- Modify: `.worktrees/v1-demo-web/projects/demo-web/src/features/overview/OverviewPage.vue`
- Modify: `.worktrees/v1-demo-web/projects/demo-web/src/features/quadrants/QuadrantsPage.vue`
- Modify: `.worktrees/v1-demo-web/projects/demo-web/src/features/warnings/WarningsPage.vue`
- Modify: `.worktrees/v1-demo-web/projects/demo-web/src/features/warnings/query.ts`
- Modify: `.worktrees/v1-demo-web/projects/demo-web/src/features/students/StudentPage.vue`
- Modify: `.worktrees/v1-demo-web/projects/demo-web/src/components/layout/DemoStatusBar.vue`
- Modify: `.worktrees/v1-demo-web/projects/demo-web/src/app/router.ts`

- [ ] **Step 1: Write failing UI/API normalization tests**

Add or update tests to expect:

- `group_segment` instead of `quadrant_label`
- group page wording no longer references quadrants
- warnings query state uses `group_segment`

- [ ] **Step 2: Run relevant frontend tests to confirm failure**

Run: `npm run test`

Expected: FAIL due to old quadrant-based types and UI expectations

- [ ] **Step 3: Rename the grouping page and payload model**

Refactor:

- `QuadrantsPage` -> `GroupsPage` or keep filename temporarily with new display wording
- API normalizers map `group_segment`
- overview uses “行为模式分布” or “重点群体分布”

- [ ] **Step 4: Replace filter/query usage**

Update warnings flow so that:

- query param uses `group_segment`
- deep links and back-navigation preserve the new field

- [ ] **Step 5: Rewrite student-page wording**

Remove:

- “属于哪个四象限”

Use:

- “所属行为模式”
- “群体标签”

- [ ] **Step 6: Run frontend tests**

Run: `npm run test`

Expected: PASS

- [ ] **Step 7: Run frontend build**

Run: `npm run build`

Expected: PASS

### Task 6: End-to-End Verification

**Files:**
- Verify only

- [ ] **Step 1: Rebuild or reuse offline artifacts**

Run one of:

- `uv run --project projects/model-stubs student-behavior-stubs build`
- or reuse existing artifacts if schema-compatible after migration

- [ ] **Step 2: Start demo API locally**

Run: `uv run --project projects/demo-api uvicorn student_behavior_demo_api.main:app --host 127.0.0.1 --port 8000`

Expected: server starts successfully

- [ ] **Step 3: Start demo web locally**

Run: `npm run dev -- --host 127.0.0.1 --port 5173`

Expected: Vite dev server starts successfully

- [ ] **Step 4: Verify key pages and requests**

Check:

- overview loads
- groups page loads
- warnings filtering works
- student profile/report loads

- [ ] **Step 5: Run targeted smoke requests**

Examples:

- `GET /api/analytics/overview?term=2024-2`
- `GET /api/analytics/groups?term=2024-2`
- `GET /api/warnings?term=2024-2&page=1&page_size=20`
- `GET /api/students/pjwrqxbj901/profile?term=2024-2`

Expected: all return 200 envelope responses

### Task 7: Final Documentation and Handoff

**Files:**
- Modify: `docs/handoff.md`
- Modify: `docs/v1-demo-runbook.md`
- Modify: `docs/session-progress.md` if needed

- [ ] **Step 1: Record what changed**

Document:

- new four-task framing
- new ten-result framing
- replacement of quadrants with grouping semantics

- [ ] **Step 2: Record residual risks**

Document any remaining gaps:

- stub risk outputs
- model metrics not yet formalized
- historical compatibility endpoints if retained

- [ ] **Step 3: Run final repository checks**

Run:

- `uv run --project projects/model-stubs pytest projects/model-stubs/tests -q`
- `uv run --project projects/demo-api pytest projects/demo-api/tests -q`
- `npm run test`
- `npm run build`

Expected: all pass
