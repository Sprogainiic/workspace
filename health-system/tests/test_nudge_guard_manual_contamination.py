from __future__ import annotations

import unittest
from datetime import datetime

from runtime.nudge_guard import check_gap_rule, nudges_sent_today, enforce_guardrails


def ts(value: str) -> datetime:
    return datetime.fromisoformat(value)


class NudgeGuardManualContaminationTests(unittest.TestCase):
    def test_local_test_rows_do_not_count_as_real_delivery(self):
        sent = [
            {
                'timestamp': '2026-04-18T11:59:47+03:00',
                'slot': 'lunch_check',
                'delivery_event_type': 'attempted_send',
                'reason_code': 'manual_test',
                'provider_confirmed': False,
                'delivery_error': None,
                'launcher_mode': 'local_test',
                'domain': 'nutrition',
            }
        ]
        self.assertEqual(nudges_sent_today(sent), 0)
        self.assertIsNone(check_gap_rule(ts('2026-04-18T12:15:00+03:00'), sent, {'min_minutes_between_proactive_messages': 90}, 'lunch_check'))

    def test_verified_delivery_counts_for_gap_rule(self):
        sent = [
            {
                'timestamp': '2026-04-18T15:57:33+03:00',
                'slot': 'evening_wrap_up',
                'delivery_event_type': 'delivered',
                'reason_code': None,
                'provider_confirmed': True,
                'delivery_error': None,
                'launcher_mode': 'live_session',
                'domain': 'wrap_up',
            }
        ]
        self.assertEqual(nudges_sent_today(sent), 1)
        self.assertEqual(check_gap_rule(ts('2026-04-18T18:00:00+03:00'), sent, {'min_minutes_between_proactive_messages': 90}, 'dinner_check'), None)
        self.assertEqual(enforce_guardrails(ts('2026-04-18T18:00:00+03:00'), 'nutrition', sent, [], {'min_minutes_between_proactive_messages': 90}, 'dinner_check'), None)


if __name__ == '__main__':
    unittest.main()
