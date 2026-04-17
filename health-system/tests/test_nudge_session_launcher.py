from __future__ import annotations

import unittest

from runtime.nudge_session_launcher import launch_to_session
from runtime.config import OPENCLAW_HEALTH_SESSION_KEY


class NudgeSessionLauncherTests(unittest.TestCase):
    def test_success_path(self):
        calls = []
        def fake_sender(**kwargs):
            calls.append(kwargs)
            return {"ok": True}
        result = launch_to_session(
            {
                "session_key": OPENCLAW_HEALTH_SESSION_KEY,
                "payload": {
                    "kind": "proactive_nudge",
                    "message_text": "hello",
                    "slot": "lunch_check",
                    "nudge_type": "reminder",
                    "domain": "nutrition",
                    "source": "health-system-runtime",
                },
            },
            fake_sender,
        )
        self.assertEqual(result["status"], "sent")
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]["message"], "hello")

    def test_failure_path(self):
        def fake_sender(**kwargs):
            raise RuntimeError("boom")
        result = launch_to_session(
            {
                "session_key": OPENCLAW_HEALTH_SESSION_KEY,
                "payload": {
                    "kind": "proactive_nudge",
                    "message_text": "hello",
                    "slot": "lunch_check",
                    "nudge_type": "reminder",
                    "domain": "nutrition",
                    "source": "health-system-runtime",
                },
            },
            fake_sender,
        )
        self.assertEqual(result["status"], "failed")

    def test_malformed_payload_rejection(self):
        result = launch_to_session({"session_key": OPENCLAW_HEALTH_SESSION_KEY, "payload": {"bad": 1}}, lambda **kwargs: None)
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["delivery_error"], "malformed_payload")

    def test_missing_session_key_rejection(self):
        result = launch_to_session({"payload": {"kind": "proactive_nudge", "message_text": "x", "slot": "lunch_check", "nudge_type": "reminder", "domain": "nutrition", "source": "health-system-runtime"}}, lambda **kwargs: None)
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["delivery_error"], "missing_session_key")


if __name__ == "__main__":
    unittest.main()
