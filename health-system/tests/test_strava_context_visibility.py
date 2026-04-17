from __future__ import annotations

import json
import unittest
from pathlib import Path

from runtime.context_loader import load_context
from runtime.snapshot_updater import update_snapshot, SNAP
from runtime.event_store import EVENTS


class StravaContextVisibilityTests(unittest.TestCase):
    def setUp(self):
        EVENTS.parent.mkdir(parents=True, exist_ok=True)
        SNAP.parent.mkdir(parents=True, exist_ok=True)
        if EVENTS.exists():
            EVENTS.unlink()
        if SNAP.exists():
            SNAP.unlink()

    def test_medium_context_includes_recent_strava_when_present(self):
        rows = [
            {
                'event_id': 'strava_x_activity',
                'timestamp': '2026-04-16T14:01:37Z',
                'event_type': 'activity_logged',
                'source_message_id': 'strava:x',
                'facts': {'source': 'strava', 'name': 'Ride', 'sport_type': 'Ride'},
                'confidence': 'high',
                'ambiguities': [],
                'write_scope': 'canonical',
                'safe_to_write': True,
            },
            {
                'event_id': 'strava_x_load',
                'timestamp': '2026-04-16T14:01:37Z',
                'event_type': 'training_load_signal',
                'source_message_id': 'strava:x',
                'facts': {'load_level': 'high', 'duration_sec': 5000},
                'confidence': 'medium',
                'ambiguities': [],
                'write_scope': 'canonical',
                'safe_to_write': True,
            },
        ]
        EVENTS.write_text('\n'.join(json.dumps(r) for r in rows) + '\n', encoding='utf-8')
        update_snapshot(rows)
        ctx = load_context(decision_complexity='medium')
        self.assertIn('recent_strava', ctx['context_payload'])
        self.assertTrue(ctx['context_payload']['recent_strava'])
        self.assertEqual(ctx['context_payload']['snapshot']['state']['last_training_event_at'], '2026-04-16T14:01:37Z')


if __name__ == '__main__':
    unittest.main()
