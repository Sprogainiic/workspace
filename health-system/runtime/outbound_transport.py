from __future__ import annotations

from typing import Dict, Optional

from .config import OPENCLAW_HEALTH_SESSION_KEY
from .transports.discord_direct_transport import send_discord_direct
from .transports.discord_adapter import adapt_openclaw_session_payload
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
        payload = adapt_openclaw_session_payload(message_text, metadata)
        if session_sender is not None:
            result = launch_to_session(
                {"session_key": session_key or OPENCLAW_HEALTH_SESSION_KEY, "payload": payload},
                session_sender=session_sender,
            )
            return {
                "channel": "openclaw_session",
                "recipient_id": recipient_id,
                "session_key": session_key or OPENCLAW_HEALTH_SESSION_KEY,
                "target_type": target_type,
                "message_text": message_text,
                "payload_kind": payload.get("kind"),
                "sent": result.get("status") == "sent",
                "delivery_status": "sent" if result.get("status") == "sent" else "failed",
                "delivery_error": result.get("delivery_error"),
                "launcher_mode": launcher_mode,
                "raw": result,
            }
        direct = send_discord_direct(recipient_id, message_text)
        return {
            "channel": "discord_direct_fallback",
            "recipient_id": recipient_id,
            "session_key": session_key or OPENCLAW_HEALTH_SESSION_KEY,
            "target_type": target_type,
            "message_text": message_text,
            "payload_kind": "discord_direct_message",
            "sent": bool(direct["sent"]),
            "delivery_status": direct["delivery_status"],
            "delivery_error": direct["delivery_error"],
            "launcher_mode": launcher_mode,
            "raw": direct.get("raw"),
        }
    if channel == "discord_direct":
        direct = send_discord_direct(recipient_id, message_text)
        return {
            "channel": "discord_direct",
            "recipient_id": recipient_id,
            "session_key": session_key or OPENCLAW_HEALTH_SESSION_KEY,
            "target_type": target_type,
            "message_text": message_text,
            "payload_kind": "discord_direct_message",
            "sent": bool(direct["sent"]),
            "delivery_status": direct["delivery_status"],
            "delivery_error": direct["delivery_error"],
            "launcher_mode": launcher_mode,
            "raw": direct.get("raw"),
        }
    raise UnsupportedTransportError(f"Unsupported outbound channel: {channel}")
