from __future__ import annotations

import json
import unittest
from datetime import datetime
from pathlib import Path

from runtime.chat_flow import evaluate_nudge_slot
from runtime.user_activity_loader import load_recent_user_activity

ROOT = Path(__file__).resolve().parents[1]
INBOUND = ROOT / "runtime" / "data" / "inbound" / "discord_messages.jsonl"


def ts(value: str) -> datetime:
    return datetime.fromisoformat(value)


class ContinuousSuppressionRegressionTests(unittest.TestCase):
    def setUp(self):
        INBOUND.parent.mkdir(parents=True, exist_ok=True)
        if INBOUND.exists():
            INBOUND.unlink()

    def test_recent_related_inbound_discord_message_suppresses_nearby_proactive_nudge(self):
        INBOUND.write_text(json.dumps({
            "timestamp": "2026-04-15T16:58:00+03:00",
            "source_channel": "discord",
            "source_type": "channel",
            "session_key": "agent:health:discord:channel:1491124367638401024",
            "discord_user_id": "u1",
            "discord_message_id": "m-suppress",
            "message_text": "I ate dinner already"
        }) + "\n", encoding="utf-8")
        activity = load_recent_user_activity(ts("2026-04-15T17:05:00+03:00"))
        result = evaluate_nudge_slot(
            current_snapshot={"state": {"fatigue": {"value": None}, "motivation": {"value": None}, "behavior_state": {"value": None}, "recent_misses": 0}, "simplification_level": "normal"},
            todays_events=[],
            daily_summary={},
            recent_user_activity=activity["recent_user_activity"],
            current_slot="dinner_check",
            now=ts("2026-04-15T17:05:00+03:00"),
            sent_nudges_today=[],
            state_source="persisted",
            allow_test_fixture=True,
            activity_source=activity["activity_source"],
        )
        self.assertFalse(result["selection"]["send"])
        self.assertEqual(result["selection"]["skip_reason"], "recent_user_activity")

    def test_recent_unrelated_inbound_discord_message_does_not_suppress(self):
        INBOUND.write_text(json.dumps({
            "timestamp": "2026-04-15T16:58:00+03:00",
            "source_channel": "discord",
            "source_type": "channel",
            "session_key": "agent:health:discord:channel:1491124367638401024",
            "discord_user_id": "u1",
            "discord_message_id": "m-unsuppress",
            "message_text": "I am tired and skipped workout"
        }) + "\n", encoding="utf-8")
        activity = load_recent_user_activity(ts("2026-04-15T17:05:00+03:00"))
        result = evaluate_nudge_slot(
            current_snapshot={"state": {"fatigue": {"value": None}, "motivation": {"value": None}, "behavior_state": {"value": None}, "recent_misses": 0}, "simplification_level": "normal"},
            todays_events=[],
            daily_summary={},
            recent_user_activity=activity["recent_user_activity"],
            current_slot="dinner_check",
            now=ts("2026-04-15T17:05:00+03:00"),
            sent_nudges_today=[],
            state_source="persisted",
            allow_test_fixture=True,
            activity_source=activity["activity_source"],
        )
        self.assertTrue(result["selection"]["send"])


if __name__ == "__main__":
    unittest.main()
