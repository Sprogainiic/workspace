from __future__ import annotations

import unittest
from datetime import datetime
from pathlib import Path

from runtime.chat_flow import evaluate_nudge_slot
from runtime.nudge_log import log_nudge_decision, read_nudge_log
from runtime.nudge_state_loader import load_sent_nudges_today

LOG_PATH = Path(__file__).resolve().parents[1] / "runtime" / "data" / "nudge_logs" / "nudge_log.jsonl"


def ts(value: str) -> datetime:
    return datetime.fromisoformat(value)


class NudgeLogReplayTests(unittest.TestCase):
    def setUp(self):
        if LOG_PATH.exists():
            LOG_PATH.unlink()
        log_nudge_decision({
            "timestamp": "2026-04-15T16:00:00+03:00",
            "slot": "lunch_check",
            "evaluated": True,
            "send": True,
            "skip_reason": None,
            "nudge_type": "reminder",
            "domain": "nutrition",
            "tokens_in": 10,
            "tokens_out": 8,
            "message_intent": "reminder",
            "fingerprint": "fp-lunch-1",
            "message_fingerprint": "fp-lunch-1",
        })
        log_nudge_decision({
            "timestamp": "2026-04-15T17:15:00+03:00",
            "slot": "afternoon_check",
            "evaluated": True,
            "send": True,
            "skip_reason": None,
            "nudge_type": "check_in",
            "domain": "behavior",
            "tokens_in": 11,
            "tokens_out": 9,
            "message_intent": "check_in",
            "fingerprint": "fp-behavior-2",
            "message_fingerprint": "fp-behavior-2",
        })

    def test_same_day_reload_suppresses_new_dinner_nutrition_nudge_without_manual_history(self):
        loaded = load_sent_nudges_today(ts("2026-04-15T18:30:00+03:00"))
        self.assertEqual(len(loaded["sent_nudges_today"]), 2)
        result = evaluate_nudge_slot(
            current_snapshot={
                "state": {
                    "fatigue": {"value": None},
                    "motivation": {"value": None},
                    "behavior_state": {"value": None},
                    "recent_misses": 0,
                },
                "simplification_level": "normal",
            },
            todays_events=[],
            daily_summary={},
            recent_user_activity=[],
            current_slot="dinner_check",
            now=ts("2026-04-15T18:30:00+03:00"),
            sent_nudges_today=loaded["sent_nudges_today"],
            state_source="test_fixture",
            allow_test_fixture=True,
        )
        self.assertFalse(result["selection"]["send"])
        self.assertEqual(result["selection"]["skip_reason"], "spam_guard")
        rows = read_nudge_log()
        self.assertEqual(len(rows), 3)
        self.assertFalse(rows[-1]["send"])
        self.assertEqual(rows[-1]["skip_reason"], "spam_guard")
        self.assertEqual(rows[-1]["state_source"], "test_fixture")


if __name__ == "__main__":
    unittest.main()
