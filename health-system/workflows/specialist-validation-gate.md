# Specialist Validation Gate

## Hard gate order

1. Specialist produces structured output
2. Validator checks schema, contract, and policy compatibility
3. Health Director ingests only if validation passes or warns safely
4. If fail, output is rejected or regeneration is requested

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
