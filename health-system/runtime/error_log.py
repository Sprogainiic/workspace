from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "runtime" / "data" / "logs" / "error_log.jsonl"
LOG.parent.mkdir(parents=True, exist_ok=True)


def log_error(
    *,
    timestamp: str,
    component: str,
    error_type: str,
    event_id: str = "",
    event_type: str = "",
    reason: str = "",
    raw_event: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    row = {
        "timestamp": timestamp,
        "component": component,
        "error_type": error_type,
        "event_id": event_id,
        "event_type": event_type,
        "reason": reason,
        "raw_event": raw_event or {},
    }
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row
