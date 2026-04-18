from __future__ import annotations

import json
import os
import tempfile
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

    def test_env_override_index_path_loads_local_session_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            session_file = os.path.join(tmp, "session.jsonl")
            with open(session_file, "w", encoding="utf-8") as f:
                f.write(json.dumps({
                    "type": "message",
                    "id": "m1",
                    "timestamp": "2026-04-15T10:00:00+03:00",
                    "message": {
                        "role": "assistant",
                        "content": [{"type": "text", "text": "hello"}],
                    },
                }) + "\n")
            index_file = os.path.join(tmp, "sessions.json")
            with open(index_file, "w", encoding="utf-8") as f:
                json.dump({"agent:health:discord:channel:1491124367638401024": {"sessionFile": session_file}}, f)

            old = os.environ.get("OPENCLAW_SESSIONS_INDEX")
            try:
                os.environ["OPENCLAW_SESSIONS_INDEX"] = index_file
                result = fetch_session_history("agent:health:discord:channel:1491124367638401024", 50, sessions_history_tool=None)
            finally:
                if old is None:
                    os.environ.pop("OPENCLAW_SESSIONS_INDEX", None)
                else:
                    os.environ["OPENCLAW_SESSIONS_INDEX"] = old

            self.assertEqual(result["status"], "ok")
            self.assertEqual(len(result["events"]), 1)


if __name__ == "__main__":
    unittest.main()
