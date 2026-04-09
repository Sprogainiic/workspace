#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path('/home/sprogainiic/.openclaw/workspace/health-system/tests')
OUT = ROOT / 'results'
OUT.mkdir(parents=True, exist_ok=True)

SCENARIOS = {
    'scenario_1_overload_dropoff': {
        'INPUT_STATE': {
            'adherence': 'low',
            'behavior_state': 'drop_off',
            'fatigue': 'medium',
            'motivation': 'low',
            'training_load': 'medium',
            'nutrition_pressure': 'medium'
        },
        'FITNESS_OUTPUT': {
            'summary': 'Slight progression proposed based on previous baseline continuity assumption.',
            'recommendations': [{'type': 'today_session', 'payload': {'today_session': {'modality': 'cycling', 'duration_min': 30, 'intensity': 'moderate', 'instructions': ['Ride 30 min steady']}, 'minimum_version': {'modality': 'walk', 'duration_min': 10, 'instructions': ['Walk 10 min']}, 'progression_rule': 'Increase duration by 10% next session', 'load_assessment': 'medium'}}]
        },
        'FITNESS_VALIDATION': {'status': 'warn', 'schema_errors': [], 'contract_violations': [], 'priority_conflicts': ['progression_under_low_adherence'], 'safe_to_ingest': True, 'recommended_action': 'accept_with_modification'},
        'DIET_OUTPUT': {
            'summary': 'Mild deficit with moderate structure.',
            'recommendations': [{'type': 'nutrition_targets', 'payload': {'CALORIE_TARGET': {'Range': '1800-2050 kcal', 'Deficit Strategy': 'mild deficit'}, 'MACRO_GUIDANCE': {'Protein Priority': 'protein in each meal', 'Other Guidance': 'keep meals simple'}, 'MEAL_CONSTRAINTS': ['3 eating decisions max', 'protein first'], 'FALLBACK_STRATEGY': 'cottage cheese, tuna salad, simple rice + protein', 'ADJUSTMENT_RULES': ['If fatigue worsens, widen calories'], 'RISK_FLAGS': []}}]
        },
        'DIET_VALIDATION': {'status': 'pass', 'schema_errors': [], 'contract_violations': [], 'priority_conflicts': [], 'safe_to_ingest': True, 'recommended_action': 'accept'},
        'CONSISTENCY_OUTPUT': {
            'summary': 'Drop-off detected with overload risk.',
            'recommendations': [{'type': 'behavior_intervention', 'payload': {'BEHAVIOR_STATE': {'Summary': 'Drop-off with low adherence and low motivation'}, 'PRIMARY_INTERVENTION': 'Reduce expectations and preserve continuity', 'MINIMUM_ACTION': '10-minute walk only', 'FRICTION_REDUCTION': 'Remove need to choose between full and partial workout', 'REENTRY_STRATEGY': 'Resume baseline only after 2 consecutive days of minimum action', 'ESCALATION_FLAGS': ['overload_risk', 'disengagement_risk']}}]
        },
        'CONSISTENCY_VALIDATION': {'status': 'pass', 'schema_errors': [], 'contract_violations': [], 'priority_conflicts': [], 'safe_to_ingest': True, 'recommended_action': 'accept'}
    },
    'scenario_2_diet_conflict': {
        'INPUT_STATE': {
            'adherence': 'low',
            'behavior_state': 'inconsistent',
            'fatigue': 'low',
            'motivation': 'low',
            'training_load': 'low',
            'nutrition_pressure': 'high'
        },
        'FITNESS_OUTPUT': {
            'summary': 'Simple low-load session proposed.',
            'recommendations': [{'type': 'today_session', 'payload': {'today_session': {'modality': 'walk', 'duration_min': 20, 'intensity': 'easy', 'instructions': ['Walk 20 min']}, 'minimum_version': {'modality': 'walk', 'duration_min': 10, 'instructions': ['Walk 10 min']}, 'load_assessment': 'low'}}]
        },
        'FITNESS_VALIDATION': {'status': 'pass', 'schema_errors': [], 'contract_violations': [], 'priority_conflicts': [], 'safe_to_ingest': True, 'recommended_action': 'accept'},
        'DIET_OUTPUT': {
            'summary': 'Structured deficit with multiple rules.',
            'recommendations': [{'type': 'nutrition_targets', 'payload': {'CALORIE_TARGET': {'Range': '1750-1950 kcal', 'Deficit Strategy': 'mild deficit'}, 'MACRO_GUIDANCE': {'Protein Priority': 'protein in each meal', 'Other Guidance': 'fiber each meal'}, 'MEAL_CONSTRAINTS': ['track all meals', 'protein each meal', 'fiber each meal', 'avoid snacks'], 'FALLBACK_STRATEGY': 'simple protein + fruit meals', 'ADJUSTMENT_RULES': ['If adherence drops, simplify'], 'RISK_FLAGS': []}}]
        },
        'DIET_VALIDATION': {'status': 'warn', 'schema_errors': [], 'contract_violations': [], 'priority_conflicts': ['diet_complexity_high_for_low_motivation'], 'safe_to_ingest': True, 'recommended_action': 'accept_with_modification'},
        'CONSISTENCY_OUTPUT': {
            'summary': 'Decision fatigue detected.',
            'recommendations': [{'type': 'friction_reduction', 'payload': {'BEHAVIOR_STATE': {'Summary': 'Inconsistent with high decision fatigue'}, 'PRIMARY_INTERVENTION': 'Reduce decision load', 'MINIMUM_ACTION': 'Follow one meal rule only today', 'FRICTION_REDUCTION': 'Remove extra nutrition decisions', 'REENTRY_STRATEGY': 'Return to baseline after 1 low-friction day', 'ESCALATION_FLAGS': ['decision_fatigue']}}]
        },
        'CONSISTENCY_VALIDATION': {'status': 'pass', 'schema_errors': [], 'contract_violations': [], 'priority_conflicts': [], 'safe_to_ingest': True, 'recommended_action': 'accept'}
    },
    'scenario_3_motivation_spike_trap': {
        'INPUT_STATE': {
            'adherence': 'low',
            'behavior_state': 'restart_cycle',
            'fatigue': 'low',
            'motivation': 'high',
            'training_load': 'low',
            'nutrition_pressure': 'low'
        },
        'FITNESS_OUTPUT': {
            'summary': 'Expansion suggested due to current motivation bump.',
            'recommendations': [{'type': 'weekly_plan', 'payload': {'weekly_structure': {'formal_sessions_per_week': 3, 'session_types': ['walk', 'cycle', 'walk+intervals']}, 'minimum_version': {'modality': 'walk', 'duration_min': 10, 'instructions': ['Walk 10 min']}, 'progression_rule': 'Add intervals this week', 'load_assessment': 'medium'}}]
        },
        'FITNESS_VALIDATION': {'status': 'warn', 'schema_errors': [], 'contract_violations': [], 'priority_conflicts': ['motivation_spike_expansion_risk'], 'safe_to_ingest': True, 'recommended_action': 'accept_with_modification'},
        'DIET_OUTPUT': {
            'summary': 'Stable moderate structure.',
            'recommendations': [{'type': 'nutrition_targets', 'payload': {'CALORIE_TARGET': {'Range': '1850-2100 kcal', 'Deficit Strategy': 'mild deficit'}, 'MACRO_GUIDANCE': {'Protein Priority': 'protein each meal', 'Other Guidance': 'keep meals repeatable'}, 'MEAL_CONSTRAINTS': ['simple meals', 'repeatable meals'], 'FALLBACK_STRATEGY': 'tuna, cottage cheese, rice + protein', 'ADJUSTMENT_RULES': ['If hunger rises, widen calories'], 'RISK_FLAGS': []}}]
        },
        'DIET_VALIDATION': {'status': 'pass', 'schema_errors': [], 'contract_violations': [], 'priority_conflicts': [], 'safe_to_ingest': True, 'recommended_action': 'accept'},
        'CONSISTENCY_OUTPUT': {
            'summary': 'Restart cycle detected; controlled re-entry needed.',
            'recommendations': [{'type': 'reentry_plan', 'payload': {'BEHAVIOR_STATE': {'Summary': 'Restart cycle after unstable adherence'}, 'PRIMARY_INTERVENTION': 'Controlled re-entry only', 'MINIMUM_ACTION': '10-minute walk', 'FRICTION_REDUCTION': 'Remove expectation of full restart', 'REENTRY_STRATEGY': 'Stay at baseline until 2-3 completed days', 'ESCALATION_FLAGS': ['restart_cycle_risk']}}]
        },
        'CONSISTENCY_VALIDATION': {'status': 'pass', 'schema_errors': [], 'contract_violations': [], 'priority_conflicts': [], 'safe_to_ingest': True, 'recommended_action': 'accept'}
    }
}

