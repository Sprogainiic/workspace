# Chat Gateway Scenarios

Use these to test:
- intent classification
- structured extraction
- specialist routing
- conflict resolution needs
- final response shape

Assumptions:
- user has max 3 formal training days/week
- user often struggles with consistency
- system front door is Chat Gateway
- final authority is Health Director
- specialists available:
  - Fitness Coach
  - Dietitian
  - Personal Chef
  - Consistency Coach

## Minimal test table format

| Case | User Message | Expected Intent | Expected Extraction | Expected Routing | HD Required | Notes |
|------|--------------|----------------|---------------------|------------------|-------------|-------|
| 1 | ate tuna salad and some bread | log_meal | meal_logged; foods=tuna salad,bread; protein_present=true; confidence=medium | Dietitian | yes | simple meal log |
| 2 | did 15 min walk, better than nothing I guess | log_workout,motivation_signal | walk 15 min; adherence_positive=true; self_evaluation=dismissive | Fitness Coach,Consistency Coach | yes | negative framing |
| 3 | energy low today | status_update | energy=low | Fitness Coach,Dietitian | yes | may affect training and food |
| 4 | ate kinda bad today lol | log_meal,status_update | meal_logged=true; meal_quality_self_report=poor; confidence=low | Dietitian,Consistency Coach | yes | do not infer calories |
| 5 | snacked a bit, nothing major | log_meal | snacking_reported=true; amount_known=false; severity_uncertain=true | Dietitian | yes | ambiguous intake |
| 6 | had some sweets at work again | log_meal,pattern_signal | sweets_consumed=true; context=work; repeat_pattern_hint=true | Dietitian,Consistency Coach | yes | pattern risk |
| 7 | breakfast was random, coffee and whatever was around | log_meal | breakfast; coffee=true; structure=unstructured; protein_present=unknown | Dietitian,Personal Chef | yes | fallback breakfast help |
| 8 | maybe I'll train later | plan_uncertainty,motivation_signal | workout_status=undecided; commitment_strength=low | Fitness Coach,Consistency Coach | yes | reduce friction |
| 9 | didn't do the workout | log_workout | workout_completed=false | Fitness Coach,Consistency Coach | yes | no punishment |
| 10 | not doing intervals today, no chance | log_workout,status_update | planned_component_rejected=intervals; training_tolerance=low | Fitness Coach | yes | downgrade, not failure |
| 11 | walked to the shop and back, does that count | log_workout,question | incidental_activity=true; activity_type=walking; duration=unknown | Fitness Coach,Consistency Coach | yes | counts as activity, maybe not full session |
| 12 | super tired but also feel guilty for skipping | status_update,emotional_signal | fatigue=high; guilt_present=true | Fitness Coach,Consistency Coach | yes | guilt + recovery |
| 13 | legs feel heavy today | status_update | localized_fatigue=legs; recovery_state=reduced | Fitness Coach | yes | possible downgrade |
| 14 | slept like garbage | status_update | sleep_quality=poor | Fitness Coach,Dietitian | yes | affects load + food simplicity |
| 15 | headache, low energy, and hungry all day | status_update | headache=true; energy=low; hunger=high | Dietitian,Fitness Coach | yes | possible under-fueling |
| 16 | should I still train today or just forget it | decision_request | decision_topic=training_today; ambivalence=true | Fitness Coach | yes | one clear action |
| 17 | what should I eat tonight, can't be bothered to cook | decision_request,meal_help | meal_request=dinner; cooking_motivation=low | Dietitian,Personal Chef | yes | simple options |
| 18 | can I eat pizza or does that ruin everything | decision_request,emotional_signal | food_question=pizza; catastrophic_framing=true | Dietitian,Consistency Coach | yes | anti-all-or-nothing |
| 19 | what's the absolute minimum I can do today | decision_request | minimum_action_requested=true | Fitness Coach,Consistency Coach | yes | fallback version |
| 20 | I don't feel like doing anything | emotional_signal,status_update | motivation=low; activation_resistance=high | Consistency Coach,Fitness Coach,Dietitian | yes | simplify both movement + food |
| 21 | I keep messing this up | emotional_signal | self_criticism=true; consistency_distress=true | Consistency Coach | yes | smaller next step |
| 22 | this system is annoying me today | feedback,emotional_signal | system_friction_reported=true; irritation=true | Consistency Coach | yes | reduce prompts/ask structure |
| 23 | honestly I just want to eat junk and lie down | emotional_signal,decision_request | motivation=low; comfort_food_drive=true; rest_preference=true | Dietitian,Consistency Coach,Fitness Coach | yes | conflict-heavy |
| 24 | I ate pasta and I'm tired so I'm skipping workout | log_meal,status_update,log_workout | foods=pasta; fatigue=elevated; workout_completed=false | Dietitian,Fitness Coach | yes | multi-intent |
| 25 | walked 10 min, ate badly, day feels wasted | log_workout,log_meal,emotional_signal | walk=10min; meal_quality_self_report=poor; negative_global_evaluation=true | Fitness Coach,Dietitian,Consistency Coach | yes | all-or-nothing correction |
| 26 | hungry all day and no chance I'm doing cardio tonight | status_update,log_workout | hunger=high; planned_workout_refused=true; workout_type=cardio | Dietitian,Fitness Coach | yes | under-fueling/training resistance |
| 27 | weight was 84.6 this morning and now I want burgers | log_metric,decision_request | weight=84.6; unit=kg; craving=burgers | Dietitian | yes | no moralizing |
| 28 | third day in a row I've had sweets at work | log_meal,pattern_signal | sweets=true; duration_days=3; context=work | Dietitian,Consistency Coach | yes | environmental pattern |
| 29 | I've skipped workouts all week | log_workout,pattern_signal | workout_adherence_week=very_low; duration=current_week | Fitness Coach,Consistency Coach | yes | reset/regression logic |
| 30 | lol | unclear | none | none | no | low-friction clarifier or wait |

## What to inspect after running

Look for failure modes:
- overconfident extraction
- under-routing
- over-routing
- bad orchestration
- awkward replies

## Confidence guidance

Use extraction confidence levels:
- high confidence: exact weight, exact workout duration
- medium confidence: tuna salad likely includes protein
- low confidence: "ate bad", "snacked a bit", "maybe later"

Without confidence scoring, memory quality degrades.
