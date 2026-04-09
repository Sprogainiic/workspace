# Dietitian Validator

## Status levels

- pass
- warn
- fail

## FAIL conditions (hard reject)

Reject output if:
- missing any required section
- calorie target is a single fixed number (no range)
- deficit appears aggressive
- no fallback strategy
- includes recipes instead of constraints
- includes direct user-facing language
- includes moral judgment about food
- ignores fatigue when high
- ignores adherence when low
- macro precision exceeds available input
- conflicts with training recovery needs

## WARN conditions

- too many constraints (>5)
- overly complex fallback strategy
- vague adjustment rules
- insufficient protein guidance
- not aligned with preferences

## Contract violations

- attempts to control training
- attempts to override Health Director
- prescribes rigid meal plans

## Output

Return:
- status: pass | warn | fail
- schema_errors: []
- contract_violations: []
- priority_conflicts: []
- safe_to_ingest: true | false
- recommended_action: accept | accept_with_modification | regenerate | reject
