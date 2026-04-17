from __future__ import annotations

import unittest

from runtime.config import OPENCLAW_HEALTH_SESSION_KEY
from runtime.outbound_transport import send_message


class OpenClawSessionTransportTests(unittest.TestCase):
    def test_transport_sends_to_mocked_session_boundary(self):
        calls = []

        def fake_sender(**kwargs):
            calls.append(kwargs)
            return {"ok": True}

        result = send_message(
            channel="openclaw_session",
            recipient_id="ignored",
            message_text="hello",
            session_key=OPENCLAW_HEALTH_SESSION_KEY,
            target_type="channel",
            metadata={"mode": "proactive", "slot": "lunch_check", "nudge_type": "reminder", "domain": "nutrition"},
            session_sender=fake_sender,
        )
        self.assertTrue(result["sent"])
        self.assertEqual(result["delivery_status"], "sent")
        self.assertEqual(result["payload_kind"], "proactive_nudge")
        self.assertEqual(calls[0]["sessionKey"], OPENCLAW_HEALTH_SESSION_KEY)
        self.assertEqual(calls[0]["message"], "hello")

    def test_unsupported_transport_fails_without_fallback(self):
        with self.assertRaises(Exception):
            send_message(channel="bad", recipient_id="x", message_text="y")


if __name__ == "__main__":
    unittest.main()
