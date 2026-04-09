#!/usr/bin/env python3
import json
from dataclasses import dataclass
from pathlib import Path

ROOT = Path('/home/sprogainiic/.openclaw/workspace/health-system/tests')
OUT = ROOT / 'multi_day_results'
OUT.mkdir(parents=True, exist_ok=True)

@dataclass
class DayState:
    day: int
    adherence: str
    fatigue: str
    motivation: str
    hunger: str
    training_load: str
    nutrition_pressure: str
    behavior_state: str
    friction_signals: list
    analyst_state: str


def scenario_fragile_restart_week():
    return [
        DayState(1, 'high', 'low', 'high', 'low', 'low', 'low', 'stable', [], 'improving'),
        DayState(2, 'low', 'medium', 'low', 'medium', 'medium', 'medium', 'drop_off', ['time', 'decision_fatigue'], 'unstable'),
        DayState(3, 'low', 'medium', 'low', 'medium', 'medium', 'medium', 'drop_off', ['time', 'decision_fatigue'], 'unstable'),
        DayState(4, 'medium', 'low', 'medium', 'low', 'low', 'low', 'restart_cycle', ['decision_fatigue'], 'unstable'),
        DayState(5, 'medium', 'low', 'medium', 'low', 'low', 'low', 'inconsistent', ['time'], 'unstable'),
        DayState(6, 'low', 'medium', 'low', 'medium', 'medium', 'medium', 'inconsistent', ['time', 'decision_fatigue'], 'unstable'),
        DayState(7, 'medium', 'low', 'medium', 'low', 'low', 'low', 'stable', [], 'improving'),
    ]


def scenario_decision_fatigue_nutrition_week():
    return [
        DayState(1, 'medium', 'low', 'low', 'high', 'low', 'high', 'inconsistent', ['time', 'decision_fatigue'], 'unstable'),
        DayState(2, 'medium', 'low', 'low', 'high', 'low', 'high', 'inconsistent', ['time', 'decision_fatigue'], 'unstable'),
        DayState(3, 'medium', 'low', 'low', 'high', 'low', 'high', 'inconsistent', ['time', 'decision_fatigue'], 'unstable'),
        DayState(4, 'medium', 'low', 'medium', 'medium', 'low', 'high', 'inconsistent', ['decision_fatigue'], 'unstable'),
        DayState(5, 'medium', 'low', 'medium', 'medium', 'low', 'high', 'inconsistent', ['decision_fatigue'], 'unstable'),
        DayState(6, 'medium', 'low', 'medium', 'medium', 'low', 'high', 'inconsistent', ['decision_fatigue'], 'unstable'),
        DayState(7, 'medium', 'low', 'medium', 'medium', 'low', 'high', 'inconsistent', ['time'], 'unstable'),
    ]


def scenario_fatigue_escalation_week():
    return [
        DayState(1, 'medium', 'low', 'medium', 'low', 'low', 'low', 'stable', [], 'stable'),
        DayState(2, 'medium', 'medium', 'medium', 'low', 'low', 'low', 'stable', [], 'stable'),
        DayState(3, 'medium', 'medium', 'medium', 'low', 'medium', 'low', 'stable', [], 'stable'),
        DayState(4, 'medium', 'high', 'medium', 'medium', 'medium', 'low', 'stable', [], 'unstable'),
        DayState(5, 'medium', 'high', 'medium', 'medium', 'medium', 'low', 'stable', [], 'unstable'),
        DayState(6, 'medium', 'high', 'medium', 'medium', 'medium', 'low', 'stable', [], 'unstable'),
        DayState(7, 'medium', 'high', 'medium', 'medium', 'medium', 'low', 'stable', [], 'unstable'),
    ]


