from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from .nudge_delivery_audit import read_delivery_audit


def _parse_ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def load_sent_nudges_today(now: datetime, rows: Optional[List[Dict[str, Any]]] = None) -> Dict[str, List[Dict[str, Any]]]:
    audit_rows = rows if rows is not None else read_delivery_audit()
    today = now.date()
    sent_nudges_today: List[Dict[str, Any]] = []
    for row in audit_rows:
        event_type = row.get("delivery_event_type")
        if event_type not in {"attempted_send", "delivered", "failed", "suppressed"}:
            continue
        timestamp = row.get("timestamp")
        if not timestamp:
            continue
        try:
            ts = _parse_ts(timestamp)
        except ValueError:
            continue
        if ts.date() != today:
            continue
        sent_nudges_today.append(
            {
                "timestamp": timestamp,
                "slot": row.get("slot", ""),
                "nudge_type": row.get("message_intent") or row.get("nudge_type", ""),
                "domain": row.get("domain", ""),
                "message_fingerprint": row.get("fingerprint", ""),
                "message_intent": row.get("message_intent") or row.get("nudge_type"),
                "fingerprint": row.get("fingerprint") or row.get("message_fingerprint"),
                "delivery_event_type": event_type,
                "reason_code": row.get("reason_code"),
                "provider": row.get("provider"),
                "target_id": row.get("target_id"),
                "provider_message_id": row.get("provider_message_id"),
                "provider_sent_at": row.get("provider_sent_at"),
                "attempted_send": bool(row.get("attempted_send", False) or event_type == "attempted_send"),
                "provider_confirmed": bool(row.get("provider_confirmed", False) or event_type == "delivered"),
                "delivery_status": event_type,
                "delivery_error": row.get("delivery_error"),
                "launcher_mode": row.get("launcher_mode"),
                "runtime_mode": row.get("runtime_mode"),
                "source": row.get("source") or row.get("launcher_mode") or "delivery_audit",
            }
        )
    return {"sent_nudges_today": sent_nudges_today}
