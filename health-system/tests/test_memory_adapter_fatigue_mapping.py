from __future__ import annotations

import sys
import types
import unittest

if "runtime.error_log" not in sys.modules:
    stub = types.ModuleType("runtime.error_log")
    stub.log_error = lambda *args, **kwargs: None
    sys.modules["runtime.error_log"] = stub

if "runtime.validator" not in sys.modules:
    validator_stub = types.ModuleType("runtime.validator")
    validator_stub.validate_memory_adapter_output = lambda payload: {"status": "PASS"}
    sys.modules["runtime.validator"] = validator_stub

if "runtime.token_logger" not in sys.modules:
    token_stub = types.ModuleType("runtime.token_logger")
    token_stub.log_token_usage = lambda *args, **kwargs: None
    sys.modules["runtime.token_logger"] = token_stub

from runtime.chat_flow import memory_adapter


class MemoryAdapterFatigueMappingTests(unittest.TestCase):
    def test_low_energy_maps_to_high_fatigue(self):
        result = memory_adapter("energy low today", "msg1", "2026-04-15T09:00:00+03:00")
        self.assertEqual(result["EXTRACTIONS"]["fatigue"], "high")
        fatigue_event = next(p for p in result["MEMORY_UPDATE_PROPOSALS"] if p["event_type"] == "fatigue_report")
        self.assertEqual(fatigue_event["value"], "high")

    def test_super_tired_maps_to_high_fatigue(self):
        result = memory_adapter("super tired after work", "msg2", "2026-04-15T18:00:00+03:00")
        self.assertEqual(result["EXTRACTIONS"]["fatigue"], "high")


if __name__ == "__main__":
    unittest.main()
