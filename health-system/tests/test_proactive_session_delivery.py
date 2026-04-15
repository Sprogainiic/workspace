from __future__ import annotations

import unittest
from datetime import datetime
from pathlib import Path

from runtime.chat_flow import evaluate_nudge_slot
from runtime.config import OPENCLAW_HEALTH_SESSION_KEY
from runtime.nudge_log import read_nudge_log

LOG_PATH = Path(__file__).resolve().parents[1] / "runtime" / "data" / "nudge_logs" / "nudge_log.jsonl"


def ts(value: str) -> datetime:
    return datetime.fromisoformat(value)


class ProactiveSessionDeliveryTests(unittest.TestCase):
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

    def test_success_path_logs_sent_to_openclaw_session(self):
        calls = []
        def fake_sender(**kwargs):
            calls.append(kwargs)
            return {"ok": True}

        result = evaluate_nudge_slot(
            current_snapshot=self.snapshot,
            todays_events=[],
            daily_summary={},
            recent_user_activity=[],
            current_slot="lunch_check",
            now=ts("2026-04-15T12:30:00+03:00"),
            outbound_channel="openclaw_session",
            recipient_id="ignored",
            sent_nudges_today=[],
            state_source="test_fixture",
            allow_test_fixture=True,
            activity_source="persisted",
            session_sender=fake_sender,
            session_key=OPENCLAW_HEALTH_SESSION_KEY,
        )
        self.assertTrue(result["transport_result"]["sent"])
        self.assertEqual(result["transport_result"]["delivery_status"], "sent")
        rows = read_nudge_log()
        self.assertEqual(rows[0]["transport"], "openclaw_session")
        self.assertEqual(rows[0]["session_key"], OPENCLAW_HEALTH_SESSION_KEY)
        self.assertEqual(rows[0]["delivery_status"], "sent")
        self.assertEqual(len(calls), 1)

    def test_failure_path_logs_failed_delivery(self):
        def fake_sender(**kwargs):
            raise RuntimeError("session failed")

        result = evaluate_nudge_slot(
            current_snapshot=self.snapshot,
            todays_events=[],
            daily_summary={},
            recent_user_activity=[],
            current_slot="lunch_check",
            now=ts("2026-04-15T12:30:00+03:00"),
            outbound_channel="openclaw_session",
            recipient_id="ignored",
            sent_nudges_today=[],
            state_source="test_fixture",
            allow_test_fixture=True,
            activity_source="persisted",
            session_sender=fake_sender,
            session_key=OPENCLAW_HEALTH_SESSION_KEY,
        )
        self.assertFalse(result["transport_result"]["sent"])
        self.assertEqual(result["transport_result"]["delivery_status"], "failed")
        rows = read_nudge_log()
        self.assertEqual(rows[0]["delivery_status"], "failed")
        self.assertEqual(rows[0]["transport"], "openclaw_session")


if __name__ == "__main__":
    unittest.main()
