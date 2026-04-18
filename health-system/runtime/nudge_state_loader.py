from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from .nudge_log import read_nudge_log


def _parse_ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def load_sent_nudges_today(now: datetime, rows: Optional[List[Dict[str, Any]]] = None) -> Dict[str, List[Dict[str, Any]]]:
    log_rows = rows if rows is not None else read_nudge_log()
    today = now.date()
    sent_nudges_today: List[Dict[str, Any]] = []
    for row in log_rows:
        if not row.get("send"):
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
                "nudge_type": row.get("nudge_type", ""),
                "domain": row.get("domain", ""),
                "message_fingerprint": row.get("message_fingerprint", ""),
                "message_intent": row.get("message_intent") or row.get("nudge_type"),
                "fingerprint": row.get("fingerprint") or row.get("message_fingerprint"),
                "send": True,
                "delivery_status": row.get("delivery_status"),
                "delivery_error": row.get("delivery_error"),
            }
        )
    return {"sent_nudges_today": sent_nudges_today}
