from __future__ import annotations

from typing import Any, Dict


def launch_to_session(input_payload: Dict[str, Any], session_sender) -> Dict[str, Any]:
    session_key = input_payload.get("session_key")
    payload = input_payload.get("payload")
    if not session_key:
        return {"status": "failed", "session_key": "", "delivery_error": "missing_session_key"}
    if not isinstance(payload, dict):
        return {"status": "failed", "session_key": session_key, "delivery_error": "malformed_payload"}
    required = ["kind", "message_text", "slot", "nudge_type", "domain", "source"]
    if any(key not in payload for key in required):
        return {"status": "failed", "session_key": session_key, "delivery_error": "malformed_payload"}
    try:
        session_sender(sessionKey=session_key, message=str(payload), timeoutSeconds=30)
    except Exception as exc:
        return {"status": "failed", "session_key": session_key, "delivery_error": str(exc)}
    return {"status": "sent", "session_key": session_key, "delivery_error": None}
