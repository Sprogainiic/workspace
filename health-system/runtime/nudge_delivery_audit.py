from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "runtime" / "data" / "nudge_logs" / "delivery_audit.jsonl"
AUDIT.parent.mkdir(parents=True, exist_ok=True)


def log_delivery_audit(entry: Dict[str, Any]) -> Dict[str, Any]:
    delivery_event_type = entry.get("delivery_event_type")
    reason_code = entry.get("reason_code")
    row = {
        "timestamp": entry.get("timestamp", ""),
        "slot": entry.get("slot", ""),
        "delivery_event_type": delivery_event_type,
        "reason_code": reason_code,
        "provider": entry.get("provider"),
        "target_id": entry.get("target_id"),
        "provider_message_id": entry.get("provider_message_id"),
        "provider_sent_at": entry.get("provider_sent_at"),
        "transport": entry.get("transport"),
        "session_key": entry.get("session_key"),
        "message_text": entry.get("message_text"),
        "message_intent": entry.get("message_intent"),
        "fingerprint": entry.get("fingerprint"),
        "launcher_mode": entry.get("launcher_mode"),
        "state_source": entry.get("state_source"),
        "activity_source": entry.get("activity_source"),
        "delivery_status": entry.get("delivery_status"),
        "delivery_error": entry.get("delivery_error"),
        "attempted_send": bool(entry.get("attempted_send", False)),
        "provider_confirmed": bool(entry.get("provider_confirmed", False)),
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
        row = json.loads(line)
        if not row.get("delivery_event_type"):
            legacy_status = row.get("delivery_status")
            if legacy_status == "verified":
                row["delivery_event_type"] = "delivered"
            elif legacy_status == "failed":
                row["delivery_event_type"] = "failed"
            elif row.get("skip_reason"):
                row["delivery_event_type"] = "suppressed"
                row.setdefault("reason_code", row.get("skip_reason"))
            elif row.get("send"):
                row["delivery_event_type"] = "attempted_send"
            else:
                row["delivery_event_type"] = "suppressed"
                row.setdefault("reason_code", row.get("skip_reason") or "unspecified")
        rows.append(row)
    return rows
