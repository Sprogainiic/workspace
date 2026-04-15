from __future__ import annotations

from typing import Any, Dict, List

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

    for event in reversed(history.get("events", [])):
        text = _content_to_text(event.get("content"))
        if expected_text and expected_text in text:
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
