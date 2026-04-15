from __future__ import annotations

from typing import Any, Dict

from .health_director_adapter import run_health_director_proactive_turn


def run_proactive_turn(payload: Dict[str, Any], *, allow_test_stub: bool = False) -> Dict[str, Any]:
    if allow_test_stub:
        raise RuntimeError("stub runtime is disabled for proactive prod path")
    return run_health_director_proactive_turn(payload)
