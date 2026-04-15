from __future__ import annotations

import json
import unittest
from pathlib import Path

from runtime.reactive_session_bridge_runner import run_once, run_loop

CHECKPOINT = Path(__file__).resolve().parents[1] / "runtime" / "data" / "reactive_bridge_checkpoint.json"
BRIDGE_LOG = Path(__file__).resolve().parents[1] / "runtime" / "data" / "ingest" / "reactive_bridge_log.jsonl"
INGEST_LOG = Path(__file__).resolve().parents[1] / "runtime" / "data" / "ingest" / "reactive_ingest_log.jsonl"
SEEN = Path(__file__).resolve().parents[1] / "runtime" / "data" / "ingest" / "reactive_seen.json"
INBOUND = Path(__file__).resolve().parents[1] / "runtime" / "data" / "inbound" / "discord_messages.jsonl"
EVENTS = Path(__file__).resolve().parents[1] / "runtime" / "data" / "events" / "events.jsonl"


class ReactiveSessionBridgeRunnerTests(unittest.TestCase):
    def setUp(self):
        for path in [CHECKPOINT, BRIDGE_LOG, INGEST_LOG, SEEN, INBOUND, EVENTS]:
            path.parent.mkdir(parents=True, exist_ok=True)
            if path.exists():
                path.unlink()

    def test_once_mode_processes_one_new_inbound_event(self):
        def fetcher(**kwargs):
            return {"messages": [{
                "role": "user",
                "timestamp": "2026-04-15T10:30:00+03:00",
                "content": [{"type": "text", "text": "I am tired and skipped workout"}],
                "__openclaw": {"id": "m1"},
                "senderLabel": "user1",
            }]}
        result = run_once("agent:health:discord:channel:1491124367638401024", fetcher)
        self.assertEqual(result["processed"], 1)
        self.assertEqual(result["results"][0]["bridge_status"], "accepted")

    def test_loop_mode_can_be_simulated(self):
        calls = [
            {"messages": [{"role": "user", "timestamp": "2026-04-15T10:30:00+03:00", "content": [{"type": "text", "text": "I am tired and skipped workout"}], "__openclaw": {"id": "m1"}, "senderLabel": "user1"}]},
            {"messages": []},
        ]
        def fetcher(**kwargs):
            return calls.pop(0)
        results = run_loop("agent:health:discord:channel:1491124367638401024", fetcher, poll_seconds=0, max_iterations=2)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["processed"], 1)

    def test_checkpoint_prevents_reprocessing(self):
        def fetcher(**kwargs):
            return {"messages": [{
                "role": "user",
                "timestamp": "2026-04-15T10:30:00+03:00",
                "content": [{"type": "text", "text": "I am tired and skipped workout"}],
                "__openclaw": {"id": "m1"},
                "senderLabel": "user1",
            }]}
        run_once("agent:health:discord:channel:1491124367638401024", fetcher)
        result = run_once("agent:health:discord:channel:1491124367638401024", fetcher)
        self.assertEqual(result["processed"], 0)

    def test_assistant_system_events_ignored(self):
        def fetcher(**kwargs):
            return {"messages": [
                {"role": "assistant", "timestamp": "2026-04-15T10:30:00+03:00", "content": [{"type": "text", "text": "x"}], "__openclaw": {"id": "a1"}},
                {"role": "system", "timestamp": "2026-04-15T10:31:00+03:00", "content": [{"type": "text", "text": "y"}], "__openclaw": {"id": "s1"}},
            ]}
        result = run_once("agent:health:discord:channel:1491124367638401024", fetcher)
        self.assertEqual(result["processed"], 0)


if __name__ == "__main__":
    unittest.main()
