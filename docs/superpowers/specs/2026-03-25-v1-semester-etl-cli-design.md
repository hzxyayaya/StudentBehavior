# V1 Semester Feature ETL CLI Design

Status: Draft for implementation planning

Last Updated: 2026-03-25

## Purpose

This spec defines the first implementation slice for V1: a project-bound offline ETL CLI that reads the frozen semester-feature sources and writes the first semester-level feature table as CSV.

This implementation exists to satisfy `V1-IMPL-001` from the frozen backlog and must stay aligned with:

- `C:\Users\Orion\Desktop\StudentBehavior\.worktrees\p0-foundation\docs\v1-semester-feature-schema.md`
- `C:\Users\Orion\Desktop\StudentBehavior\.worktrees\p0-foundation\docs\v1-frozen-baseline.md`

## Chosen Approach

The implementation will use a small Python package layout managed by `uv`, not a one-off script and not a configuration-heavy generic pipeline.

Why this approach:

- It is still small enough for a first implementation slice.
- It keeps the ETL rules testable.
- It creates a reusable base for later model-output stubs and backend contract stubs without prematurely building a generic framework.

## Scope

This slice only builds the first offline ETL CLI.

In scope:

- create a minimal Python project in the repository root
- provide one runnable CLI command
- read the currently frozen semester-feature sources from the project dataset directory
- output one semester feature CSV and one warning summary JSON
- implement tests for the normalization, aggregation, degradation, and CLI flow

Out of scope:

- model training
- backend APIs
- frontend pages
- label construction output
- feature columns not frozen in the semester schema document
- semester inference from unfrozen time fields

## Runtime Contract

The CLI will be project-bound for V1.

- Input directory is fixed to `C:\Users\Orion\Desktop\StudentBehavior\数据集及类型`
- Output directory is fixed to `C:\Users\Orion\Desktop\StudentBehavior\artifacts\semester_features`
- Output CSV path is fixed to `C:\Users\Orion\Desktop\StudentBehavior\artifacts\semester_features\v1_semester_features.csv`
- Output warning path is fixed to `C:\Users\Orion\Desktop\StudentBehavior\artifacts\semester_features\v1_warnings.json`
- Primary command is `uv run semester-features build`

The command should print a concise terminal summary covering:

- which frozen sources were read
- how many output rows were generated
- how many unique students were generated
- how many unique `term_key` values were generated
- how many rows were dropped due to row-level data issues
- whether `上网统计.xlsx` was degraded out of aggregation
- where the warning JSON was written

## Frozen Source Set for This Slice

The implementation only touches these three source files:

- `学生基本信息.xlsx`
- `考勤汇总.xlsx`
- `上网统计.xlsx`

The output must only contain these frozen columns:

- `student_id`
- `term_key`
- `major_name`
- `attendance_record_count`
- `internet_duration_sum`

No additional feature columns may be silently added.

## Data Facts Confirmed Against the Current Snapshot

The current dataset snapshot already shows the following facts and the implementation must respect them:

- `学生基本信息.xlsx` contains `XH`, `XSM`, and `ZYM`
- `考勤汇总.xlsx` contains `XH`, `XN`, and `XQ`
- `考勤汇总.xlsx` currently uses `XN` values like `2023-2024` and `2024-2025`
- `考勤汇总.xlsx` currently uses `XQ` values `1` and `2`
- `上网统计.xlsx` contains `XSBH`, `TJNY`, and `SWLJSC`
- `上网统计.xlsx` currently has `XN` and `XQ` fully null in the inspected snapshot
- `上网统计.xlsx` still shares the same student-id domain as `学生基本信息.xlsx`

These facts are implementation inputs, not a reason to expand the frozen schema.

## Normalization Rules

### Student Key

- normalize student identifiers to `student_id`
- accepted raw fields in this slice:
  - `XH` from `学生基本信息.xlsx`
  - `XH` from `考勤汇总.xlsx`
  - `XSBH` from `上网统计.xlsx`
- normalization trims surrounding whitespace
- empty student ids are invalid and the affected rows are dropped with warnings

### Student Dimension Duplicate Rule

`学生基本信息.xlsx` is treated as the authoritative source for `major_name`.

Rules:

- repeated rows with the same `(student_id, ZYM)` are harmless and may be deduplicated
- if one `student_id` maps to multiple distinct non-empty `ZYM` values, this is a structural dimension conflict and the run must hard-fail instead of guessing

This keeps the join deterministic and avoids silently assigning the wrong major.

### Term Key

`term_key` is frozen as `{term_year}-{term_no}`.

For this implementation slice, `term_year` is the start year parsed from `XN`, and `term_no` is the normalized semester number from `XQ`.

Examples:

- `XN=2023-2024`, `XQ=1` -> `term_key=2023-1`
- `XN=2023-2024`, `XQ=2` -> `term_key=2023-2`

Rules:

- `XQ` must normalize to `1` or `2`
- invalid or missing `XN`/`XQ` values make the row ineligible for semester aggregation
- the implementation must not invent a term mapping from other date fields unless that mapping is separately frozen later

## Output Row Construction

The base output row set comes from `考勤汇总.xlsx`.

Construction flow:

