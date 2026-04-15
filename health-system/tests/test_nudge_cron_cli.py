from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path

from runtime.nudge_log import read_nudge_log

ROOT = Path(__file__).resolve().parents[1]
LOG_PATH = ROOT / "runtime" / "data" / "nudge_logs" / "nudge_log.jsonl"


class NudgeCronCliTests(unittest.TestCase):
    def setUp(self):
        if LOG_PATH.exists():
            LOG_PATH.unlink()

    def test_valid_slot_executes_and_logs_send_or_skip(self):
        proc = subprocess.run(
            ["python3", "-m", "runtime.nudge_cron_bootstrap", "--slot", "lunch_check", "--channel", "test", "--recipient", "user_1"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["slot"], "lunch_check")
        rows = read_nudge_log()
        self.assertEqual(len(rows), 1)
        self.assertIn(rows[0]["send"], {True, False})

    def test_invalid_slot_fails_nonzero(self):
        proc = subprocess.run(
            ["python3", "-m", "runtime.nudge_cron_bootstrap", "--slot", "bad_slot", "--channel", "test", "--recipient", "user_1"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(proc.returncode, 0)
        payload = json.loads(proc.stdout)
        self.assertIn("error", payload)

    def test_skip_path_logs(self):
        proc = subprocess.run(
            ["python3", "-m", "runtime.nudge_cron_bootstrap", "--slot", "morning_plan_check", "--channel", "test", "--recipient", "user_1"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0)
        rows = read_nudge_log()
        self.assertEqual(len(rows), 1)
        self.assertTrue(rows[0]["evaluated"])

    def test_console_transport_executes(self):
        proc = subprocess.run(
            ["python3", "-m", "runtime.nudge_cron_bootstrap", "--slot", "lunch_check", "--channel", "console", "--recipient", "user_1"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0)
        rows = read_nudge_log()
        self.assertEqual(len(rows), 1)


if __name__ == "__main__":
    unittest.main()
