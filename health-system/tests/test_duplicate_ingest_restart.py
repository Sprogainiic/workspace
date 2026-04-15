from __future__ import annotations

import unittest
from pathlib import Path

from runtime.reactive_session_bridge_runner import run_once

ROOT = Path(__file__).resolve().parents[1]
CHECKPOINT = ROOT / "runtime" / "data" / "reactive_bridge_checkpoint.json"
BRIDGE_LOG = ROOT / "runtime" / "data" / "ingest" / "reactive_bridge_log.jsonl"
INGEST_LOG = ROOT / "runtime" / "data" / "ingest" / "reactive_ingest_log.jsonl"
SEEN = ROOT / "runtime" / "data" / "ingest" / "reactive_seen.json"
INBOUND = ROOT / "runtime" / "data" / "inbound" / "discord_messages.jsonl"
EVENTS = ROOT / "runtime" / "data" / "events" / "events.jsonl"


class DuplicateIngestRestartTests(unittest.TestCase):
    def setUp(self):
        for path in [CHECKPOINT, BRIDGE_LOG, INGEST_LOG, SEEN, INBOUND, EVENTS]:
            path.parent.mkdir(parents=True, exist_ok=True)
            if path.exists():
                path.unlink()

    def test_restart_same_message_not_ingested_twice(self):
        def fetcher(**kwargs):
            return {"messages": [{
                "role": "user",
                "timestamp": "2026-04-15T10:30:00+03:00",
                "content": [{"type": "text", "text": "I am tired and skipped workout"}],
                "__openclaw": {"id": "m-restart"},
                "senderLabel": "user1",
            }]}
        first = run_once("agent:health:discord:channel:1491124367638401024", fetcher)
        second = run_once("agent:health:discord:channel:1491124367638401024", fetcher)
        self.assertEqual(first["processed"], 1)
        self.assertEqual(second["processed"], 0)


if __name__ == "__main__":
    unittest.main()
