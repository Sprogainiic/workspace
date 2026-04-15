from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "runtime" / "data" / "nudge_logs" / "nudge_log.jsonl"
LOG.parent.mkdir(parents=True, exist_ok=True)


def log_nudge_decision(entry: Dict[str, Any]) -> Dict[str, Any]:
    row = {
        "timestamp": entry.get("timestamp", ""),
        "slot": entry.get("slot", ""),
        "evaluated": bool(entry.get("evaluated", True)),
        "send": bool(entry.get("send", False)),
        "skip_reason": entry.get("skip_reason"),
        "nudge_type": entry.get("nudge_type"),
        "domain": entry.get("domain"),
        "tokens_in": int(entry.get("tokens_in", 0) or 0),
        "tokens_out": int(entry.get("tokens_out", 0) or 0),
        "message_intent": entry.get("message_intent"),
        "fingerprint": entry.get("fingerprint"),
        "message_fingerprint": entry.get("message_fingerprint"),
        "runtime_mode": entry.get("runtime_mode"),
    }
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row


def read_nudge_log() -> List[Dict[str, Any]]:
    if not LOG.exists():
        return []
    rows: List[Dict[str, Any]] = []
    for line in LOG.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows
