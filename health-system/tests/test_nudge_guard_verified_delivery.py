from __future__ import annotations

import unittest
from datetime import datetime

from runtime.nudge_guard import check_gap_rule, nudges_sent_today


def ts(value: str) -> datetime:
    return datetime.fromisoformat(value)


class NudgeGuardVerifiedDeliveryTests(unittest.TestCase):
    def test_unverified_failed_send_does_not_count_as_sent(self):
        sent = [
            {
                'timestamp': '2026-04-18T09:45:21+03:00',
                'send': True,
                'delivery_status': 'sent',
                'delivery_error': 'message_not_found',
                'domain': 'wrap_up',
            }
        ]
        self.assertEqual(nudges_sent_today(sent), 0)
        self.assertIsNone(check_gap_rule(ts('2026-04-18T10:45:18+03:00'), sent, {'min_minutes_between_proactive_messages': 90}))

    def test_verified_send_counts_for_gap_rule(self):
        sent = [
            {
                'timestamp': '2026-04-18T09:45:21+03:00',
                'send': True,
                'delivery_status': 'verified',
                'delivery_error': None,
                'domain': 'wrap_up',
            }
        ]
        self.assertEqual(nudges_sent_today(sent), 1)
        self.assertEqual(check_gap_rule(ts('2026-04-18T10:00:00+03:00'), sent, {'min_minutes_between_proactive_messages': 90}), 'spam_guard')


if __name__ == '__main__':
    unittest.main()
