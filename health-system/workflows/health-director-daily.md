# Health Director Daily Workflow

## Morning run

1. Read canonical memory:
   - latest daily logs
   - adherence trend
   - fatigue trend
   - weight trend
   - training load status
   - hunger state if available
2. Collect validated specialist outputs only
   - Fitness Coach output must be validated before use
   - Dietitian output must be validated before use
3. Classify state:
   - adherence
   - fatigue
   - motivation
   - hunger
   - training load
4. Run conflict resolution rules
5. Classify conflict context explicitly:
   - behavior_state
   - adherence
   - fatigue
   - motivation
   - training_load
   - nutrition_pressure
6. Choose exactly one adjudication action:
   - accept_all
   - modify_fitness
   - modify_diet
   - modify_both
   - reject_and_regenerate_fitness
   - reject_and_regenerate_diet
   - hold_progression
7. Generate one unified `TODAY_PLAN`
8. Persist only the final canonical summary if appropriate

## Evening run

1. Capture what the user did
2. Capture what the user ate
3. Capture how the user felt
4. Update canonical daily log
5. Update metrics if needed:
   - adherence
   - fatigue
   - training load
   - weight
6. Decide whether specialist refresh is needed tomorrow

## Weekly run

1. Request Progress Analyst summary
2. Review adherence over the last 7 days
3. Review fatigue and weight trend
4. Review nutrition/training compatibility
5. Approve / reject progression
6. Write weekly summary

## Conflict adjudication block

When Fitness Coach and Dietitian both produce valid outputs, the Health Director must adjudicate, not just merge.

Check explicitly:
- fatigue vs deficit
- adherence vs tightening
- progression vs under-fueling risk
- motivation vs total plan friction
- weight stall vs consistency quality
- hunger vs sustainability

Use one outcome only:
- accept_all
- modify_fitness
- modify_diet
- modify_both
- reject_and_regenerate_fitness
- reject_and_regenerate_diet
- hold_progression

If adherence = low, behavior_state = drop_off, or fatigue = high, enter Stability Mode:
- training = minimal or simplified
- diet = simplified and non-restrictive
- focus = continuity
- progression paused
