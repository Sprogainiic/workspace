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

CONSISTENCY_COACH_VALIDATION_GATE:

All Consistency Coach outputs MUST pass through the validation gate before the Health Director may read, classify, or use them.

Direct intake of raw Consistency Coach output is forbidden.

Purpose:
This gate ensures the Health Director only receives Consistency Coach outputs that are:
- structurally valid
- contract-compliant
- behaviorally actionable
- safe to use in plan adjudication

This prevents vague behavioral advice, motivational fluff, guilt language, and unauthorized plan rewriting from entering the system.

Required intake sequence:

Step 1 — Validate Envelope
- validate against `schemas/specialist-output-envelope.schema.json`
- confirm valid specialist metadata and structured payload
- if envelope validation fails: stop intake, mark invalid, do not continue

Step 2 — Validate Consistency Coach Specialist Schema
- validate payload against `schemas/consistency-coach-output.schema.json`
- validate specialist output against `schemas/consistency-coach-specialist-output.schema.json`
- confirm required sections are present and typed:
  - BEHAVIOR_STATE
  - PRIMARY_INTERVENTION
  - MINIMUM_ACTION
  - FRICTION_REDUCTION
  - REENTRY_STRATEGY
  - ESCALATION_FLAGS
- if schema validation fails: stop intake, return schema failure, do not continue

Step 3 — Run Consistency Coach Validator
- run `validators/consistency-coach-validator.md`
- assess:
  - contract compliance
  - priority conflicts
  - behavioral usefulness
  - intervention specificity
  - prohibited language or role drift
- explicitly detect:
  - guilt/shame/pressure language
  - motivational fluff without action
  - vague or generic interventions
  - missing or overly complex minimum action
  - missing or weak re-entry logic
  - attempts to alter training or nutrition directly
  - attempts to override Health Director authority
  - behavior recommendations that ignore fatigue, overload, or adherence state

Combined validation result (required output):
- status: pass | warn | fail
- schema_errors: []
- contract_violations: []
- priority_conflicts: []
- safe_to_ingest: true | false
- recommended_action:
  - accept
  - accept_with_modification
  - regenerate
  - reject

PROGRESS_ANALYST_VALIDATION_GATE:

All Progress Analyst outputs MUST pass through the validation gate before the Health Director may read, interpret, or use them.

Direct intake of raw Progress Analyst output is forbidden.

Purpose:
This gate ensures the Health Director only receives Progress Analyst outputs that are:
- structurally valid
- contract-compliant
- trend-based rather than snapshot-based
- behavior-aware
- safe to use in system interpretation

This prevents noisy summaries, false trend claims, plan-prescribing drift, and overconfident analysis from entering the system.

Required intake sequence:

Step 1 — Validate Envelope
- validate against `schemas/specialist-output-envelope.schema.json`
- confirm valid specialist metadata and properly structured payload
- if envelope validation fails: stop intake, mark invalid, do not continue

Step 2 — Validate Progress Analyst Specialist Schema
- validate payload against `schemas/progress-analyst-output.schema.json`
- validate specialist output against `schemas/progress-analyst-specialist-output.schema.json`
- confirm required sections are present and typed:
  - TREND_SUMMARY
  - KEY_PATTERNS
  - RISK_SIGNALS
  - PROGRESS_CLASSIFICATION
  - SYSTEM_IMPLICATIONS
- if schema validation fails: stop intake, return schema failure, do not continue

Step 3 — Run Progress Analyst Validator
- run `validators/progress-analyst-validator.md`
- assess:
  - contract compliance
  - classification quality
  - signal-vs-noise discipline
  - behavior-first interpretation
  - prohibited prescription drift
  - unsupported certainty
- explicitly detect:
  - trend claims based on inadequate history
  - plateau claims without sufficient adherence and duration
  - progress claims unsupported by behavior stability
  - regression claims based only on short-term fluctuation
  - direct training or nutrition prescriptions
  - user-facing language
  - overconfident or overly precise interpretation
  - failure to incorporate adherence instability into analysis
  - emotional or motivational language

Combined validation result (required output):
- status: pass | warn | fail
- schema_errors: []
- contract_violations: []
- priority_conflicts: []
- safe_to_ingest: true | false
- recommended_action:
  - accept
  - accept_with_modification
  - regenerate
  - reject
- validated_payload: {}
- validation_notes: []

Hard intake rule:
The Health Director may consume only one of the following:
- a validated pass payload
- a validated warn payload with explicit modification note
- a fail result that triggers regeneration or rejection

The Health Director must not:
- read raw Progress Analyst output
- infer meaning from failed analyst output
- merge partially invalid analytical claims
- silently downgrade failure to warning
- treat weak trend claims as decision-grade truth

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

PERSONAL_CHEF_VALIDATION_GATE:

All Personal Chef outputs MUST pass through the validation gate before the Health Director may read, classify, or use them.

Direct intake of raw Personal Chef output is forbidden.

Purpose:
This gate ensures the Health Director only receives Personal Chef outputs that are:
- structurally valid
- contract-compliant
- low-friction and execution-oriented
- safe to use in meal execution context

This prevents recipe-style output, excessive choice, ignored friction signals, and unbounded complexity from entering the system.

Required intake sequence:

Step 1 — Validate Envelope
- validate against `schemas/specialist-output-envelope.schema.json`
- confirm valid specialist metadata and properly structured payload
- if envelope validation fails: stop intake, mark invalid, do not continue

Step 2 — Validate Personal Chef Specialist Schema
- validate payload against `schemas/personal-chef-output.schema.json`
- validate specialist output against `schemas/personal-chef-specialist-output.schema.json`
- confirm required sections are present and typed:
  - SIMPLICITY_MODE
  - MEAL_OPTIONS
  - FALLBACK_MEAL
  - CONSTRAINT_ALIGNMENT
- if schema validation fails: stop intake, return schema failure, do not continue

Step 3 — Run Personal Chef Validator
- run `validators/personal-chef-validator.md`
- assess:
  - contract compliance
  - option count discipline
  - fallback quality
  - friction responsiveness
  - prohibited recipe/planning drift
  - mode alignment (stability vs normal)
- explicitly detect:
  - more than 4 options
  - missing fallback
  - recipe-style instructions
  - ignored Stability Mode
  - ignored friction signals
  - chef inventing nutrition rules
  - descriptive or persuasive language
  - multi-step prep burden

Combined validation result (required output):
- status: pass | warn | fail
- schema_errors: []
- contract_violations: []
- priority_conflicts: []
- safe_to_ingest: true | false
- recommended_action:
  - accept
  - accept_with_modification
  - regenerate
  - reject
- validated_payload: {}
- validation_notes: []

Hard intake rule:
The Health Director may consume only one of the following:
- a validated pass payload
- a validated warn payload with explicit modification note
- a fail result that triggers regeneration or rejection

The Health Director must not:
- read raw Personal Chef output
- infer meaning from failed chef output
- merge partially invalid meal suggestions
- silently downgrade failure to warning
- treat recipe-like output as execution-ready

## Health Director requirement

The Health Director must not directly trust specialist output.
It must always pass through validation first.

For Dietitian specifically, raw output is never used for planning.
Only validated accepted payloads or validated warn payloads with explicit modification notes may be integrated.
