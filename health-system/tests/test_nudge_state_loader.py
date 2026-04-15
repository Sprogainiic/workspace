from __future__ import annotations

import json
import unittest
from datetime import datetime
from pathlib import Path

from runtime.nudge_log import log_nudge_decision
from runtime.state_loader import MissingRuntimeStateError, load_runtime_state

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "runtime" / "data"
SNAPSHOT = DATA / "snapshots" / "current_state_snapshot.json"
EVENTS = DATA / "events" / "events.jsonl"
SUMMARY = DATA / "daily_summaries" / "latest.json"
LOG_PATH = DATA / "nudge_logs" / "nudge_log.jsonl"


def ts(value: str) -> datetime:
    return datetime.fromisoformat(value)


class NudgeStateLoaderTests(unittest.TestCase):
    def setUp(self):
        SNAPSHOT.parent.mkdir(parents=True, exist_ok=True)
        EVENTS.parent.mkdir(parents=True, exist_ok=True)
        SUMMARY.parent.mkdir(parents=True, exist_ok=True)
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        for path in [SNAPSHOT, EVENTS, SUMMARY, LOG_PATH]:
            if path.exists():
                path.unlink()

    def test_loads_snapshot_events_summary_and_today_sent_nudges(self):
        SNAPSHOT.write_text(json.dumps({"state": {"fatigue": {"value": "low"}}}), encoding="utf-8")
        EVENTS.write_text(
            "\n".join([
                json.dumps({"timestamp": "2026-04-15T08:00:00+03:00", "event_type": "fatigue_report", "facts": {"fatigue": "low"}}),
                json.dumps({"timestamp": "2026-04-14T08:00:00+03:00", "event_type": "meal_logged", "facts": {"logged": True}}),
            ]),
            encoding="utf-8",
        )
        SUMMARY.write_text(json.dumps({"date": "2026-04-15", "facts": {"events_count": 1}}), encoding="utf-8")
        log_nudge_decision({
            "timestamp": "2026-04-15T12:30:00+03:00",
            "slot": "lunch_check",
            "evaluated": True,
            "send": True,
            "skip_reason": None,
            "nudge_type": "reminder",
            "domain": "nutrition",
            "tokens_in": 1,
            "tokens_out": 1,
            "message_intent": "reminder",
            "fingerprint": "fp1",
            "message_fingerprint": "fp1",
        })

        state = load_runtime_state(ts("2026-04-15T15:00:00+03:00"))
        self.assertEqual(state["state_source"], "persisted")
        self.assertEqual(state["snapshot"]["state"]["fatigue"]["value"], "low")
        self.assertEqual(len(state["today_events"]), 1)
        self.assertEqual(state["daily_summary"]["date"], "2026-04-15")
        self.assertEqual(len(state["sent_nudges_today"]), 1)

    def test_missing_state_handled_cleanly(self):
        with self.assertRaises(MissingRuntimeStateError):
            load_runtime_state(ts("2026-04-15T15:00:00+03:00"))

    def test_test_fixture_mode_uses_fixture_not_synthetic_fallback(self):
        fixture = {
            "snapshot": {"state": {"fatigue": {"value": "medium"}}},
            "today_events": [{"timestamp": "2026-04-15T09:00:00+03:00", "event_type": "fatigue_report"}],
            "daily_summary": {"date": "2026-04-15"},
            "sent_nudges_today": [{"slot": "lunch_check"}],
        }
        state = load_runtime_state(ts("2026-04-15T15:00:00+03:00"), allow_test_fixture=True, fixture=fixture)
        self.assertEqual(state["state_source"], "test_fixture")
        self.assertEqual(state["snapshot"]["state"]["fatigue"]["value"], "medium")


if __name__ == "__main__":
    unittest.main()
