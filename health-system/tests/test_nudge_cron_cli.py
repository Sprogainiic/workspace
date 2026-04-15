from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path

from runtime.nudge_log import read_nudge_log

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "runtime" / "data"
LOG_PATH = DATA / "nudge_logs" / "nudge_log.jsonl"
SNAPSHOT = DATA / "snapshots" / "current_state_snapshot.json"
EVENTS = DATA / "events" / "events.jsonl"
SUMMARY = DATA / "daily_summaries" / "latest.json"


class NudgeCronCliTests(unittest.TestCase):
    def setUp(self):
        for path in [LOG_PATH, SNAPSHOT, EVENTS, SUMMARY]:
            path.parent.mkdir(parents=True, exist_ok=True)
            if path.exists():
                path.unlink()

    def _write_persisted_state(self):
        SNAPSHOT.write_text(json.dumps({"state": {"fatigue": {"value": "low"}}, "simplification_level": "normal"}), encoding="utf-8")
        EVENTS.write_text(json.dumps({"timestamp": "2026-04-15T08:00:00+03:00", "event_type": "fatigue_report", "facts": {"fatigue": "low"}}) + "\n", encoding="utf-8")
        SUMMARY.write_text(json.dumps({"date": "2026-04-15", "facts": {"events_count": 1}}), encoding="utf-8")

    def test_valid_slot_with_persisted_state_executes_and_logs(self):
        self._write_persisted_state()
        proc = subprocess.run(
            ["python3", "-m", "runtime.nudge_cron_bootstrap", "--slot", "lunch_check", "--channel", "test", "--recipient", "user_1"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        self.assertNotIn("RuntimeWarning", proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["slot"], "lunch_check")
        self.assertEqual(payload["state_source"], "persisted")
        rows = read_nudge_log()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["state_source"], "persisted")

    def test_valid_slot_with_missing_state_fails_cleanly(self):
        proc = subprocess.run(
            ["python3", "-m", "runtime.nudge_cron_bootstrap", "--slot", "lunch_check", "--channel", "test", "--recipient", "user_1"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertNotIn("RuntimeWarning", proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["error"], "missing_runtime_state")

    def test_invalid_slot_fails_nonzero(self):
        self._write_persisted_state()
        proc = subprocess.run(
            ["python3", "-m", "runtime.nudge_cron_bootstrap", "--slot", "bad_slot", "--channel", "test", "--recipient", "user_1"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertNotIn("RuntimeWarning", proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertIn("error", payload)

    def test_console_transport_executes(self):
        self._write_persisted_state()
        proc = subprocess.run(
            ["python3", "-m", "runtime.nudge_cron_bootstrap", "--slot", "lunch_check", "--channel", "console", "--recipient", "user_1"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        self.assertNotIn("RuntimeWarning", proc.stderr)
        rows = read_nudge_log()
        self.assertEqual(len(rows), 1)


if __name__ == "__main__":
    unittest.main()
