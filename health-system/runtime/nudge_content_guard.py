from __future__ import annotations

import hashlib
from typing import Dict, List, Tuple


def fingerprint_nudge(slot: str, domain: str, message_intent: str, payload_brief: Dict) -> str:
    raw = f"{slot}|{domain}|{message_intent}|{sorted(payload_brief.items())}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def content_guard_decision(
    slot: str,
    domain: str,
    message_intent: str,
    payload_brief: Dict,
    sent_nudges_today: List[Dict],
) -> Tuple[bool, str]:
    fingerprint = fingerprint_nudge(slot, domain, message_intent, payload_brief)
    for row in sent_nudges_today:
        if not row.get("send"):
            continue
        same_slot = row.get("slot") == slot
        same_domain = row.get("domain") == domain
        same_intent = row.get("message_intent") == message_intent
        same_fp = row.get("fingerprint") == fingerprint
        if same_fp or (same_slot and same_domain and same_intent):
            return False, fingerprint
    return True, fingerprint
