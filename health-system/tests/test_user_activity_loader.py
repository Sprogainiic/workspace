from __future__ import annotations

import json
import unittest
from datetime import datetime
from pathlib import Path

from runtime.chat_flow import evaluate_nudge_slot
from runtime.user_activity_loader import load_recent_user_activity

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "runtime" / "data"
EVENTS = DATA / "events" / "events.jsonl"
CHAT = DATA / "raw_chat" / "recent.json"
TURNS = DATA / "turn_logs" / "reactive_turns.jsonl"
LOG_PATH = DATA / "nudge_logs" / "nudge_log.jsonl"


def ts(value: str) -> datetime:
    return datetime.fromisoformat(value)


class UserActivityLoaderTests(unittest.TestCase):
    def setUp(self):
        for path in [EVENTS, CHAT, TURNS, LOG_PATH]:
            path.parent.mkdir(parents=True, exist_ok=True)
            if path.exists():
                path.unlink()

    def test_persisted_recent_activity_loaded_correctly(self):
        EVENTS.write_text(
            json.dumps({"timestamp": "2026-04-15T14:40:00+03:00", "event_type": "meal_logged", "facts": {"logged": True}}) + "\n",
            encoding="utf-8",
        )
        result = load_recent_user_activity(ts("2026-04-15T15:00:00+03:00"))
        self.assertEqual(result["activity_source"], "persisted")
        self.assertEqual(len(result["recent_user_activity"]), 1)
        self.assertEqual(result["recent_user_activity"][0]["signal_type"], "meal_log")

    def test_no_activity_returns_explicit_missing_status(self):
        result = load_recent_user_activity(ts("2026-04-15T15:00:00+03:00"))
        self.assertEqual(result["activity_source"], "missing")
        self.assertEqual(result["recent_user_activity"], [])

    def test_suppression_fires_when_recent_activity_exists(self):
        result = evaluate_nudge_slot(
            current_snapshot={"state": {"fatigue": {"value": None}, "motivation": {"value": None}, "behavior_state": {"value": None}, "recent_misses": 0}, "simplification_level": "normal"},
            todays_events=[],
            daily_summary={},
            recent_user_activity=[{"timestamp": "2026-04-15T14:40:00+03:00", "source": "event", "signal_type": "meal_log"}],
            current_slot="lunch_check",
            now=ts("2026-04-15T15:00:00+03:00"),
            sent_nudges_today=[],
            state_source="test_fixture",
            allow_test_fixture=True,
            activity_source="persisted",
        )
        self.assertFalse(result["selection"]["send"])
        self.assertEqual(result["selection"]["skip_reason"], "recent_user_activity")

    def test_suppression_does_not_fire_when_recent_activity_absent(self):
        result = evaluate_nudge_slot(
            current_snapshot={"state": {"fatigue": {"value": None}, "motivation": {"value": None}, "behavior_state": {"value": None}, "recent_misses": 0}, "simplification_level": "normal"},
            todays_events=[],
            daily_summary={},
            recent_user_activity=[],
            current_slot="lunch_check",
            now=ts("2026-04-15T15:00:00+03:00"),
            sent_nudges_today=[],
            state_source="test_fixture",
            allow_test_fixture=True,
            activity_source="missing",
        )
        self.assertTrue(result["selection"]["send"])


if __name__ == "__main__":
    unittest.main()
