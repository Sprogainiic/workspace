from __future__ import annotations

import unittest
from pathlib import Path

from runtime.reactive_session_bridge import process_session_messages, read_bridge_log

BRIDGE_LOG = Path(__file__).resolve().parents[1] / "runtime" / "data" / "ingest" / "reactive_bridge_log.jsonl"
INGEST_LOG = Path(__file__).resolve().parents[1] / "runtime" / "data" / "ingest" / "reactive_ingest_log.jsonl"
SEEN = Path(__file__).resolve().parents[1] / "runtime" / "data" / "ingest" / "reactive_seen.json"
INBOUND = Path(__file__).resolve().parents[1] / "runtime" / "data" / "inbound" / "discord_messages.jsonl"
EVENTS = Path(__file__).resolve().parents[1] / "runtime" / "data" / "events" / "events.jsonl"


class ReactiveSessionBridgeTests(unittest.TestCase):
    def setUp(self):
        for path in [BRIDGE_LOG, INGEST_LOG, SEEN, INBOUND, EVENTS]:
            path.parent.mkdir(parents=True, exist_ok=True)
            if path.exists():
                path.unlink()

    def test_inbound_user_message_forwarded(self):
        results = process_session_messages("agent:health:discord:channel:1491124367638401024", [{
            "role": "user",
            "timestamp": "2026-04-15T10:30:00+03:00",
            "content": [{"type": "text", "text": "I am tired and skipped workout"}],
            "__openclaw": {"id": "m1"},
            "senderLabel": "user1",
        }])
        self.assertEqual(results[0]["bridge_status"], "accepted")

    def test_assistant_system_ignored(self):
        results = process_session_messages("agent:health:discord:channel:1491124367638401024", [
            {"role": "assistant", "timestamp": "2026-04-15T10:30:00+03:00", "content": [{"type": "text", "text": "x"}], "__openclaw": {"id": "a1"}},
            {"role": "system", "timestamp": "2026-04-15T10:31:00+03:00", "content": [{"type": "text", "text": "y"}], "__openclaw": {"id": "s1"}},
        ])
        self.assertEqual(results[0]["bridge_status"], "ignored")
        self.assertEqual(results[1]["bridge_status"], "ignored")

    def test_duplicate_ignored(self):
        messages = [{
            "role": "user",
            "timestamp": "2026-04-15T10:30:00+03:00",
            "content": [{"type": "text", "text": "I am tired and skipped workout"}],
            "__openclaw": {"id": "m1"},
            "senderLabel": "user1",
        }]
        process_session_messages("agent:health:discord:channel:1491124367638401024", messages)
        results = process_session_messages("agent:health:discord:channel:1491124367638401024", messages)
        self.assertEqual(results[0]["bridge_status"], "ignored")

    def test_malformed_rejected(self):
        results = process_session_messages("agent:health:discord:channel:1491124367638401024", [{
            "role": "user",
            "timestamp": "2026-04-15T10:30:00+03:00",
            "content": [],
            "__openclaw": {"id": "m1"},
            "senderLabel": "user1",
        }])
        self.assertEqual(results[0]["bridge_status"], "ignored")

    def test_bridge_log_written(self):
        process_session_messages("agent:health:discord:channel:1491124367638401024", [{
            "role": "user",
            "timestamp": "2026-04-15T10:30:00+03:00",
            "content": [{"type": "text", "text": "I am tired and skipped workout"}],
            "__openclaw": {"id": "m1"},
            "senderLabel": "user1",
        }])
        rows = read_bridge_log()
        self.assertEqual(rows[0]["bridge_status"], "accepted")


if __name__ == "__main__":
    unittest.main()
