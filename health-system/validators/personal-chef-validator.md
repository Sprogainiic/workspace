# Personal Chef Validator

## Status Levels

- PASS
- WARN
- FAIL

## FAIL Conditions

Reject output if:
- missing required section
- more than 4 meal options
- fewer than 2 meal options
- fallback meal missing
- meals resemble recipes or instructions
- meals require multi-step preparation
- meals conflict with Dietitian constraints
- meals ignore friction signals
- output increases complexity in Stability Mode
- includes descriptive or persuasive language
- includes calorie calculations or macro numbers

## WARN Conditions

- meals slightly too complex
- fallback not significantly simpler than other options
- options too similar (low usefulness)
- weak alignment explanation

## Contract Violations

- acting as Dietitian (setting rules)
- acting as planner (full meal plan)
- overriding Health Director
- introducing unnecessary complexity

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
