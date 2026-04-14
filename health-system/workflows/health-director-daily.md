# Health Director Daily Workflow

## Default runtime inputs
1. current state snapshot
2. latest daily summary
3. validated specialist outputs for this cycle only
4. latest weekly summary only when trend confidence matters

Do not load broad daily log history by default.
Do not load raw chat by default.

## Morning run
1. Load snapshot
2. Check active risk flags, simplification level, and open ambiguities
3. Decide whether any specialist is needed
4. Build only the required briefs:
   - training_brief
   - nutrition_brief
   - behavior_brief
   - meal_execution_brief
5. Validate specialist outputs deterministically
6. Adjudicate conflicts
7. Produce one unified `TODAY_PLAN`

## Evening run
1. Persist approved structured events from the day
2. Update snapshot
3. Generate daily summary on schedule
4. Mark any unresolved ambiguity explicitly

## Weekly run
1. Load latest weekly summary package
2. Request Progress Analyst only when trend interpretation is needed
3. Use analyst output as interpretation support, not authority
4. Adjust progression confidence or simplification posture if justified

## Stability Mode
Enter Stability Mode when snapshot indicates:
- adherence low
- behavior_state drop_off or restart_cycle
- fatigue high
- overload risk active

In Stability Mode:
- training simplified
- nutrition simplified and non-restrictive
- meal options reduced
- continuity outranks progression