def scenario_stable_improvement_week():
    return [
        DayState(1, 'medium', 'low', 'medium', 'low', 'low', 'low', 'stable', [], 'improving'),
        DayState(2, 'high', 'low', 'medium', 'low', 'low', 'low', 'stable', [], 'improving'),
        DayState(3, 'high', 'low', 'medium', 'low', 'low', 'low', 'stable', [], 'improving'),
        DayState(4, 'high', 'low', 'high', 'low', 'low', 'low', 'stable', [], 'improving'),
        DayState(5, 'high', 'low', 'high', 'low', 'low', 'low', 'stable', [], 'improving'),
        DayState(6, 'high', 'low', 'high', 'low', 'low', 'low', 'stable', [], 'improving'),
        DayState(7, 'high', 'low', 'high', 'low', 'low', 'low', 'stable', [], 'improving'),
    ]


def fitness_output(state):
    if state.behavior_state in ('drop_off', 'restart_cycle') or state.adherence == 'low':
        return {
            'summary': 'Simplified low-load session.',
            'recommendations': [{'type': 'today_session', 'payload': {'today_session': {'modality': 'walk', 'duration_min': 20, 'intensity': 'easy', 'instructions': ['Walk 20 min']}, 'minimum_version': {'modality': 'walk', 'duration_min': 10, 'instructions': ['Walk 10 min']}, 'load_assessment': 'low'}}]
        }
    if state.fatigue == 'high':
        return {
            'summary': 'Recovery-biased session.',
            'recommendations': [{'type': 'recovery_substitution', 'payload': {'today_session': {'modality': 'walk', 'duration_min': 10, 'intensity': 'very_easy', 'instructions': ['Walk 10 min']}, 'minimum_version': {'modality': 'walk', 'duration_min': 10, 'instructions': ['Walk 10 min']}, 'load_assessment': 'low', 'regression_rule': 'Hold progression until fatigue falls'}}]
        }
    return {
        'summary': 'Moderate steady session.',
        'recommendations': [{'type': 'today_session', 'payload': {'today_session': {'modality': 'cycle', 'duration_min': 30, 'intensity': 'easy', 'instructions': ['Cycle 30 min steady']}, 'minimum_version': {'modality': 'walk', 'duration_min': 10, 'instructions': ['Walk 10 min']}, 'progression_rule': 'Add 5-10% only if stable for 3-4 days', 'load_assessment': 'medium'}}]
    }


def diet_output(state):
    if state.fatigue == 'high':
        return {
            'summary': 'Reduced or paused deficit for recovery.',
            'recommendations': [{'type': 'nutrition_targets', 'payload': {'CALORIE_TARGET': {'Range': '1950-2250 kcal', 'Deficit Strategy': 'paused or minimal'}, 'MACRO_GUIDANCE': {'Protein Priority': 'protein each meal', 'Other Guidance': 'fiber and repeatable meals'}, 'MEAL_CONSTRAINTS': ['simple meals', 'repeatable meals'], 'FALLBACK_STRATEGY': 'cottage cheese, tuna, rice + protein', 'ADJUSTMENT_RULES': ['If fatigue remains high, keep deficit paused'], 'RISK_FLAGS': ['fatigue_recovery_priority']}}]
        }
    if state.adherence == 'low':
        return {
            'summary': 'Simplified eating structure with wider range.',
            'recommendations': [{'type': 'nutrition_targets', 'payload': {'CALORIE_TARGET': {'Range': '1900-2200 kcal', 'Deficit Strategy': 'reduced'}, 'MACRO_GUIDANCE': {'Protein Priority': 'protein each meal', 'Other Guidance': 'fiber and repeatable meals'}, 'MEAL_CONSTRAINTS': ['simple meals', 'repeatable meals'], 'FALLBACK_STRATEGY': 'cottage cheese, tuna, rice + protein', 'ADJUSTMENT_RULES': ['If adherence improves, tighten slightly'], 'RISK_FLAGS': []}}]
        }
    if state.behavior_state == 'stable' and state.fatigue == 'low':
        return {
            'summary': 'Moderate structure with mild deficit.',
            'recommendations': [{'type': 'nutrition_targets', 'payload': {'CALORIE_TARGET': {'Range': '1800-2050 kcal', 'Deficit Strategy': 'mild deficit'}, 'MACRO_GUIDANCE': {'Protein Priority': 'protein in each meal', 'Other Guidance': 'fiber and repeatable meals'}, 'MEAL_CONSTRAINTS': ['simple meals', 'repeatable meals'], 'FALLBACK_STRATEGY': 'tuna salad, cottage cheese, rice + protein', 'ADJUSTMENT_RULES': ['If adherence drops, simplify'], 'RISK_FLAGS': []}}]
        }
    return {
        'summary': 'Simplified nutrition structure.',
        'recommendations': [{'type': 'nutrition_targets', 'payload': {'CALORIE_TARGET': {'Range': '1850-2100 kcal', 'Deficit Strategy': 'mild deficit'}, 'MACRO_GUIDANCE': {'Protein Priority': 'protein each meal', 'Other Guidance': 'keep meals repeatable'}, 'MEAL_CONSTRAINTS': ['simple meals', 'repeatable meals'], 'FALLBACK_STRATEGY': 'tuna, cottage cheese, rice + protein', 'ADJUSTMENT_RULES': ['If fatigue worsens, widen calories'], 'RISK_FLAGS': []}}]
    }


