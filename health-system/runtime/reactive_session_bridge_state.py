from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
CHECKPOINT = ROOT / 'runtime' / 'data' / 'reactive_bridge_checkpoint.json'
CHECKPOINT.parent.mkdir(parents=True, exist_ok=True)


def load_bridge_checkpoint() -> Dict[str, Any]:
    if not CHECKPOINT.exists():
        return {
            'session_key': '',
            'last_processed_timestamp': '',
            'last_processed_message_id': '',
            'recent_message_ids': [],
        }
    try:
        data = json.loads(CHECKPOINT.read_text(encoding='utf-8'))
    except Exception:
        return {
            'session_key': '',
            'last_processed_timestamp': '',
            'last_processed_message_id': '',
            'recent_message_ids': [],
        }
    data.setdefault('session_key', '')
    data.setdefault('last_processed_timestamp', '')
    data.setdefault('last_processed_message_id', '')
    data.setdefault('recent_message_ids', [])
    return data


def save_bridge_checkpoint(session_key: str, last_processed_timestamp: str, last_processed_message_id: str, recent_message_ids: List[str]) -> None:
    payload = {
        'session_key': session_key,
        'last_processed_timestamp': last_processed_timestamp,
        'last_processed_message_id': last_processed_message_id,
        'recent_message_ids': list(dict.fromkeys(recent_message_ids))[-500:],
    }
    CHECKPOINT.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding='utf-8')
