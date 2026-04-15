from __future__ import annotations

from typing import Dict, Optional

from .config import OPENCLAW_HEALTH_SESSION_KEY
from .transports.openclaw_session_transport import build_session_message


class UnsupportedTransportError(ValueError):
    pass


def send_message(
    channel: str,
    recipient_id: str,
    message_text: str,
    *,
    session_key: Optional[str] = None,
    target_type: str = "dm",
    metadata: Optional[Dict[str, str]] = None,
    session_sender=None,
) -> Dict[str, object]:
    metadata = metadata or {}
    if channel == "console":
        print(f"[{recipient_id}] {message_text}")
        return {
            "channel": channel,
            "recipient_id": recipient_id,
            "message_text": message_text,
            "sent": True,
            "delivery_status": "sent",
            "delivery_error": None,
        }
    if channel == "test":
        return {
            "channel": channel,
            "recipient_id": recipient_id,
            "message_text": message_text,
            "sent": True,
            "delivery_status": "sent",
            "delivery_error": None,
        }
    if channel == "openclaw_session":
        effective_session_key = session_key or OPENCLAW_HEALTH_SESSION_KEY
        payload = build_session_message(message_text, metadata)
        if session_sender is None:
            raise UnsupportedTransportError("openclaw_session requires session_sender")
        result = session_sender(sessionKey=effective_session_key, message=str(payload), timeoutSeconds=30)
        return {
            "channel": channel,
            "recipient_id": recipient_id,
            "session_key": effective_session_key,
            "target_type": target_type,
            "message_text": message_text,
            "payload": payload,
            "sent": True,
            "delivery_status": "sent",
            "delivery_error": None,
            "result": result,
        }
    raise UnsupportedTransportError(f"Unsupported outbound channel: {channel}")
