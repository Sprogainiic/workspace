from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "runtime" / "data" / "nudge_logs" / "delivery_audit.jsonl"
AUDIT.parent.mkdir(parents=True, exist_ok=True)


def log_delivery_audit(entry: Dict[str, Any]) -> Dict[str, Any]:
    row = {
        "timestamp": entry.get("timestamp", ""),
        "slot": entry.get("slot", ""),
        "send": bool(entry.get("send", False)),
        "skip_reason": entry.get("skip_reason"),
        "transport": entry.get("transport"),
        "session_key": entry.get("session_key"),
        "delivery_status": entry.get("delivery_status"),
        "delivery_error": entry.get("delivery_error"),
        "message_text": entry.get("message_text"),
        "message_intent": entry.get("message_intent"),
        "fingerprint": entry.get("fingerprint"),
        "launcher_mode": entry.get("launcher_mode"),
        "state_source": entry.get("state_source"),
        "activity_source": entry.get("activity_source"),
    }
    with AUDIT.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row


def read_delivery_audit() -> List[Dict[str, Any]]:
    if not AUDIT.exists():
        return []
    rows: List[Dict[str, Any]] = []
    for line in AUDIT.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows
