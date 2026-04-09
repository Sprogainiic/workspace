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
   - Consistency Coach output must be validated before use
3. Classify state:
   - adherence
   - fatigue
   - motivation
   - hunger
   - training load
   - behavior_state from validated Consistency Coach output when available
4. Run conflict resolution rules
5. Classify conflict context explicitly:
   - behavior_state
   - adherence
   - fatigue
   - motivation
   - training_load
   - nutrition_pressure
6. Evaluate validated behavior intervention output explicitly:
   - primary intervention
   - minimum action
   - friction reduction
   - re-entry strategy
   - escalation flags
7. Choose exactly one adjudication action:
   - accept_all
   - modify_fitness
   - modify_diet
   - modify_both
   - reject_and_regenerate_fitness
   - reject_and_regenerate_diet
   - hold_progression
8. Generate one unified `TODAY_PLAN`
9. Persist only the final canonical summary if appropriate

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

1. Request validated Progress Analyst summary
2. Review adherence over the last 7 days
3. Review fatigue and weight trend
4. Review nutrition/training compatibility
5. Review analyst interpretation:
   - progress classification
   - key patterns
   - risk signals
   - system implications
6. Use analyst output to adjust confidence in progression or plateau interpretation
7. Approve / reject progression
8. Write weekly summary

## Conflict adjudication block

When Fitness Coach, Dietitian, and Consistency Coach produce valid outputs, the Health Director must adjudicate, not just merge.
Validated Progress Analyst output may influence interpretation confidence, but it may not directly prescribe action.

Check explicitly:
- fatigue vs deficit
- adherence vs tightening
- progression vs under-fueling risk
- motivation vs total plan friction
- weight stall vs consistency quality
- hunger vs sustainability
- behavior intervention vs training difficulty
- behavior intervention vs nutrition complexity
- re-entry strategy vs next-day planning
- analyst classification vs progression confidence
- analyst risk signals vs simplification/stabilization confidence

Use one outcome only:
- accept_all
- modify_fitness
- modify_diet
- modify_both
- reject_and_regenerate_fitness
- reject_and_regenerate_diet
- hold_progression

If adherence = low, behavior_state = drop_off, fatigue = high, or validated Consistency Coach escalation flags indicate overload/disengagement risk, enter Stability Mode:
- training = minimal or simplified
- diet = simplified and non-restrictive
- focus = continuity
- progression paused
- use validated minimum action and re-entry strategy as primary execution anchor

Validated Progress Analyst output may reinforce hold_progression or lower confidence in plateau/progress interpretation, but it does not directly trigger plan changes on its own.
