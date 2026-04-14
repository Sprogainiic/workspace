# Specialist Validation Gate

## Default validation path
1. Parse output
2. Validate envelope schema
3. Validate specialist schema
4. Run deterministic specialist rules
5. Emit compact validation result

Validation result shape:
- status: pass | warn | fail
- violations: []
- safe_to_ingest: true | false
- suggested_action: accept | accept_with_modification | regenerate | reject
- notes: []

## Rules
- do not feed full workflow prose into validation by default
- do not feed full agent prompts into validation by default
- use LLM regeneration only after deterministic validation fails or warns materially
- Health Director consumes validated payloads only

## Specialist-specific fast checks
- Fitness Coach: max 3 formal sessions; minimum version required
- Dietitian: calorie range + fallback required; no aggressive deficit language
- Consistency Coach: minimum action + re-entry required; no guilt language
- Personal Chef: 2-4 options only; fallback required; no recipes
- Progress Analyst: interpretation only; no prescriptions
