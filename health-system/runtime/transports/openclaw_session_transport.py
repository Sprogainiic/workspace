from __future__ import annotations

from typing import Dict

from .discord_adapter import adapt_openclaw_session_payload


def build_session_message(message_text: str, metadata: Dict[str, str]) -> Dict[str, object]:
    return adapt_openclaw_session_payload(message_text, metadata)
