from __future__ import annotations

import unittest
from pathlib import Path

from runtime.reactive_session_bridge_launcher import launch_bridge

CHECKPOINT = Path(__file__).resolve().parents[1] / "runtime" / "data" / "reactive_bridge_checkpoint.json"
BRIDGE_LOG = Path(__file__).resolve().parents[1] / "runtime" / "data" / "ingest" / "reactive_bridge_log.jsonl"
PRE_INGEST_LOG = Path(__file__).resolve().parents[1] / "runtime" / "data" / "ingest" / "reactive_bridge_pre_ingest.jsonl"
INGEST_LOG = Path(__file__).resolve().parents[1] / "runtime" / "data" / "ingest" / "reactive_ingest_log.jsonl"
SEEN = Path(__file__).resolve().parents[1] / "runtime" / "data" / "ingest" / "reactive_seen.json"
INBOUND = Path(__file__).resolve().parents[1] / "runtime" / "data" / "inbound" / "discord_messages.jsonl"
EVENTS = Path(__file__).resolve().parents[1] / "runtime" / "data" / "events" / "events.jsonl"


class ReactiveSessionBridgeLauncherTests(unittest.TestCase):
    def setUp(self):
        for path in [CHECKPOINT, BRIDGE_LOG, PRE_INGEST_LOG, INGEST_LOG, SEEN, INBOUND, EVENTS]:
            path.parent.mkdir(parents=True, exist_ok=True)
            if path.exists():
                path.unlink()

    def test_test_mode_still_allows_injected_fetcher(self):
        def fetcher(**kwargs):
            return {"messages": [
                {"role": "assistant", "timestamp": "2026-04-15T10:30:00+03:00", "content": [{"type": "text", "text": "x"}], "__openclaw": {"id": "a1"}},
                {"role": "user", "timestamp": "2026-04-15T10:31:00+03:00", "content": [{"type": "text", "text": "I am tired and skipped workout"}], "__openclaw": {"id": "m1"}, "senderLabel": "user1"},
            ]}
        result = launch_bridge("agent:health:discord:channel:1491124367638401024", "once", history_fetcher=fetcher, runtime_mode="test")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["processed"], 1)
        self.assertEqual(result["accepted"], 1)
        self.assertTrue(PRE_INGEST_LOG.exists())

    def test_prod_mode_uses_real_boundary_client(self):
        result = launch_bridge(
            "agent:health:discord:channel:1491124367638401024",
            "once",
            runtime_mode="prod",
            sessions_history_tool=lambda **kwargs: {"messages": [{"role": "user", "timestamp": "2026-04-15T10:31:00+03:00", "content": [{"type": "text", "text": "I am tired and skipped workout"}], "__openclaw": {"id": "m1"}, "senderLabel": "user1"}]}
        )
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["processed"], 1)

    def test_prod_mode_fails_cleanly_if_client_unavailable(self):
        result = launch_bridge("agent:health:discord:channel:1491124367638401024", "once", runtime_mode="prod", sessions_history_tool=None)
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["failure_point"], "session_history_unavailable")

    def test_prod_mode_does_not_treat_fake_empty_result_as_success(self):
        result = launch_bridge("agent:health:discord:channel:1491124367638401024", "once", runtime_mode="prod", sessions_history_tool=lambda **kwargs: {"bad": []})
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["failure_point"], "session_history_unavailable")


if __name__ == "__main__":
    unittest.main()
