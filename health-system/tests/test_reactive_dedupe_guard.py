from __future__ import annotations

import unittest
from pathlib import Path

from runtime.reactive_dedupe_guard import check_and_mark

SEEN = Path(__file__).resolve().parents[1] / "runtime" / "data" / "ingest" / "reactive_seen.json"


class ReactiveDedupeGuardTests(unittest.TestCase):
    def setUp(self):
        if SEEN.exists():
            SEEN.unlink()

    def test_first_message_accepts_second_duplicate_ignores(self):
        self.assertTrue(check_and_mark("agent:health:discord:channel:1491124367638401024", "msg-1"))
        self.assertFalse(check_and_mark("agent:health:discord:channel:1491124367638401024", "msg-1"))


if __name__ == "__main__":
    unittest.main()
