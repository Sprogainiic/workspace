from __future__ import annotations

import json
import unittest
from pathlib import Path

from runtime.reactive_reply import build_reactive_reply
from runtime.event_store import EVENTS
from runtime.snapshot_updater import SNAP, DEFAULT, update_snapshot


class ReactiveReplyTests(unittest.TestCase):
    def setUp(self):
        EVENTS.parent.mkdir(parents=True, exist_ok=True)
        SNAP.parent.mkdir(parents=True, exist_ok=True)
        if EVENTS.exists():
            EVENTS.unlink()
        SNAP.write_text(json.dumps(DEFAULT, indent=2, ensure_ascii=False), encoding='utf-8')
        rows = [
            {
                'event_id': 'strava_abc_activity',
                'timestamp': '2026-04-16T14:01:37Z',
                'event_type': 'activity_logged',
                'source_message_id': 'strava:abc',
                'facts': {'source': 'strava', 'name': 'Afternoon Ride', 'sport_type': 'Ride', 'distance_m': 40609.2, 'duration_sec': 7667, 'average_heartrate': 139.2},
                'confidence': 'high',
                'ambiguities': [],
                'write_scope': 'canonical',
                'safe_to_write': True,
            },
            {
                'event_id': 'strava_abc_load',
                'timestamp': '2026-04-16T14:01:37Z',
                'event_type': 'training_load_signal',
                'source_message_id': 'strava:abc',
                'facts': {'load_level': 'high', 'duration_sec': 7667, 'average_heartrate': 139.2},
                'confidence': 'medium',
                'ambiguities': [],
                'write_scope': 'canonical',
                'safe_to_write': True,
            },
        ]
        EVENTS.write_text('\n'.join(json.dumps(r, ensure_ascii=False) for r in rows) + '\n', encoding='utf-8')
        update_snapshot(rows)

    def test_strava_question_uses_recent_runtime_data(self):
        result = build_reactive_reply('Do you see my yesterday\'s Strava ride now?', 'm1', '2026-04-17T17:12:00+03:00')
        self.assertEqual(result['status'], 'ok')
        self.assertTrue(result['used_recent_strava'])
        self.assertIn('Yes', result['message_text'])
        self.assertIn('Strava', result['message_text'])
        self.assertNotIn('screenshot', result['message_text'].lower())


if __name__ == '__main__':
    unittest.main()
