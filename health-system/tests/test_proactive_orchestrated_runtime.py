from __future__ import annotations

import unittest
from datetime import datetime
from pathlib import Path

from runtime.chat_flow import evaluate_nudge_slot
from runtime.nudge_log import read_nudge_log

LOG_PATH = Path(__file__).resolve().parents[1] / "runtime" / "data" / "nudge_logs" / "nudge_log.jsonl"


def ts(value: str) -> datetime:
    return datetime.fromisoformat(value)


class ProactiveOrchestratedRuntimeTests(unittest.TestCase):
    def setUp(self):
        if LOG_PATH.exists():
            LOG_PATH.unlink()
        self.snapshot = {
            "state": {
                "fatigue": {"value": "high"},
                "motivation": {"value": "low"},
                "behavior_state": {"value": "fragile"},
                "recent_misses": 2,
            },
            "simplification_level": "normal",
        }

    def test_orchestrated_runtime_routes_health_director_and_specialists(self):
        result = evaluate_nudge_slot(
            current_snapshot=self.snapshot,
            todays_events=[],
            daily_summary={},
            weekly_summary={},
            recent_user_activity=[],
            current_slot="afternoon_check",
            now=ts("2026-04-15T15:30:00+03:00"),
            outbound_channel="test",
            recipient_id="user-123",
            sent_nudges_today=[],
            state_source="test_fixture",
            allow_test_fixture=True,
            activity_source="persisted",
        )
        self.assertTrue(result["selection"]["send"])
        self.assertEqual(result["advisor_runtime"]["runtime_mode"], "orchestrated")
        self.assertIn("Health Director", result["advisor_runtime"]["routing"])
        self.assertIn("Fitness Coach", result["advisor_runtime"]["routing"])
        self.assertIn("Consistency Coach", result["advisor_runtime"]["routing"])
        self.assertEqual(result["transport_result"]["message_text"], result["advisor_runtime"]["message_text"])
        rows = read_nudge_log()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["runtime_mode"], "orchestrated")
        self.assertIn("Health Director", rows[0]["routing"])
        self.assertGreater(rows[0]["advisor_tokens_in"], 0)
        self.assertGreater(rows[0]["advisor_tokens_out"], 0)


if __name__ == "__main__":
    unittest.main()