def consistency_output(state):
    if state.behavior_state in ('drop_off', 'restart_cycle') or state.adherence == 'low' or 'decision_fatigue' in state.friction_signals:
        return {
            'summary': 'Behavior instability; reduce friction.',
            'recommendations': [{'type': 'behavior_intervention', 'payload': {'BEHAVIOR_STATE': {'Summary': f'{state.behavior_state} with low continuity'}, 'PRIMARY_INTERVENTION': 'Reduce decision load and preserve continuity', 'MINIMUM_ACTION': '10-minute walk only', 'FRICTION_REDUCTION': 'Remove extra decisions', 'REENTRY_STRATEGY': 'Resume baseline after one low-friction day', 'ESCALATION_FLAGS': ['overload_risk'] if state.fatigue == 'high' else ['decision_fatigue']}}]
        }
    if state.fatigue == 'high':
        return {
            'summary': 'Fatigue rising; simplify execution.',
            'recommendations': [{'type': 'behavior_intervention', 'payload': {'BEHAVIOR_STATE': {'Summary': 'Stable but fatigued'}, 'PRIMARY_INTERVENTION': 'Reduce effort and protect continuity', 'MINIMUM_ACTION': '10-minute walk', 'FRICTION_REDUCTION': 'Trim task complexity', 'REENTRY_STRATEGY': 'Hold baseline until fatigue falls', 'ESCALATION_FLAGS': ['fatigue_risk']}}]
        }
    return {
        'summary': 'Stable execution anchor.',
        'recommendations': [{'type': 'behavior_intervention', 'payload': {'BEHAVIOR_STATE': {'Summary': 'Stable and adherent'}, 'PRIMARY_INTERVENTION': 'Maintain current baseline', 'MINIMUM_ACTION': '20-minute session', 'FRICTION_REDUCTION': 'Keep options small', 'REENTRY_STRATEGY': 'Progress only after stable streak', 'ESCALATION_FLAGS': []}}]
    }


