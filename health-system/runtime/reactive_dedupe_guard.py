from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

ROOT = Path(__file__).resolve().parents[1]
SEEN = ROOT / "runtime" / "data" / "ingest" / "reactive_seen.json"
SEEN.parent.mkdir(parents=True, exist_ok=True)


def _load() -> Dict[str, bool]:
    if not SEEN.exists():
        return {}
    return json.loads(SEEN.read_text(encoding="utf-8"))


def _save(data: Dict[str, bool]) -> None:
    SEEN.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def check_and_mark(session_key: str, discord_message_id: str) -> bool:
    key = f"{session_key}:{discord_message_id}"
    seen = _load()
    if key in seen:
        return False
    seen[key] = True
    _save(seen)
    return True
