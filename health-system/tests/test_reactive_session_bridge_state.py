from __future__ import annotations

import json
import unittest
from pathlib import Path

from runtime.reactive_session_bridge_state import load_bridge_checkpoint, save_bridge_checkpoint
from runtime.reactive_session_bridge_runner import run_once

ROOT = Path(__file__).resolve().parents[1]
CHECKPOINT = ROOT / 'runtime' / 'data' / 'reactive_bridge_checkpoint.json'


class ReactiveSessionBridgeStateTests(unittest.TestCase):
    def setUp(self):
        CHECKPOINT.parent.mkdir(parents=True, exist_ok=True)
        if CHECKPOINT.exists():
            CHECKPOINT.unlink()

    def test_checkpoint_roundtrip_uses_cursor_fields(self):
        save_bridge_checkpoint('s1', '2026-04-17T17:14:46Z', 'm42', ['m1', 'm2', 'm42'])
        data = load_bridge_checkpoint()
        self.assertEqual(data['session_key'], 's1')
        self.assertEqual(data['last_processed_timestamp'], '2026-04-17T17:14:46Z')
        self.assertEqual(data['last_processed_message_id'], 'm42')
        self.assertEqual(data['recent_message_ids'][-1], 'm42')

    def test_run_once_only_processes_newer_messages(self):
        calls = []
        def fetcher(**kwargs):
            return {
                'messages': [
                    {
                        'role': 'user',
                        'timestamp': '2026-04-17T17:14:46Z',
                        'content': [{'type': 'text', 'text': 'older'}],
                        '__openclaw': {'id': 'm42'},
                        'senderLabel': 'u',
                    },
                    {
                        'role': 'user',
                        'timestamp': '2026-04-17T17:15:00Z',
                        'content': [{'type': 'text', 'text': 'newer'}],
                        '__openclaw': {'id': 'm43'},
                        'senderLabel': 'u',
                    },
                ]
            }

        save_bridge_checkpoint('sess', '2026-04-17T17:14:46Z', 'm42', ['m42'])
        result = run_once('sess', fetcher, reply_sender=lambda **kwargs: calls.append(kwargs))
        self.assertEqual(result['processed'], 1)
        self.assertEqual(len(calls), 1)
        data = load_bridge_checkpoint()
        self.assertEqual(data['last_processed_message_id'], 'm43')


if __name__ == '__main__':
    unittest.main()
