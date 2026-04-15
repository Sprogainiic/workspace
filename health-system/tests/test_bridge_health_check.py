from __future__ import annotations

import json
import unittest
from datetime import datetime
from pathlib import Path

from runtime.bridge_health_check import bridge_health

ROOT = Path(__file__).resolve().parents[1]
INGEST = ROOT / "runtime" / "data" / "ingest"
HEARTBEAT = INGEST / "reactive_bridge_heartbeat.jsonl"
STATUS = INGEST / "reactive_bridge_status.json"


class BridgeHealthCheckTests(unittest.TestCase):
    def setUp(self):
        INGEST.mkdir(parents=True, exist_ok=True)
        for path in [HEARTBEAT, STATUS]:
            if path.exists():
                path.unlink()

    def test_healthy_when_fresh(self):
        HEARTBEAT.write_text(json.dumps({"timestamp": "2026-04-15T17:00:00+03:00"}) + "\n", encoding="utf-8")
        STATUS.write_text(json.dumps({"timestamp": "2026-04-15T17:00:05+03:00"}), encoding="utf-8")
        result = bridge_health(now=datetime.fromisoformat("2026-04-15T17:00:10+03:00"))
        self.assertTrue(result["healthy"])

    def test_unhealthy_when_stale(self):
        HEARTBEAT.write_text(json.dumps({"timestamp": "2026-04-15T17:00:00+03:00"}) + "\n", encoding="utf-8")
        STATUS.write_text(json.dumps({"timestamp": "2026-04-15T17:00:00+03:00"}), encoding="utf-8")
        result = bridge_health(now=datetime.fromisoformat("2026-04-15T17:00:20+03:00"))
        self.assertFalse(result["healthy"])


if __name__ == "__main__":
    unittest.main()
