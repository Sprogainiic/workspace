from __future__ import annotations

from typing import Dict


def adapt_openclaw_session_payload(message_text: str, metadata: Dict[str, str]) -> Dict[str, object]:
    return {
        "kind": "proactive_nudge",
        "message_text": message_text,
        "slot": metadata.get("slot", ""),
        "nudge_type": metadata.get("nudge_type", ""),
        "domain": metadata.get("domain", ""),
        "source": "health-system-runtime",
    }