def progress_output(state):
    # tighter plateau validation: plateau only when adherence is not low, behavior is stable, and fatigue is not high
    if state.behavior_state in ('drop_off', 'restart_cycle') or state.adherence == 'low':
        cls = 'unstable'
        summary = {
            'Adherence': 'volatile',
            'Fatigue': f'{state.fatigue}',
            'Training': 'irregular',
            'Nutrition': 'mixed',
            'Weight': 'not decision-grade'
        }
        patterns = ['Restart-cycle behavior', 'Low signal reliability']
        risks = ['False plateau risk']
        implications = ['Do not treat trend as decision-grade', 'Stabilization required before progression']
    elif 'decision_fatigue' in state.friction_signals and state.adherence != 'high':
        cls = 'insufficient_data'
        summary = {
            'Adherence': 'mixed',
            'Fatigue': f'{state.fatigue}',
            'Training': 'mixed',
            'Nutrition': 'mixed',
            'Weight': 'not decision-grade'
        }
        patterns = ['Execution friction reduces interpretability']
        risks = ['Weak signal quality']
        implications = ['Avoid strong trend claims', 'Use only as low-confidence context']
    elif state.fatigue == 'high':
        cls = 'unstable'
        summary = {
            'Adherence': f'{state.adherence}',
            'Fatigue': 'increasing',
            'Training': 'consistency weakening',
            'Nutrition': 'stable but vulnerable',
            'Weight': 'unclear'
        }
        patterns = ['Rising fatigue trend', 'Overload risk']
        risks = ['Progress confidence reduced']
        implications = ['Lower confidence in progression', 'Simplify if fatigue persists']
    elif state.adherence == 'high' and state.fatigue == 'low' and state.behavior_state == 'stable':
        cls = 'improving'
        summary = {
            'Adherence': 'stable',
            'Fatigue': 'low',
            'Training': 'regular',
            'Nutrition': 'stable',
            'Weight': 'directional signal possible'
        }
        patterns = ['Stable adherence streak', 'Signal quality adequate']
        risks = ['Monitor for overconfidence']
        implications = ['Progression confidence improves', 'Interpretation quality is higher']
    else:
        cls = 'insufficient_data'
        summary = {
            'Adherence': f'{state.adherence}',
            'Fatigue': f'{state.fatigue}',
            'Training': 'mixed',
            'Nutrition': 'mixed',
            'Weight': 'unclear'
        }
        patterns = ['Conditions are mixed', 'Trend confidence remains limited']
        risks = ['False plateau classification risk']
        implications = ['Treat as weak signal', 'Hold confidence moderate']
    return {
        'summary': 'Derived from simulated daily state.',
        'recommendations': [{'type': 'trend_analysis', 'payload': {'TREND_SUMMARY': summary, 'KEY_PATTERNS': patterns, 'RISK_SIGNALS': risks, 'PROGRESS_CLASSIFICATION': cls, 'SYSTEM_IMPLICATIONS': implications}}]
    }


def chef_output(state, diet_payload, consistency_payload):
    stability = state.behavior_state in ('drop_off', 'restart_cycle') or state.adherence == 'low' or state.fatigue == 'high' or 'decision_fatigue' in state.friction_signals
    if stability:
        mode = 'stability'
        options = ['Cottage cheese + fruit', 'Tuna salad', 'Rice + pre-cooked chicken']
        fallback = 'Cottage cheese only'
    else:
        mode = 'normal'
        options = ['Cottage cheese + fruit', 'Tuna salad', 'Rice + chicken', 'Greek yogurt + berries']
        fallback = 'Tuna salad'
    return {
        'summary': 'Meal execution simplified to match system state.',
        'recommendations': [{'type': 'meal_options', 'payload': {'SIMPLICITY_MODE': mode, 'MEAL_OPTIONS': options, 'FALLBACK_MEAL': fallback, 'CONSTRAINT_ALIGNMENT': 'Meals remain simple, repeatable, and protein-first within Dietitian constraints.'}}]
    }


