from __future__ import annotations

import unittest

from runtime.nudge_delivery_verify import verify_message_in_session_history


class NudgeDeliveryVerifyTests(unittest.TestCase):
    def test_verifies_message_when_present(self):
        result = verify_message_in_session_history(
            "agent:health:discord:channel:1491124367638401024",
            "Quick wrap-up: what got done today?",
            sessions_history_tool=lambda **kwargs: {
                "messages": [
                    {
                        "role": "assistant",
                        "content": [{"type": "text", "text": "Quick wrap-up: what got done today?"}],
                    }
                ]
            },
        )
        self.assertTrue(result["verified"])
        self.assertEqual(result["status"], "ok")

    def test_reports_message_not_found(self):
        result = verify_message_in_session_history(
            "agent:health:discord:channel:1491124367638401024",
            "needle",
            sessions_history_tool=lambda **kwargs: {
                "messages": [
                    {
                        "role": "assistant",
                        "content": [{"type": "text", "text": "haystack"}],
                    }
                ]
            },
        )
        self.assertFalse(result["verified"])
        self.assertEqual(result["error"], "message_not_found")


if __name__ == "__main__":
    unittest.main()
