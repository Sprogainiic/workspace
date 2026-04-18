from __future__ import annotations

import unittest
from unittest.mock import patch

from runtime.config import OPENCLAW_HEALTH_SESSION_KEY
from runtime.outbound_transport import send_message


class OpenClawSessionTransportTests(unittest.TestCase):
    def test_transport_sends_via_direct_discord_transport(self):
        with patch('runtime.outbound_transport.send_discord_direct', return_value={'sent': True, 'delivery_status': 'sent', 'delivery_error': None, 'raw': {'ok': True}}) as mock_send:
            result = send_message(
                channel="openclaw_session",
                recipient_id="1491124367638401024",
                message_text="hello",
                session_key=OPENCLAW_HEALTH_SESSION_KEY,
                target_type="channel",
                metadata={"mode": "proactive", "slot": "lunch_check", "nudge_type": "reminder", "domain": "nutrition"},
                session_sender=None,
            )
        self.assertTrue(result["sent"])
        self.assertEqual(result["delivery_status"], "sent")
        self.assertEqual(result["payload_kind"], "discord_direct_message")
        mock_send.assert_called_once_with('1491124367638401024', 'hello')

    def test_unsupported_transport_fails_without_fallback(self):
        with self.assertRaises(Exception):
            send_message(channel="bad", recipient_id="x", message_text="y")

    def test_discord_direct_alias_uses_same_transport(self):
        with patch('runtime.outbound_transport.send_discord_direct', return_value={'sent': True, 'delivery_status': 'sent', 'delivery_error': None, 'raw': {'ok': True}}) as mock_send:
            result = send_message(
                channel="discord_direct",
                recipient_id="1491124367638401024",
                message_text="hello",
            )
        self.assertTrue(result["sent"])
        self.assertEqual(result["channel"], "discord_direct")
        mock_send.assert_called_once_with('1491124367638401024', 'hello')


if __name__ == "__main__":
    unittest.main()
