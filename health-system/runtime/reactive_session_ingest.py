from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from .chat_flow import memory_adapter
from .validator import validate_memory_adapter_output
from .event_store import store_events
from .snapshot_updater import update_snapshot
from .context_loader import load_context
from .daily_summary import generate_daily_summary
from .reactive_dedupe_guard import check_and_mark
from .reactive_ingest_log import log_reactive_ingest

ROOT = Path(__file__).resolve().parents[1]
INBOUND_LOG = ROOT / "runtime" / "data" / "inbound" / "discord_messages.jsonl"
INBOUND_LOG.parent.mkdir(parents=True, exist_ok=True)


def _persist_inbound(event: Dict[str, Any], session_key: str) -> None:
    row = {
        "timestamp": event.get("timestamp", ""),
        "source_channel": "discord",
        "source_type": "channel",
        "session_key": session_key,
        "discord_user_id": event.get("user_id", ""),
        "discord_message_id": event.get("message_id", ""),
        "message_text": event.get("message_text", ""),
    }
    with INBOUND_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def ingest_reactive_session_event(input_payload: Dict[str, Any]) -> Dict[str, Any]:
    session_key = input_payload.get("session_key", "")
    event = input_payload.get("event", {})
    message_text = event.get("message_text", "")
    user_id = event.get("user_id", "")
    message_id = event.get("message_id", "")
    timestamp = event.get("timestamp", "")
    source_type = event.get("source_type", "")

    if not session_key or not message_text or not user_id or not message_id or not timestamp or source_type != "discord_channel":
        log_reactive_ingest({
            "timestamp": timestamp,
            "session_key": session_key,
            "discord_message_id": message_id,
            "status": "failed",
            "reason": "malformed_event",
            "event_id": "",
        })
        return {"status": "failed", "ingest_reason": "malformed_event", "event_id": ""}

    if not check_and_mark(session_key, message_id):
        log_reactive_ingest({
            "timestamp": timestamp,
            "session_key": session_key,
            "discord_message_id": message_id,
            "status": "ignored",
            "reason": "duplicate",
            "event_id": "",
        })
        return {"status": "ignored", "ingest_reason": "duplicate", "event_id": ""}

    _persist_inbound(event, session_key)
    adapter = memory_adapter(message_text, message_id, timestamp)
    validation = validate_memory_adapter_output(adapter)
    if not validation.get("safe_to_ingest", False):
        log_reactive_ingest({
            "timestamp": timestamp,
            "session_key": session_key,
            "discord_message_id": message_id,
            "status": "failed",
            "reason": "validation_failed",
            "event_id": "",
        })
        return {"status": "failed", "ingest_reason": "validation_failed", "event_id": ""}

    events = store_events(adapter)
    snapshot = update_snapshot(events["appended"])
    context = load_context(decision_complexity="medium", unresolved=False, still_unresolved=False)
    daily = generate_daily_summary(events["appended"], snapshot)
    event_id = events["appended"][0]["event_id"] if events["appended"] else ""
    log_reactive_ingest({
        "timestamp": timestamp,
        "session_key": session_key,
        "discord_message_id": message_id,
        "status": "accepted",
        "reason": "ingested",
        "event_id": event_id,
    })
    return {
        "status": "accepted",
        "ingest_reason": "ingested",
        "event_id": event_id,
        "routing": adapter.get("ROUTING_HINTS", []),
        "snapshot": snapshot,
        "context": context,
        "daily_summary": daily,
    }
