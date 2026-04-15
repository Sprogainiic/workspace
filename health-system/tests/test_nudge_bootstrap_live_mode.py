from __future__ import annotations

import json
import unittest
from pathlib import Path

from runtime.config import OPENCLAW_HEALTH_SESSION_KEY
from runtime.nudge_cron_bootstrap import execute_slot

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "runtime" / "data"
SNAPSHOT = DATA / "snapshots" / "current_state_snapshot.json"
EVENTS = DATA / "events" / "events.jsonl"
SUMMARY = DATA / "daily_summaries" / "latest.json"
WEEKLY = DATA / "weekly_summaries" / "latest.json"
LOG_PATH = DATA / "nudge_logs" / "nudge_log.jsonl"


class NudgeBootstrapLiveModeTests(unittest.TestCase):
    def setUp(self):
        for path in [SNAPSHOT, EVENTS, SUMMARY, WEEKLY, LOG_PATH]:
            path.parent.mkdir(parents=True, exist_ok=True)
            if path.exists():
                path.unlink()
        SNAPSHOT.write_text(json.dumps({"state": {"fatigue": {"value": None}, "motivation": {"value": None}, "behavior_state": {"value": None}, "recent_misses": 0}, "simplification_level": "normal"}), encoding="utf-8")
        EVENTS.write_text(json.dumps({"timestamp": "2026-04-15T08:00:00+03:00", "event_type": "fatigue_report", "facts": {"fatigue": "low"}}) + "\n", encoding="utf-8")
        SUMMARY.write_text(json.dumps({"date": "2026-04-15", "facts": {"events_count": 1}}), encoding="utf-8")
        WEEKLY.write_text(json.dumps({"week_end": "2026-04-15", "interpretation": {"summary": "Observed completion was mixed."}}), encoding="utf-8")

    def test_live_mode_uses_launcher_path_and_logs_openclaw_session(self):
        calls = []
        def fake_sender(**kwargs):
            calls.append(kwargs)
            return {"ok": True}

        result = execute_slot(
            "evening_wrap_up",
            "openclaw_session",
            "ignored",
            exec_mode="live_session",
            fixture={
                "snapshot": {"state": {"fatigue": {"value": None}, "motivation": {"value": None}, "behavior_state": {"value": None}, "recent_misses": 0}, "simplification_level": "normal"},
                "today_events": [],
                "daily_summary": {"date": "2026-04-15", "facts": {"events_count": 1}},
                "weekly_summary": {"week_end": "2026-04-15", "interpretation": {"summary": "Observed completion was mixed."}},
                "sent_nudges_today": [],
                "recent_user_activity": [],
                "activity_source": "persisted",
            },
            session_sender=fake_sender,
        )
        self.assertTrue(result["selection"]["send"])
        self.assertEqual(result["log"]["transport"], "openclaw_session")
        self.assertEqual(result["log"]["session_key"], OPENCLAW_HEALTH_SESSION_KEY)
        self.assertEqual(result["log"]["delivery_status"], "sent")
        self.assertEqual(result["log"]["launcher_mode"], "live_session")
        self.assertEqual(len(calls), 1)


if __name__ == "__main__":
    unittest.main()
