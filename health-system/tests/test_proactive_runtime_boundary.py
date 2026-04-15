from __future__ import annotations

import unittest
from datetime import datetime
from pathlib import Path

from runtime.chat_flow import evaluate_nudge_slot
from runtime.nudge_log import read_nudge_log

LOG_PATH = Path(__file__).resolve().parents[1] / "runtime" / "data" / "nudge_logs" / "nudge_log.jsonl"


def ts(value: str) -> datetime:
    return datetime.fromisoformat(value)


class ProactiveRuntimeBoundaryTests(unittest.TestCase):
    def setUp(self):
        if LOG_PATH.exists():
            LOG_PATH.unlink()
        self.snapshot = {
            "state": {
                "fatigue": {"value": "medium"},
                "motivation": {"value": None},
                "behavior_state": {"value": None},
                "recent_misses": 0,
            },
            "simplification_level": "normal",
        }

    def test_boundary_flow_runs_selector_history_advisor_transport_and_log(self):
        result = evaluate_nudge_slot(
            current_snapshot=self.snapshot,
            todays_events=[],
            daily_summary={},
            weekly_summary={},
            recent_user_activity=[],
            current_slot="lunch_check",
            now=ts("2026-04-15T12:30:00+03:00"),
            outbound_channel="test",
            recipient_id="user-123",
            sent_nudges_today=[],
            state_source="test_fixture",
            allow_test_fixture=True,
        )
        self.assertTrue(result["evaluated"])
        self.assertTrue(result["selection"]["send"])
        self.assertEqual(result["state_source"], "test_fixture")
        self.assertEqual(result["advisor_runtime"]["runtime_mode"], "orchestrated")
        self.assertTrue(result["advisor_runtime"]["approved"])
        self.assertEqual(result["transport_result"]["channel"], "test")
        self.assertEqual(result["transport_result"]["recipient_id"], "user-123")
        self.assertTrue(result["transport_result"]["sent"])
        rows = read_nudge_log()
        self.assertEqual(len(rows), 1)
        self.assertTrue(rows[0]["send"])
        self.assertEqual(rows[0]["slot"], "lunch_check")
        self.assertTrue(rows[0]["message_fingerprint"])
        self.assertGreater(rows[0]["tokens_in"], 0)
        self.assertGreater(rows[0]["tokens_out"], 0)
        self.assertEqual(rows[0]["runtime_mode"], "orchestrated")


if __name__ == "__main__":
    unittest.main()
