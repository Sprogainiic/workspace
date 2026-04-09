# Specialist Validation Gate

## Hard gate order

1. Specialist produces structured output
2. Validator checks schema, contract, and policy compatibility
3. Health Director ingests only if validation passes or warns safely
4. If fail, output is rejected or regeneration is requested

Hard rule:
- Health Director may not read raw specialist output directly.
- Only these may enter planning:
  - validated accepted payload
  - validated warn payload with explicit modification note
  - rejected payload paired with regeneration request

## Validation pipeline

### Step 1: Parse output
- confirm JSON/YAML structure is parseable
- confirm required envelope fields exist

### Step 2: Schema validation
- validate against specialist envelope schema
- validate against specialist-specific schema

Minimum set:
- `schemas/specialist-output-envelope.schema.json`
- specialist schema (e.g. `schemas/fitness-coach-output.schema.json`, `schemas/dietitian-specialist-output.schema.json`)

Dietitian intake sequence:
1. validate envelope against `schemas/specialist-output-envelope.schema.json`
2. validate payload against `schemas/dietitian-specialist-output.schema.json`
3. run `validators/dietitian-validator.md`
4. return combined result:
   - status
   - schema_errors
   - contract_violations
   - priority_conflicts
   - safe_to_ingest
   - recommended_action

### Step 3: Contract validation
- enforce specialist domain boundaries
- enforce fallback logic
- enforce output shape rules

### Step 4: Policy validation
- compare output against current user state
- compare output against system priorities
- detect overload or safety conflicts

### Step 5: Decision
- pass -> ingest
- warn -> ingest with warning log and possible modification
- fail -> reject or regenerate

## Health Director requirement

The Health Director must not directly trust specialist output.
It must always pass through validation first.

For Dietitian specifically, raw output is never used for planning.
Only validated accepted payloads or validated warn payloads with explicit modification notes may be integrated.
