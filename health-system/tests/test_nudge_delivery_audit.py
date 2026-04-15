from __future__ import annotations

import unittest
from datetime import datetime
from pathlib import Path

from runtime.chat_flow import evaluate_nudge_slot
from runtime.nudge_delivery_audit import read_delivery_audit

AUDIT_PATH = Path(__file__).resolve().parents[1] / "runtime" / "data" / "nudge_logs" / "delivery_audit.jsonl"


def ts(value: str) -> datetime:
    return datetime.fromisoformat(value)


class NudgeDeliveryAuditTests(unittest.TestCase):
    def setUp(self):
        if AUDIT_PATH.exists():
            AUDIT_PATH.unlink()
        self.snapshot = {
            "state": {
                "fatigue": {"value": None},
                "motivation": {"value": None},
                "behavior_state": {"value": None},
                "recent_misses": 0,
            },
            "simplification_level": "normal",
        }

    def test_successful_send_writes_delivery_audit(self):
        result = evaluate_nudge_slot(
            current_snapshot=self.snapshot,
            todays_events=[],
            daily_summary={},
            weekly_summary={},
            recent_user_activity=[],
            current_slot="evening_wrap_up",
            now=ts("2026-04-15T20:30:00+03:00"),
            outbound_channel="test",
            recipient_id="user-123",
            sent_nudges_today=[],
            state_source="test_fixture",
            allow_test_fixture=True,
        )
        self.assertTrue(result["selection"]["send"])
        rows = read_delivery_audit()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["slot"], "evening_wrap_up")
        self.assertEqual(rows[0]["delivery_status"], "sent")
        self.assertTrue(rows[0]["message_text"])


if __name__ == "__main__":
    unittest.main()
