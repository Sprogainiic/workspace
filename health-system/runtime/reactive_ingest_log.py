from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "runtime" / "data" / "ingest" / "reactive_ingest_log.jsonl"
LOG.parent.mkdir(parents=True, exist_ok=True)


def log_reactive_ingest(entry: Dict[str, Any]) -> Dict[str, Any]:
    row = {
        "timestamp": entry.get("timestamp", ""),
        "session_key": entry.get("session_key", ""),
        "discord_message_id": entry.get("discord_message_id", ""),
        "status": entry.get("status", "failed"),
        "reason": entry.get("reason", ""),
        "event_id": entry.get("event_id", ""),
    }
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row


def read_reactive_ingest_log() -> List[Dict[str, Any]]:
    if not LOG.exists():
        return []
    return [json.loads(line) for line in LOG.read_text(encoding="utf-8").splitlines() if line.strip()]
