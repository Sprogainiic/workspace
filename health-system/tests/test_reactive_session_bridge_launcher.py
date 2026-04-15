from __future__ import annotations

import unittest
from pathlib import Path

from runtime.reactive_session_bridge_launcher import launch_bridge

CHECKPOINT = Path(__file__).resolve().parents[1] / "runtime" / "data" / "reactive_bridge_checkpoint.json"
BRIDGE_LOG = Path(__file__).resolve().parents[1] / "runtime" / "data" / "ingest" / "reactive_bridge_log.jsonl"
INGEST_LOG = Path(__file__).resolve().parents[1] / "runtime" / "data" / "ingest" / "reactive_ingest_log.jsonl"
SEEN = Path(__file__).resolve().parents[1] / "runtime" / "data" / "ingest" / "reactive_seen.json"
INBOUND = Path(__file__).resolve().parents[1] / "runtime" / "data" / "inbound" / "discord_messages.jsonl"
EVENTS = Path(__file__).resolve().parents[1] / "runtime" / "data" / "events" / "events.jsonl"


class ReactiveSessionBridgeLauncherTests(unittest.TestCase):
    def setUp(self):
        for path in [CHECKPOINT, BRIDGE_LOG, INGEST_LOG, SEEN, INBOUND, EVENTS]:
            path.parent.mkdir(parents=True, exist_ok=True)
            if path.exists():
                path.unlink()

    def test_once_mode_with_mixed_events(self):
        def fetcher(**kwargs):
            return {"messages": [
                {"role": "assistant", "timestamp": "2026-04-15T10:30:00+03:00", "content": [{"type": "text", "text": "x"}], "__openclaw": {"id": "a1"}},
                {"role": "user", "timestamp": "2026-04-15T10:31:00+03:00", "content": [{"type": "text", "text": "I am tired and skipped workout"}], "__openclaw": {"id": "m1"}, "senderLabel": "user1"},
            ]}
        result = launch_bridge("agent:health:discord:channel:1491124367638401024", "once", fetcher)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["processed"], 1)
        self.assertEqual(result["accepted"], 1)

    def test_loop_mode_can_be_simulated(self):
        calls = [
            {"messages": [{"role": "user", "timestamp": "2026-04-15T10:31:00+03:00", "content": [{"type": "text", "text": "I am tired and skipped workout"}], "__openclaw": {"id": "m1"}, "senderLabel": "user1"}]},
            {"messages": []},
        ]
        def fetcher(**kwargs):
            return calls.pop(0)
        result = launch_bridge("agent:health:discord:channel:1491124367638401024", "loop", fetcher, poll_seconds=0, max_iterations=2)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["processed"], 1)

    def test_missing_session_key_fails(self):
        result = launch_bridge("", "once", lambda **kwargs: {"messages": []})
        self.assertEqual(result["status"], "failed")

    def test_tool_failure_fails_cleanly(self):
        def fetcher(**kwargs):
            raise RuntimeError("tool failed")
        result = launch_bridge("agent:health:discord:channel:1491124367638401024", "once", fetcher)
        self.assertEqual(result["status"], "failed")


if __name__ == "__main__":
    unittest.main()
