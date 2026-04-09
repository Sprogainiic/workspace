# Fitness Coach Validator

## Purpose

This validator sits between Fitness Coach output and Health Director ingestion.
It is a hard gate, not an optional helper.

## Validation layers

### 1) Structural validity
Check that the output matches:
- `schemas/specialist-output-envelope.schema.json`
- `schemas/fitness-coach-output.schema.json`

Fail if:
- required fields are missing
- forbidden fields exist
- enums are invalid
- numeric ranges are broken
- `fallback.minimum_version` is missing

### 2) Contract compliance
Check that the output obeys Fitness Coach rules.

Fail if:
- formal sessions exceed 3/week
- punishment or makeup sessions are present
- direct user-facing language is present
- nutrition/calorie advice is present
- aggressive progression is present
- no minimum version exists
- no recovery downgrade exists for high fatigue cases

### 3) Policy compatibility
Check against Health Director priorities.

Warn or fail if:
- progression is recommended despite low adherence
- intensity is too high during high fatigue
- complexity is too high for low motivation
- safety or adherence is compromised

## Required validator result

Return:
- `status: pass | warn | fail`
- `schema_errors: []`
- `contract_violations: []`
- `priority_conflicts: []`
- `safe_to_ingest: true | false`
- `recommended_action: accept | accept_with_modification | regenerate | reject`

## Minimum failure rules

Fail if any of the following are true:
- `MINIMUM_VERSION` is missing
- session count > 3
- any prescribed intensity exceeds allowed threshold for current phase
- output contains direct address to user
- progression occurs despite adherence below threshold
- missed-session logic includes compensation or punishment
- output includes meal/calorie advice
- no recovery downgrade exists for high fatigue case