def classify_and_adjudicate(state, consistency_payload, analyst_payload, stable_streak):
    behavior_summary = consistency_payload['BEHAVIOR_STATE']['Summary']
    escalation_flags = set(consistency_payload['ESCALATION_FLAGS'])
    analyst_class = analyst_payload['recommendations'][0]['payload']['PROGRESS_CLASSIFICATION']

    local_conflict = state.adherence == 'low' or state.behavior_state in ('inconsistent', 'drop_off', 'restart_cycle')
    friction_only = (
        state.fatigue != 'high' and
        state.training_load == 'low' and
        state.behavior_state == 'inconsistent' and
        'decision_fatigue' in state.friction_signals and
        state.nutrition_pressure == 'high'
    )
    heavy_global_instability = (
        state.fatigue == 'high' or
        state.behavior_state == 'drop_off' or
        (state.behavior_state == 'restart_cycle' and state.adherence == 'low') or
        (state.adherence == 'low' and 'overload_risk' in escalation_flags and state.training_load != 'low' and state.nutrition_pressure != 'low')
    )

    # progression re-entry gating
    progression_unlocked = stable_streak >= 3 and state.behavior_state == 'stable' and state.fatigue == 'low' and state.adherence == 'high'

    if heavy_global_instability:
        action = 'modify_both_heavy'
    elif friction_only:
        action = 'friction_reduction_only'
    elif state.behavior_state == 'restart_cycle' or (state.adherence == 'low' and state.motivation == 'low'):
        action = 'hold_progression'
    elif state.fatigue == 'medium' and state.training_load == 'medium':
        action = 'modify_both_light'
    elif progression_unlocked and analyst_class == 'improving':
        action = 'accept_all'
    elif state.behavior_state == 'stable' and state.fatigue == 'low' and state.adherence in ('medium', 'high'):
        action = 'monitor_only'
    elif state.adherence == 'low' and state.nutrition_pressure != 'low':
        action = 'modify_diet'
    elif local_conflict:
        action = 'modify_fitness'
    else:
        action = 'monitor_only'

    final = {
        'training': 'minimum or simplified' if action in ('modify_both_heavy', 'modify_both_light', 'hold_progression', 'modify_fitness') else 'as proposed',
        'nutrition': 'simplified, non-restrictive' if action in ('modify_both_heavy', 'modify_both_light', 'modify_diet', 'hold_progression', 'friction_reduction_only') else 'as proposed',
        'meals': '2-3 simple options, fallback first' if action in ('modify_both_heavy', 'hold_progression', 'friction_reduction_only') or heavy_global_instability or state.behavior_state != 'stable' else '3-4 simple options',
        'focus': 'continuity' if action != 'accept_all' else 'progression',
        'stability_mode': heavy_global_instability,
        'anchor': consistency_payload['MINIMUM_ACTION']
    }
    return behavior_summary, local_conflict, heavy_global_instability, friction_only, progression_unlocked, action, final


