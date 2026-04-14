# Deterministic Specialist Rules

Use deterministic validation before any LLM-based regeneration.

## Global rules
- schema must parse and validate
- envelope fields must exist
- specialist must remain in domain
- fallback must exist when required
- confidence must exist

## Specialist-specific fast checks
- fitness_coach: max 3 formal sessions/week; minimum_version required
- dietitian: calorie range required; no aggressive deficit wording; fallback required
- consistency_coach: minimum action required; no guilt/punishment language; re-entry required
- personal_chef: max 4 options; fallback required; no recipe-style instructions
- progress_analyst: no prescriptions; one classification only; trend claims must match evidence bundle

## Output
Emit only compact violation codes and suggested_action.
