from __future__ import annotations

import unittest

from runtime.session_history_client import fetch_session_history


class SessionHistoryClientTests(unittest.TestCase):
    def test_prod_success(self):
        result = fetch_session_history("agent:health:discord:channel:1491124367638401024", 50, sessions_history_tool=lambda **kwargs: {"messages": [{"role": "user"}]})
        self.assertEqual(result["status"], "ok")
        self.assertEqual(len(result["events"]), 1)

    def test_prod_unavailable_boundary(self):
        result = fetch_session_history("agent:health:discord:channel:1491124367638401024", 50, sessions_history_tool=None)
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["error"], "session_history_unavailable")

    def test_malformed_response_failure(self):
        result = fetch_session_history("agent:health:discord:channel:1491124367638401024", 50, sessions_history_tool=lambda **kwargs: {"bad": []})
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["error"], "malformed_session_history_response")


if __name__ == "__main__":
    unittest.main()
