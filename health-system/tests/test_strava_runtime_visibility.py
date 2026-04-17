from __future__ import annotations

import json
import unittest
from datetime import datetime
from pathlib import Path

from runtime.state_loader import load_runtime_state
from runtime.snapshot_updater import SNAP
from runtime.event_store import EVENTS

ROOT = Path(__file__).resolve().parents[1]
STRAVA_RECENT = ROOT / 'runtime' / 'data' / 'strava' / 'recent_activities.json'


class StravaRuntimeVisibilityTests(unittest.TestCase):
    def setUp(self):
        EVENTS.parent.mkdir(parents=True, exist_ok=True)
        SNAP.parent.mkdir(parents=True, exist_ok=True)
        STRAVA_RECENT.parent.mkdir(parents=True, exist_ok=True)
        if EVENTS.exists():
            EVENTS.unlink()
        if SNAP.exists():
            SNAP.unlink()

    def test_snapshot_state_can_expose_strava_training_load(self):
        EVENTS.write_text(
            json.dumps({
                'event_id': 'strava_1_load',
                'timestamp': '2026-04-17T09:00:00+03:00',
                'event_type': 'training_load_signal',
                'source_message_id': 'strava:1',
                'facts': {'load_level': 'medium', 'duration_sec': 3600, 'average_heartrate': 130, 'suffer_score': 60},
                'confidence': 'medium',
                'ambiguities': [],
                'write_scope': 'canonical',
                'safe_to_write': True,
            }) + '\n',
            encoding='utf-8'
        )
        SNAP.write_text(json.dumps({
            'state': {
                'fatigue': {'value': None},
                'motivation': {'value': None},
                'behavior_state': {'value': None},
                'recent_misses': 0,
                'training_load': {
                    'value': 'medium',
                    'confidence': 'medium',
                    'updated_at': '2026-04-17T09:00:00+03:00',
                    'evidence_event_ids': ['strava_1_load'],
                    'staleness': 'fresh'
                }
            },
            'simplification_level': 'normal'
        }), encoding='utf-8')

        state = load_runtime_state(datetime.fromisoformat('2026-04-17T12:00:00+03:00'))
        self.assertEqual(state['snapshot']['state']['training_load']['value'], 'medium')
        self.assertEqual(len(state['today_events']), 1)
        self.assertEqual(state['today_events'][0]['event_id'], 'strava_1_load')


if __name__ == '__main__':
    unittest.main()
