#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path('/home/sprogainiic/.openclaw/workspace/health-system/tests')
OUT = ROOT / 'chat_gateway_results'
OUT.mkdir(parents=True, exist_ok=True)

CASES = [
    {
        'case': 1,
        'message': 'ate tuna salad and some bread',
        'expected': {
            'intent': ['log_meal'],
            'extracted': {'meal_logged': True, 'foods': ['tuna salad', 'bread'], 'protein_present': True, 'extraction_confidence': 'medium'},
            'route_to': ['Dietitian'],
            'health_director_required': True,
            'notes': 'Simple meal log; no need for Chef unless asked.'
        }
    },
    {
        'case': 4,
        'message': 'ate kinda bad today lol',
        'expected': {
            'intent': ['log_meal', 'status_update'],
            'extracted': {'meal_logged': True, 'meal_quality_self_report': 'poor', 'extraction_confidence': 'low'},
            'route_to': ['Dietitian', 'Consistency Coach'],
            'health_director_required': True,
            'notes': 'Do not infer calories or exact foods.'
        }
    },
    {
        'case': 8,
        'message': "maybe I'll train later",
        'expected': {
            'intent': ['plan_uncertainty', 'motivation_signal'],
            'extracted': {'workout_status': 'undecided', 'commitment_strength': 'low', 'extraction_confidence': 'medium'},
            'route_to': ['Fitness Coach', 'Consistency Coach'],
            'health_director_required': True,
            'notes': 'Low commitment; reduce friction.'
        }
    },
    {
        'case': 12,
        'message': 'super tired but also feel guilty for skipping',
        'expected': {
            'intent': ['status_update', 'emotional_signal'],
            'extracted': {'fatigue': 'high', 'guilt_present': True, 'extraction_confidence': 'high'},
            'route_to': ['Fitness Coach', 'Consistency Coach'],
            'health_director_required': True,
            'notes': 'Recovery and guilt handling both matter.'
        }
    },
    {
        'case': 17,
        'message': "what should I eat tonight, can't be bothered to cook",
        'expected': {
            'intent': ['decision_request', 'meal_help'],
            'extracted': {'meal_request': 'dinner', 'motivation_for_cooking': 'low', 'extraction_confidence': 'high'},
            'route_to': ['Dietitian', 'Personal Chef'],
            'health_director_required': True,
            'notes': 'Chef should provide simple options within constraints.'
        }
    },
    {
        'case': 24,
        'message': "I ate pasta and I'm tired so I'm skipping workout",
        'expected': {
            'intent': ['log_meal', 'status_update', 'log_workout'],
            'extracted': {'foods': ['pasta'], 'fatigue': 'elevated', 'workout_completed': False, 'extraction_confidence': 'medium'},
            'route_to': ['Dietitian', 'Fitness Coach'],
            'health_director_required': True,
            'notes': 'Must update both food and training.'
        }
    },
    {
        'case': 30,
        'message': 'lol',
        'expected': {
            'intent': ['unclear'],
            'extracted': {},
            'route_to': [],
            'health_director_required': False,
            'notes': 'No structured update; clarifier or wait.'
        }
    }
]

(Path(OUT / 'sample_cases.json')).write_text(json.dumps(CASES, indent=2, ensure_ascii=False))
print(json.dumps({'written': str(OUT / 'sample_cases.json'), 'count': len(CASES)}, indent=2))
