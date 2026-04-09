# Progress Analyst Validator

## Status Levels

- PASS
- WARN
- FAIL

## FAIL Conditions

Reject output if:
- missing required section
- no trend summary
- no classification
- classification contradicts data
- output prescribes actions (training/diet)
- output speaks to the user
- ignores adherence trend
- overreacts to short-term fluctuations
- uses emotional or motivational language
- invents precision without sufficient data

## WARN Conditions

- patterns too generic
- implications vague
- insufficient differentiation between noise and trend
- weak risk signals
- classification borderline ambiguous

## Contract Violations

- acting as planner instead of analyst
- overriding Health Director
- mixing interpretation with instruction

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