def run_scenario(name, states):
    day_traces = []
    stats = {
        'days': 0,
        'stability_mode_days': 0,
        'hold_progression_days': 0,
        'modify_both_days': 0,
        'modify_both_light_days': 0,
        'modify_both_heavy_days': 0,
        'friction_reduction_only_days': 0,
        'monitor_only_days': 0,
        'chef_stability_days': 0,
        'analyst_classifications': {},
        'blocked_progression_days': 0,
        'allowed_progression_days': 0
    }

    stable_streak = 0
    for s in states:
        if s.behavior_state == 'stable' and s.adherence == 'high' and s.fatigue == 'low':
            stable_streak += 1
        else:
            stable_streak = 0

        fitness = fitness_output(s)
        diet = diet_output(s)
        consistency = consistency_output(s)
        analyst = progress_output(s)
        chef = chef_output(s, diet, consistency)
        behavior_summary, local_conflict, heavy_global_instability, friction_only, progression_unlocked, action, final = classify_and_adjudicate(s, consistency['recommendations'][0]['payload'], analyst, stable_streak)

        trace = {
            'day': s.day,
            'INPUT_STATE': s.__dict__,
            'FITNESS_OUTPUT': fitness,
            'FITNESS_VALIDATION': {'status': 'pass', 'schema_errors': [], 'contract_violations': [], 'priority_conflicts': [], 'safe_to_ingest': True, 'recommended_action': 'accept'},
            'DIET_OUTPUT': diet,
            'DIET_VALIDATION': {'status': 'pass', 'schema_errors': [], 'contract_violations': [], 'priority_conflicts': [], 'safe_to_ingest': True, 'recommended_action': 'accept'},
            'CONSISTENCY_OUTPUT': consistency,
            'CONSISTENCY_VALIDATION': {'status': 'pass', 'schema_errors': [], 'contract_violations': [], 'priority_conflicts': [], 'safe_to_ingest': True, 'recommended_action': 'accept'},
            'PROGRESS_ANALYST_OUTPUT': analyst,
            'PROGRESS_ANALYST_VALIDATION': {'status': 'pass', 'schema_errors': [], 'contract_violations': [], 'priority_conflicts': [], 'safe_to_ingest': True, 'recommended_action': 'accept'},
            'PERSONAL_CHEF_OUTPUT': chef,
            'PERSONAL_CHEF_VALIDATION': {'status': 'pass', 'schema_errors': [], 'contract_violations': [], 'priority_conflicts': [], 'safe_to_ingest': True, 'recommended_action': 'accept'},
            'HEALTH_DIRECTOR_CLASSIFICATION': {
                'behavior_state': s.behavior_state,
                'adherence': s.adherence,
                'fatigue': s.fatigue,
                'motivation': s.motivation,
                'training_load': s.training_load,
                'nutrition_pressure': s.nutrition_pressure,
                'global_instability': heavy_global_instability,
                'local_conflict': local_conflict,
                'friction_only': friction_only,
                'progression_unlocked': progression_unlocked,
                'behavior_summary': behavior_summary,
                'analyst_classification': analyst['recommendations'][0]['payload']['PROGRESS_CLASSIFICATION']
            },
            'TRIGGERED_RULES': [r for r in [
                'consistency_vs_fitness_progression_conflict' if local_conflict else None,
                'consistency_vs_diet_restriction_conflict' if (s.adherence == 'low' and s.nutrition_pressure != 'low') else None,
                'analyst_instability_reduces_progression_confidence' if analyst['recommendations'][0]['payload']['PROGRESS_CLASSIFICATION'] == 'unstable' else None,
                'chef_execution_rules_stability_mode' if chef['recommendations'][0]['payload']['SIMPLICITY_MODE'] == 'stability' else None,
                'friction_reduction_only' if friction_only else None,
                'progression_reentry_gate' if not progression_unlocked and s.behavior_state == 'stable' and s.fatigue == 'low' else None,
            ] if r],
            'ADJUDICATION_ACTION': action,
            'FINAL_PLAN': final,
            'CROSS_AGENT_CONSISTENCY_CHECK': {
                'fitness_vs_diet': True,
                'chef_vs_dietitian': True,
                'chef_vs_consistency': True,
                'analyst_interpretation_only': True
            },
            'REASONING': 'Adherence continuity and behavior friction override optimization; local friction, global instability, and progression confidence are separated explicitly.'
        }
        day_traces.append(trace)
        stats['days'] += 1
        stats['stability_mode_days'] += 1 if final['stability_mode'] else 0
        stats['hold_progression_days'] += 1 if action == 'hold_progression' else 0
        stats['modify_both_days'] += 1 if action in ('modify_both_light', 'modify_both_heavy') else 0
        stats['modify_both_light_days'] += 1 if action == 'modify_both_light' else 0
        stats['modify_both_heavy_days'] += 1 if action == 'modify_both_heavy' else 0
        stats['friction_reduction_only_days'] += 1 if action == 'friction_reduction_only' else 0
        stats['monitor_only_days'] += 1 if action == 'monitor_only' else 0
        stats['chef_stability_days'] += 1 if chef['recommendations'][0]['payload']['SIMPLICITY_MODE'] == 'stability' else 0
        cls = analyst['recommendations'][0]['payload']['PROGRESS_CLASSIFICATION']
        stats['analyst_classifications'][cls] = stats['analyst_classifications'].get(cls, 0) + 1
        if action in ('hold_progression', 'modify_both_light', 'modify_both_heavy'):
            stats['blocked_progression_days'] += 1
        else:
            stats['allowed_progression_days'] += 1

    (OUT / f'{name}.json').write_text(json.dumps(day_traces, indent=2))
    return day_traces, stats

SCENARIOS = {
    'fragile_restart_week': scenario_fragile_restart_week(),
    'decision_fatigue_nutrition_week': scenario_decision_fatigue_nutrition_week(),
    'fatigue_escalation_week': scenario_fatigue_escalation_week(),
    'stable_improvement_week': scenario_stable_improvement_week(),
}

summary = {}
for name, states in SCENARIOS.items():
    _, stats = run_scenario(name, states)
    summary[name] = stats

(OUT / 'summary.json').write_text(json.dumps(summary, indent=2))
print(json.dumps({'scenarios': list(SCENARIOS.keys()), 'summary_file': str(OUT / 'summary.json')}, indent=2))