def get_behavior_payload(s):
    return s['CONSISTENCY_OUTPUT']['recommendations'][0]['payload']

def detect_local_conflicts(state, scenario):
    rules = []
    if state['behavior_state'] in ('inconsistent', 'drop_off') or state['adherence'] == 'low':
        if 'progression_rule' in json.dumps(scenario['FITNESS_OUTPUT']):
            rules.append('consistency_vs_fitness_progression_conflict')
    if state['adherence'] == 'low' and (state['motivation'] == 'low' or state['nutrition_pressure'] == 'high'):
        rules.append('consistency_vs_diet_restriction_conflict')
    if state['behavior_state'] == 'restart_cycle':
        rules.append('restart_cycle_handling')
    if state['motivation'] == 'high' and state['adherence'] == 'low':
        rules.append('motivation_spike_trap')
    return rules

def detect_global_instability(state, behavior_payload, local_conflicts):
    flags = set(behavior_payload.get('ESCALATION_FLAGS', []))
    overload_flags = {'overload_risk', 'disengagement_risk'}
    both_domains_under_strain = (
        'consistency_vs_fitness_progression_conflict' in local_conflicts and
        'consistency_vs_diet_restriction_conflict' in local_conflicts
    )
    return (
        state['fatigue'] == 'high' or
        state['behavior_state'] == 'drop_off' or
        (state['behavior_state'] == 'restart_cycle' and state['adherence'] == 'low') or
        (state['adherence'] == 'low' and bool(flags & overload_flags) and both_domains_under_strain)
    )

