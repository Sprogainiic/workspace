from __future__ import annotations

import unittest
from pathlib import Path

from runtime.reactive_session_ingest import ingest_reactive_session_event
from runtime.reactive_ingest_log import read_reactive_ingest_log
from runtime.user_activity_loader import load_recent_user_activity
from datetime import datetime

INBOUND = Path(__file__).resolve().parents[1] / "runtime" / "data" / "inbound" / "discord_messages.jsonl"
SEEN = Path(__file__).resolve().parents[1] / "runtime" / "data" / "ingest" / "reactive_seen.json"
INGEST_LOG = Path(__file__).resolve().parents[1] / "runtime" / "data" / "ingest" / "reactive_ingest_log.jsonl"
EVENTS = Path(__file__).resolve().parents[1] / "runtime" / "data" / "events" / "events.jsonl"


class ReactiveSessionIngestTests(unittest.TestCase):
    def setUp(self):
        for path in [INBOUND, SEEN, INGEST_LOG, EVENTS]:
            path.parent.mkdir(parents=True, exist_ok=True)
            if path.exists():
                path.unlink()

    def test_valid_inbound_message_accepted(self):
        result = ingest_reactive_session_event({
            "session_key": "agent:health:discord:channel:1491124367638401024",
            "event": {
                "message_text": "I am tired and skipped workout",
                "user_id": "u1",
                "message_id": "m1",
                "timestamp": "2026-04-15T10:30:00+03:00",
                "source_type": "discord_channel",
            },
        })
        self.assertEqual(result["status"], "accepted")
        self.assertIn("Fitness Coach", result["routing"])
        self.assertIn("Consistency Coach", result["routing"])

    def test_duplicate_message_ignored(self):
        payload = {
            "session_key": "agent:health:discord:channel:1491124367638401024",
            "event": {
                "message_text": "I am tired and skipped workout",
                "user_id": "u1",
                "message_id": "m1",
                "timestamp": "2026-04-15T10:30:00+03:00",
                "source_type": "discord_channel",
            },
        }
        ingest_reactive_session_event(payload)
        result = ingest_reactive_session_event(payload)
        self.assertEqual(result["status"], "ignored")

    def test_malformed_inbound_message_rejected(self):
        result = ingest_reactive_session_event({"session_key": "x", "event": {"message_text": "bad"}})
        self.assertEqual(result["status"], "failed")

    def test_recent_activity_loader_sees_ingested_discord_message(self):
        ingest_reactive_session_event({
            "session_key": "agent:health:discord:channel:1491124367638401024",
            "event": {
                "message_text": "I am tired and skipped workout",
                "user_id": "u1",
                "message_id": "m1",
                "timestamp": "2026-04-15T10:30:00+03:00",
                "source_type": "discord_channel",
            },
        })
        activity = load_recent_user_activity(datetime.fromisoformat("2026-04-15T10:40:00+03:00"))
        self.assertEqual(activity["activity_source"], "persisted")
        self.assertEqual(activity["recent_user_activity"][0]["source"], "discord_inbound")

    def test_ingest_log_written(self):
        ingest_reactive_session_event({
            "session_key": "agent:health:discord:channel:1491124367638401024",
            "event": {
                "message_text": "I am tired and skipped workout",
                "user_id": "u1",
                "message_id": "m1",
                "timestamp": "2026-04-15T10:30:00+03:00",
                "source_type": "discord_channel",
            },
        })
        rows = read_reactive_ingest_log()
        self.assertEqual(rows[0]["status"], "accepted")


if __name__ == "__main__":
    unittest.main()
