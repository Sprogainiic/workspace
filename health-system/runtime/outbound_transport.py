from __future__ import annotations

from typing import Dict


def send_message(channel: str, recipient_id: str, message_text: str) -> Dict[str, object]:
    if channel not in {"test", "console"}:
        raise ValueError(f"Unsupported outbound channel: {channel}")
    if channel == "console":
        print(f"[{recipient_id}] {message_text}")
    return {
        "channel": channel,
        "recipient_id": recipient_id,
        "message_text": message_text,
        "sent": True,
    }
