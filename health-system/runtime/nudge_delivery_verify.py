from __future__ import annotations

from typing import Any, Dict, List
from datetime import datetime, timedelta

from .session_history_client import fetch_session_history


def _content_to_text(content: List[Dict[str, Any]] | Any) -> str:
    if not isinstance(content, list):
        return ""
    parts = []
    for part in content:
        if isinstance(part, dict) and part.get("type") == "text":
            parts.append(part.get("text", ""))
    return "\n".join(parts)


def verify_message_in_session_history(
    session_key: str,
    expected_text: str,
    *,
    limit: int = 20,
    earliest_timestamp: str | None = None,
    sessions_history_tool=None,
) -> Dict[str, Any]:
    history = fetch_session_history(session_key, limit=limit, sessions_history_tool=sessions_history_tool)
    if history.get("status") != "ok":
        return {
            "verified": False,
            "status": "failed",
            "error": history.get("error"),
            "matched_event": None,
        }

    earliest_dt = None
    if earliest_timestamp:
        try:
            earliest_dt = datetime.fromisoformat(earliest_timestamp)
        except Exception:
            earliest_dt = None

    for event in reversed(history.get("events", [])):
        text = _content_to_text(event.get("content"))
        if not (expected_text and expected_text in text):
            continue
        if earliest_dt is not None:
            event_ts = event.get("timestamp")
            if not event_ts:
                continue
            try:
                event_dt = datetime.fromisoformat(str(event_ts))
            except Exception:
                continue
            if event_dt < (earliest_dt - timedelta(seconds=5)):
                continue
        return {
            "verified": True,
            "status": "ok",
            "error": None,
            "matched_event": event,
        }

    return {
        "verified": False,
        "status": "ok",
        "error": "message_not_found",
        "matched_event": None,
    }
