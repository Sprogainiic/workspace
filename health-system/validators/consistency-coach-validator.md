# Consistency Coach Validator

## Status Levels

- PASS
- WARN
- FAIL

## FAIL Conditions

Reject output if:
- missing any required section
- no MINIMUM_ACTION present
- MINIMUM_ACTION is too complex (>15 min implied or multi-step)
- includes motivational or emotional language
- includes guilt, shame, or pressure
- increases difficulty after low adherence
- ignores fatigue when high
- no re-entry strategy provided
- tries to modify training or nutrition directly
- vague or generic advice (e.g. "stay consistent")

## WARN Conditions

- friction reduction unclear
- intervention too generic
- escalation flags missing when risk present
- minimum action slightly too complex
- re-entry logic weak or vague

## Contract Violations

- acting like Health Director
- prescribing workouts or meals
- overriding system decisions

## Output

status: pass | warn | fail
schema_errors: []
contract_violations: []
priority_conflicts: []
safe_to_ingest: true | false
recommended_action:
- accept
- accept_with_modification
- regenerate
- reject
