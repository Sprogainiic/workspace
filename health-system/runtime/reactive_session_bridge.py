from __future__ import annotations

import json
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from .reactive_session_ingest import ingest_reactive_session_event
from .reactive_reply import build_reactive_reply

ROOT = Path(__file__).resolve().parents[1]
INGEST_DIR = ROOT / "runtime" / "data" / "ingest"
INGEST_DIR.mkdir(parents=True, exist_ok=True)
BRIDGE_LOG = INGEST_DIR / "reactive_bridge_log.jsonl"
PRE_INGEST_LOG = INGEST_DIR / "reactive_bridge_pre_ingest.jsonl"

PRE_INGEST_ROTATION_BYTES = 25 * 1024 * 1024
PRE_INGEST_RETENTION_COUNT = 3
_PRE_INGEST_LOCK = threading.Lock()


def _pre_ingest_archives() -> List[Path]:
    return sorted(
        [p for p in INGEST_DIR.glob("reactive_bridge_pre_ingest.*.jsonl") if p.name != PRE_INGEST_LOG.name],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )


def _rotate_pre_ingest_if_needed(path: Path = PRE_INGEST_LOG) -> None:
    if not path.exists() or path.stat().st_size < PRE_INGEST_ROTATION_BYTES:
        return
    stamp = datetime.now().astimezone().strftime("%Y%m%dT%H%M%S")
    archive = INGEST_DIR / f"reactive_bridge_pre_ingest.{stamp}.jsonl"
    path.rename(archive)
    path.touch(exist_ok=True)
    for old in _pre_ingest_archives()[PRE_INGEST_RETENTION_COUNT:]:
        try:
            old.unlink()
        except FileNotFoundError:
            pass


def _append_jsonl(path: Path, row: Dict[str, Any]) -> Dict[str, Any]:
    with _PRE_INGEST_LOCK:
        if path == PRE_INGEST_LOG:
            _rotate_pre_ingest_if_needed(path)
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row


def log_bridge_event(entry: Dict[str, Any]) -> Dict[str, Any]:
    row = {
        "timestamp": entry.get("timestamp", ""),
        "session_key": entry.get("session_key", ""),
        "discord_message_id": entry.get("discord_message_id", ""),
        "origin": entry.get("origin", "system"),
        "bridge_status": entry.get("bridge_status", "failed"),
        "bridge_reason": entry.get("bridge_reason", ""),
        "runner_mode": entry.get("runner_mode"),
        "poll_iteration": entry.get("poll_iteration", 0),
    }
    return _append_jsonl(BRIDGE_LOG, row)


def log_accepted_pre_ingest(session_key: str, discord_message_id: str, timestamp: str | None = None) -> Dict[str, Any]:
    row = {
        "timestamp": timestamp or datetime.now().astimezone().isoformat(),
        "session_key": session_key,
        "discord_message_id": discord_message_id,
        "bridge_stage": "accepted_pre_ingest",
    }
    return _append_jsonl(PRE_INGEST_LOG, row)


def read_bridge_log() -> List[Dict[str, Any]]:
    if not BRIDGE_LOG.exists():
        return []
    return [json.loads(line) for line in BRIDGE_LOG.read_text(encoding="utf-8").splitlines() if line.strip()]


def process_session_messages(session_key: str, messages: List[Dict[str, Any]], reply_sender=None) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    for message in messages:
        role = message.get("role")
        timestamp = message.get("timestamp", "")
        origin = "user" if role == "user" else ("assistant" if role == "assistant" else "system")
        text_parts = []
        for part in message.get("content", []):
            if isinstance(part, dict) and part.get("type") == "text":
                text_parts.append(part.get("text", ""))
        message_text = "\n".join(part for part in text_parts if part).strip()
        message_id = message.get("__openclaw", {}).get("id", "")
        sender_label = message.get("senderLabel", "")

        if origin != "user":
            results.append(log_bridge_event({
                "timestamp": timestamp,
                "session_key": session_key,
                "discord_message_id": message_id,
                "origin": origin,
                "bridge_status": "ignored",
                "bridge_reason": "non_user_origin",
            }))
            continue
        if not message_text or not message_id:
            results.append(log_bridge_event({
                "timestamp": timestamp,
                "session_key": session_key,
                "discord_message_id": message_id,
                "origin": origin,
                "bridge_status": "ignored",
                "bridge_reason": "malformed_event",
            }))
            continue

        log_accepted_pre_ingest(session_key, message_id, str(timestamp))
        ingest = ingest_reactive_session_event({
            "session_key": session_key,
            "event": {
                "message_text": message_text,
                "user_id": sender_label,
                "message_id": message_id,
                "timestamp": str(timestamp),
                "source_type": "discord_channel",
            },
        })
        status = "accepted" if ingest.get("status") == "accepted" else ("ignored" if ingest.get("status") == "ignored" else "failed")
        reason = ingest.get("ingest_reason", "")
        if status == "accepted" and reply_sender is not None:
            reply = build_reactive_reply(message_text, message_id, str(timestamp))
            reply_sender(sessionKey=session_key, message=reply["message_text"], timeoutSeconds=30)
        results.append(log_bridge_event({
            "timestamp": timestamp,
            "session_key": session_key,
            "discord_message_id": message_id,
            "origin": origin,
            "bridge_status": status,
            "bridge_reason": reason,
        }))
    return results