def choose_action(state, local_conflicts, global_instability):
    if 'restart_cycle_handling' in local_conflicts or 'motivation_spike_trap' in local_conflicts:
        return 'hold_progression'
    if global_instability and 'consistency_vs_fitness_progression_conflict' in local_conflicts and 'consistency_vs_diet_restriction_conflict' in local_conflicts:
        return 'modify_both'
    if 'consistency_vs_fitness_progression_conflict' in local_conflicts and 'consistency_vs_diet_restriction_conflict' in local_conflicts:
        return 'modify_both'
    if 'consistency_vs_diet_restriction_conflict' in local_conflicts:
        return 'modify_diet'
    if 'consistency_vs_fitness_progression_conflict' in local_conflicts:
        return 'modify_fitness'
    if global_instability:
        return 'modify_both'
    return 'accept_all'

def adjudicate(s):
    state = s['INPUT_STATE']
    behavior_payload = get_behavior_payload(s)
    local_conflicts = detect_local_conflicts(state, s)
    global_instability = detect_global_instability(state, behavior_payload, local_conflicts)
    action = choose_action(state, local_conflicts, global_instability)

    final_plan = {
        'training': 'minimum or simplified' if action in ('modify_fitness', 'modify_both', 'hold_progression') else 'as proposed',
        'nutrition': 'simplified, non-restrictive' if action in ('modify_diet', 'modify_both') or global_instability else 'as proposed',
        'focus': 'continuity',
        'stability_mode': global_instability,
        'anchor': behavior_payload['MINIMUM_ACTION']
    }

    classification = {
        'behavior_state': state['behavior_state'],
        'adherence': state['adherence'],
        'fatigue': state['fatigue'],
        'motivation': state['motivation'],
        'training_load': state['training_load'],
        'nutrition_pressure': state['nutrition_pressure'],
        'global_instability': global_instability,
        'local_conflict': len(local_conflicts) > 0
    }

    reasoning = 'Adherence continuity overrides optimization; use validated behavior anchor and separate local correction from system-wide stabilization.'

    return classification, local_conflicts, action, final_plan, reasoning

for name, scenario in SCENARIOS.items():
    classification, rules, action, final_plan, reasoning = adjudicate(scenario)
    trace = dict(scenario)
    trace['HEALTH_DIRECTOR_CLASSIFICATION'] = classification
    trace['TRIGGERED_RULES'] = rules
    trace['ADJUDICATION_ACTION'] = action
    trace['FINAL_PLAN'] = final_plan
    trace['REASONING'] = reasoning
    (OUT / f'{name}.json').write_text(json.dumps(trace, indent=2))

print(json.dumps({'written': sorted([p.name for p in OUT.glob('*.json')])}, indent=2))
