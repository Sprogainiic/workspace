# Integration Scenarios

## Required trace fields

For each scenario, log:
- INPUT_STATE
- FITNESS_OUTPUT
- FITNESS_VALIDATION
- DIET_OUTPUT
- DIET_VALIDATION
- CONSISTENCY_OUTPUT
- CONSISTENCY_VALIDATION
- HEALTH_DIRECTOR_CLASSIFICATION
- TRIGGERED_RULES
- ADJUDICATION_ACTION
- FINAL_PLAN
- REASONING

## Scenario 1 — Overload + Drop-off
- adherence: low
- behavior_state: drop_off
- fatigue: medium
- motivation: low
- training_load: medium
- nutrition_pressure: medium

Expected:
- action = modify_both OR hold_progression
- Stability Mode = ON

## Scenario 2 — Diet Conflict (Decision Fatigue)
- adherence: low
- behavior_state: inconsistent
- fatigue: low
- motivation: low
- nutrition_pressure: high
- training_load: low

Expected:
- action = modify_diet

## Scenario 3 — Motivation Spike Trap
- adherence: low
- behavior_state: restart_cycle
- fatigue: low
- motivation: high
- training_load: low
- nutrition_pressure: low

Expected:
- action = hold_progression OR modify_fitness