1. Read attendance rows.
2. Normalize `student_id`.
3. Normalize `term_key` from `XN` and `XQ`.
4. Drop rows with invalid `student_id` or invalid term fields and record warnings.
5. Aggregate `attendance_record_count` by `(student_id, term_key)`.
6. Left join `major_name` from `学生基本信息.xlsx` by `student_id`.
7. Fill `internet_duration_sum` according to the network-source rules below.
8. Drop final output rows whose `major_name` cannot be resolved and record warnings.

`学生基本信息.xlsx` does not create semester rows by itself. It only broadcasts student-dimension data onto the retained `(student_id, term_key)` rows.

Final CSV ordering must be deterministic:

- sort by `student_id` ascending
- then sort by `term_key` ascending

## Feature Rules

### `major_name`

- source: `学生基本信息.xlsx`
- raw field: `ZYM`
- join key: `student_id`
- required in final output

### `attendance_record_count`

- source: `考勤汇总.xlsx`
- aggregation: count rows inside each `(student_id, term_key)` bucket
- null handling: output `0` only if a retained row somehow lacks a count after aggregation; normal path should produce counts directly

### `internet_duration_sum`

- source: `上网统计.xlsx`
- intended aggregation: sum `SWLJSC` inside each `(student_id, term_key)` bucket
- null handling: `0`

However, the current snapshot has a frozen-boundary issue:

- `上网统计.xlsx` has `XN` and `XQ` fully null
- `TJNY` is populated, but `TJNY -> term_key` is not a frozen mapping rule

Therefore V1 must not infer semester membership from `TJNY` in this slice.

Current-snapshot behavior:

- the network source is treated as a degraded source for semester aggregation
- no rows from `上网统计.xlsx` are merged into semester buckets
- `internet_duration_sum` is set to `0` for all output rows
- the warning summary must explicitly record this source-level degradation

Future-snapshot behavior:

- if `上网统计.xlsx` later arrives with valid `XN` and `XQ`, the same code path may aggregate it normally
- this does not authorize using unfrozen fields for term inference

## Warning and Failure Policy

The CLI should prefer producing output, but not hide structural problems.

Hard-fail conditions:

- a required source file is missing
- a required column is missing from a required source file
- the output directory cannot be created or written

Soft-fail or warning conditions:

- empty student ids on individual rows
- invalid or missing term values on individual attendance rows
- unresolved `major_name` after join
- source-level degradation where a source cannot be safely mapped to `(student_id, term_key)` under frozen rules

Row-level invalid data should be skipped, counted, and reported.

## Warning Summary Output

The CLI must write `C:\Users\Orion\Desktop\StudentBehavior\artifacts\semester_features\v1_warnings.json`.

The warning summary should be stable enough for later tooling and include at least:

- generation timestamp
- output file path
- source file status list
- counts of dropped attendance rows by reason
- counts of dropped final rows by reason
- degraded source list

Minimum stable shape for `source file status list`:

- `source_file`
- `status` where status is one of `used`, `degraded`, or `failed`
- `rows_read`
- `notes`

Minimum stable reason keys for dropped-row counters:

- `missing_student_id`
- `invalid_term_fields`
- `missing_major_name`

For the degraded network source, include at least:

- source file name
- degradation reason
- excluded row count
- affected unique student count
- visible `TJNY` min and max values in the snapshot

## Suggested Package Shape

The implementation plan should stay close to this shape unless a smaller equivalent is clearly better:

- `pyproject.toml`
- `src/.../cli.py`
- `src/.../io.py`
- `src/.../normalize.py`
- `src/.../build_semester_features.py`
- `src/.../reporting.py`
- `tests/...`

The exact package name is an implementation detail, but the public command must remain `uv run semester-features build`.

## Testing Strategy

Implementation must follow TDD.

Minimum test layers:

### Unit tests

- `XN + XQ -> term_key`
- invalid `XQ` rejection
- student-id normalization
- warning accumulator behavior

### Component tests

- attendance aggregation into `attendance_record_count`
- student-dimension join into `major_name`
- network-source degradation when `XN` and `XQ` are unavailable

### CLI integration test

- create minimal Excel fixtures in a temporary directory
- keep the public CLI project-bound in production
- allow tests to inject temporary input and output roots through an internal seam, such as an internal configuration object or builder function, rather than adding public path flags to the CLI
- run the CLI or CLI-adjacent entry path against the fixture directory through that internal seam
- assert both CSV and JSON outputs exist
- assert output columns and warning contents match the frozen rules

## Acceptance Criteria

The implementation plan should be judged against these outcomes:

- `uv` can install and run the project locally
- `uv run semester-features build` works from the repository root
- the output CSV only contains the five frozen columns
- `term_key` values only use the `YYYY-1` or `YYYY-2` shape
- the current real snapshot produces a CSV and a warning JSON
- the current real snapshot produces `internet_duration_sum = 0` for every output row because the network source is degraded out
- the warning JSON explicitly explains why the network source was excluded
- tests run locally and pass

## Planning Notes

The implementation plan should stay narrow:

- do not pull in additional data sources
- do not add generic pipeline abstractions without a concrete need
- do not solve model or API work in the ETL task
- do not silently infer semester membership from `TJNY`

This spec is ready to drive a single-task implementation plan for `V1-IMPL-001`.
