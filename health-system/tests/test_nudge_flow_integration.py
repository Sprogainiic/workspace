from __future__ import annotations

import unittest
from datetime import datetime
from pathlib import Path

from runtime.chat_flow import evaluate_nudge_slot
from runtime.nudge_cron_bootstrap import local_cron_map
from runtime.nudge_log import read_nudge_log

LOG_PATH = Path(__file__).resolve().parents[1] / "runtime" / "data" / "nudge_logs" / "nudge_log.jsonl"


def ts(value: str) -> datetime:
    return datetime.fromisoformat(value)


class NudgeFlowIntegrationTests(unittest.TestCase):
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

    def test_cron_map_is_explicit(self):
        self.assertEqual(local_cron_map(), {
            "morning_plan_check": "08:05",
            "late_morning_check": "10:45",
            "lunch_check": "12:15",
            "afternoon_check": "15:30",
            "dinner_check": "18:00",
            "evening_wrap_up": "20:00"
        })

    def test_skip_path_logs_recent_activity_suppression(self):
        result = evaluate_nudge_slot(
            current_snapshot=self.snapshot,
            todays_events=[],
            daily_summary={},
            weekly_summary={},
            recent_user_activity=[{"timestamp": "2026-04-15T12:00:00+03:00", "source": "chat", "signal_type": "meal_log", "domain": "nutrition"}],
            current_slot="lunch_check",
            now=ts("2026-04-15T12:20:00+03:00"),
            sent_nudges_today=[],
            state_source="test_fixture",
            allow_test_fixture=True,
            activity_source="persisted",
        )
        self.assertTrue(result["evaluated"])
        self.assertTrue(result["stopped"])
        self.assertEqual(result["selection"], {"send": False, "skip_reason": "recent_user_activity"})
        rows = read_nudge_log()
        self.assertEqual(len(rows), 1)
        self.assertTrue(rows[0]["evaluated"])
        self.assertFalse(rows[0]["send"])
        self.assertEqual(rows[0]["skip_reason"], "recent_user_activity")
        self.assertEqual(rows[0]["tokens_in"], 0)
        self.assertEqual(rows[0]["tokens_out"], 0)
        self.assertEqual(rows[0]["activity_source"], "persisted")
        self.assertEqual(rows[0]["recent_user_activity_count"], 1)

    def test_send_path_reaches_advisor_runtime_and_logs(self):
        result = evaluate_nudge_slot(
            current_snapshot=self.snapshot,
            todays_events=[],
            daily_summary={},
            weekly_summary={},
            recent_user_activity=[],
            current_slot="lunch_check",
            now=ts("2026-04-15T12:30:00+03:00"),
            sent_nudges_today=[],
            state_source="test_fixture",
            allow_test_fixture=True,
            activity_source="missing",
        )
        self.assertTrue(result["evaluated"])
        self.assertTrue(result["selection"]["send"])
        self.assertIn("advisor_runtime", result)
        self.assertTrue(result["advisor_runtime"]["approved"])
        self.assertTrue(result["transport_result"]["sent"])
        rows = read_nudge_log()
        self.assertEqual(len(rows), 1)
        self.assertTrue(rows[0]["send"])
        self.assertIsNone(rows[0]["skip_reason"])
        self.assertEqual(rows[0]["slot"], "lunch_check")
        self.assertEqual(rows[0]["nudge_type"], "reminder")
        self.assertEqual(rows[0]["domain"], "nutrition")
        self.assertTrue(rows[0]["message_fingerprint"])
        self.assertGreater(rows[0]["tokens_in"], 0)
        self.assertGreater(rows[0]["tokens_out"], 0)
        self.assertEqual(rows[0]["activity_source"], "missing")
        self.assertEqual(rows[0]["recent_user_activity_count"], 0)

    def test_quiet_hours_block_end_to_end(self):
        result = evaluate_nudge_slot(
            current_snapshot=self.snapshot,
            todays_events=[],
            daily_summary={},
            weekly_summary={},
            recent_user_activity=[],
            current_slot="morning_plan_check",
            now=ts("2026-04-15T07:50:00+03:00"),
            sent_nudges_today=[],
            state_source="test_fixture",
            allow_test_fixture=True,
        )
        self.assertEqual(result["selection"], {"send": False, "skip_reason": "quiet_hours"})
        rows = read_nudge_log()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["skip_reason"], "quiet_hours")

    def test_recent_activity_suppression_end_to_end(self):
        result = evaluate_nudge_slot(
            current_snapshot=self.snapshot,
            todays_events=[],
            daily_summary={},
            weekly_summary={},
            recent_user_activity=[{"timestamp": "2026-04-15T15:10:00+03:00", "text": "I already ate"}],
            current_slot="afternoon_check",
            now=ts("2026-04-15T15:30:00+03:00"),
            sent_nudges_today=[],
            state_source="test_fixture",
            allow_test_fixture=True,
        )
        self.assertFalse(result["selection"]["send"])
        self.assertEqual(result["selection"]["skip_reason"], "recent_user_activity")
        rows = read_nudge_log()
        self.assertEqual(len(rows), 1)
        self.assertFalse(rows[0]["send"])
        self.assertEqual(rows[0]["skip_reason"], "recent_user_activity")


if __name__ == "__main__":
    unittest.main()
