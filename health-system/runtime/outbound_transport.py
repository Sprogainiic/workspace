from __future__ import annotations

from typing import Dict, Optional

from .config import OPENCLAW_HEALTH_SESSION_KEY
from .transports.openclaw_session_transport import build_session_message
from .nudge_session_launcher import launch_to_session


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
    launcher_mode: str = "local_test",
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
            "launcher_mode": launcher_mode,
        }
    if channel == "test":
        return {
            "channel": channel,
            "recipient_id": recipient_id,
            "message_text": message_text,
            "sent": True,
            "delivery_status": "sent",
            "delivery_error": None,
            "launcher_mode": launcher_mode,
        }
    if channel == "openclaw_session":
        effective_session_key = session_key or OPENCLAW_HEALTH_SESSION_KEY
        payload = build_session_message(message_text, metadata)
        if session_sender is None:
            raise UnsupportedTransportError("openclaw_session requires session_sender")
        launch = launch_to_session({"session_key": effective_session_key, "payload": payload}, session_sender)
        return {
            "channel": channel,
            "recipient_id": recipient_id,
            "session_key": effective_session_key,
            "target_type": target_type,
            "message_text": message_text,
            "payload": payload,
            "sent": launch["status"] == "sent",
            "delivery_status": launch["status"],
            "delivery_error": launch["delivery_error"],
            "launcher_mode": launcher_mode,
        }
    raise UnsupportedTransportError(f"Unsupported outbound channel: {channel}")
