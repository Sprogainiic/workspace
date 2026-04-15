from __future__ import annotations

import unittest
from datetime import datetime

from runtime.nudge_selector import select_nudge
from runtime.nudge_schedule import NUDGE_SLOTS, cron_specs


BASE_SNAPSHOT = {
    "state": {
        "fatigue": {"value": None},
        "motivation": {"value": None},
        "behavior_state": {"value": None},
        "recent_misses": 0,
    },
    "simplification_level": "normal",
}


def ts(value: str) -> datetime:
    return datetime.fromisoformat(value)


class NudgeRuntimeTests(unittest.TestCase):
    def test_weekly_reflection_can_shift_send_style_to_reset(self):
        snapshot = {
            "state": {
                "fatigue": {"value": "medium"},
                "motivation": {"value": "low"},
                "behavior_state": {"value": "fragile"},
                "recent_misses": 1,
            },
            "simplification_level": "normal",
        }
        weekly = {
            "interpretation": {"summary": "Most common behavior pattern this week: restart_cycle."},
            "next_week_implications": ["Bias toward simpler restarts and lower-friction recovery after misses."],
            "risk_flags": [],
        }
        result = select_nudge(snapshot, [], None, weekly, [], [], "afternoon_check", ts("2026-04-15T15:40:00+03:00"))
        self.assertTrue(result["send"])
        self.assertEqual(result["payload_brief"]["send_style"], "reset")
        self.assertEqual(result["payload_brief"]["weekly_reflection"]["summary"], weekly["interpretation"]["summary"])

    def test_cron_specs_cover_all_slots(self):
        specs = cron_specs()
        self.assertEqual(len(specs), len(NUDGE_SLOTS))
        self.assertEqual({row["slot"] for row in specs}, set(NUDGE_SLOTS))
        self.assertTrue(all(row["evaluation_only"] for row in specs))

    def test_no_user_activity_all_day_respects_caps_and_gaps(self):
        snapshot = BASE_SNAPSHOT
        sent = []
        recent = []
        events = []
        daily_summary = None
        planned = []

        cases = [
            ("morning_plan_check", ts("2026-04-15T08:20:00+03:00")),
            ("late_morning_check", ts("2026-04-15T10:50:00+03:00")),
            ("lunch_check", ts("2026-04-15T12:20:00+03:00")),
            ("afternoon_check", ts("2026-04-15T15:40:00+03:00")),
            ("dinner_check", ts("2026-04-15T18:05:00+03:00")),
            ("evening_wrap_up", ts("2026-04-15T20:05:00+03:00")),
        ]
        for slot, now in cases:
            result = select_nudge(snapshot, events, daily_summary, None, sent, recent, slot, now)
            planned.append(result)
            if result["send"]:
                sent.append({
                    "timestamp": now.isoformat(),
                    "slot": slot,
                    "send": True,
                    "domain": result["domain"],
                    "message_intent": result["message_intent"],
                    "fingerprint": result["fingerprint"],
                })
        sent_results = [row for row in planned if row["send"]]
        self.assertTrue(1 <= len(sent_results) <= 4)
        self.assertFalse(planned[-1]["send"])
        self.assertIn(planned[-1]["skip_reason"], {"spam_guard", "already_reported", "recent_user_activity"})

    def test_morning_and_lunch_reported_are_skipped(self):
        events = [
            {"timestamp": "2026-04-15T08:10:00+03:00", "event_type": "fatigue_report", "facts": {"fatigue": "medium"}},
            {"timestamp": "2026-04-15T12:00:00+03:00", "event_type": "meal_logged", "facts": {"logged": True, "meal": "lunch"}},
        ]
        morning = select_nudge(BASE_SNAPSHOT, events, None, None, [], [], "morning_plan_check", ts("2026-04-15T08:20:00+03:00"))
        lunch = select_nudge(BASE_SNAPSHOT, events, None, None, [], [], "lunch_check", ts("2026-04-15T12:20:00+03:00"))
        self.assertEqual(morning, {"send": False, "skip_reason": "already_reported"})
        self.assertEqual(lunch, {"send": False, "skip_reason": "already_reported"})

    def test_frequent_user_messages_suppress_proactive_nudges(self):
        recent = [{"timestamp": "2026-04-15T12:00:00+03:00", "text": "just checking in again"}]
        result = select_nudge(BASE_SNAPSHOT, [], None, None, [], recent, "lunch_check", ts("2026-04-15T12:20:00+03:00"))
        self.assertEqual(result, {"send": False, "skip_reason": "recent_user_activity"})

    def test_low_motivation_afternoon_allows_coaching(self):
        snapshot = {
            "state": {
                "fatigue": {"value": "medium"},
                "motivation": {"value": "low"},
                "behavior_state": {"value": "fragile"},
                "recent_misses": 2,
            },
            "simplification_level": "normal",
        }
        result = select_nudge(snapshot, [], None, None, [], [], "afternoon_check", ts("2026-04-15T15:40:00+03:00"))
        self.assertTrue(result["send"])
        self.assertEqual(result["nudge_type"], "coaching")
        self.assertEqual(result["domain"], "training")

    def test_evening_wrap_up_reported_is_skipped(self):
        events = [
            {"timestamp": "2026-04-15T19:50:00+03:00", "event_type": "day_summary", "facts": {"summary": "done"}},
        ]
        result = select_nudge(BASE_SNAPSHOT, events, None, None, [], [], "evening_wrap_up", ts("2026-04-15T20:05:00+03:00"))
        self.assertEqual(result, {"send": False, "skip_reason": "already_reported"})


if __name__ == "__main__":
    unittest.main()
