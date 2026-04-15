from __future__ import annotations

import unittest
from datetime import datetime
from pathlib import Path

from runtime.chat_flow import evaluate_nudge_slot
from runtime.nudge_log import read_nudge_log

ROOT = Path(__file__).resolve().parents[1]
CHAT_FLOW_PATH = ROOT / "runtime" / "chat_flow.py"
LOG_PATH = ROOT / "runtime" / "data" / "nudge_logs" / "nudge_log.jsonl"


def ts(value: str) -> datetime:
    return datetime.fromisoformat(value)


class AdvisorRuntimeContractTests(unittest.TestCase):
    def setUp(self):
        if LOG_PATH.exists():
            LOG_PATH.unlink()
        self.snapshot = {
            "state": {
                "fatigue": {"value": None},
                "motivation": {"value": None},
                "behavior_state": {"value": None},
                "recent_misses": 0,
            },
            "simplification_level": "normal",
        }

    def test_chat_flow_does_not_inline_build_final_message(self):
        text = CHAT_FLOW_PATH.read_text(encoding="utf-8")
        self.assertNotIn("Quick check:", text)
        self.assertNotIn("Quick check-in:", text)
        self.assertNotIn("Quick reset option:", text)

    def test_all_proactive_message_text_comes_from_advisor_runtime_and_logs_runtime_mode(self):
        result = evaluate_nudge_slot(
            current_snapshot=self.snapshot,
            todays_events=[],
            daily_summary={},
            recent_user_activity=[],
            current_slot="lunch_check",
            now=ts("2026-04-15T12:30:00+03:00"),
            outbound_channel="test",
            recipient_id="user-123",
            sent_nudges_today=[],
            state_source="test_fixture",
            allow_test_fixture=True,
        )
        self.assertEqual(result["transport_result"]["message_text"], result["advisor_runtime"]["message_text"])
        self.assertEqual(result["advisor_runtime"]["runtime_mode"], "orchestrated")
        rows = read_nudge_log()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["runtime_mode"], result["advisor_runtime"]["runtime_mode"])


if __name__ == "__main__":
    unittest.main()
