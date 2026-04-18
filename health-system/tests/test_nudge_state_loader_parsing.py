from __future__ import annotations

import unittest
from datetime import datetime

from runtime.nudge_state_loader import load_sent_nudges_today


def ts(value: str) -> datetime:
    return datetime.fromisoformat(value)


class NudgeStateLoaderParsingTests(unittest.TestCase):
    def test_accepts_z_timestamps_and_skips_invalid_rows(self):
        rows = [
            {
                "timestamp": "2026-04-15T16:00:00Z",
                "send": True,
                "slot": "lunch_check",
                "nudge_type": "reminder",
                "domain": "nutrition",
                "message_intent": "reminder",
                "fingerprint": "fp-z",
            },
            {
                "timestamp": "not-a-timestamp",
                "send": True,
                "slot": "afternoon_check",
                "nudge_type": "check_in",
                "domain": "behavior",
            },
        ]
        loaded = load_sent_nudges_today(ts("2026-04-15T18:30:00+00:00"), rows=rows)
        self.assertEqual(len(loaded["sent_nudges_today"]), 1)
        self.assertEqual(loaded["sent_nudges_today"][0]["fingerprint"], "fp-z")


if __name__ == "__main__":
    unittest.main()
