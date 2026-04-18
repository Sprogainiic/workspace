from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List

DEFAULT_SESSIONS_INDEX = Path.home() / ".openclaw" / "agents" / "health" / "sessions" / "sessions.json"


def _sessions_index_path() -> Path:
    configured = os.getenv("OPENCLAW_SESSIONS_INDEX", "").strip()
    if configured:
        return Path(configured).expanduser()
    return DEFAULT_SESSIONS_INDEX


def _load_session_file(session_key: str) -> Path | None:
    sessions_index = _sessions_index_path()
    if not sessions_index.exists():
        return None
    try:
        index = json.loads(sessions_index.read_text(encoding='utf-8'))
    except Exception:
        return None
    entry = index.get(session_key)
    if not isinstance(entry, dict):
        return None
    session_file = entry.get('sessionFile')
    if not session_file:
        return None
    path = Path(session_file)
    return path if path.exists() else None


def fetch_session_history(session_key: str, limit: int = 50, sessions_history_tool=None) -> Dict[str, Any]:
    if not session_key:
        return {"status": "failed", "events": [], "error": "session_history_unavailable"}

    # Prefer explicit tool boundary when available (tests/agent-context), but prod can use real host file boundary.
    if sessions_history_tool is not None:
        try:
            result = sessions_history_tool(sessionKey=session_key, limit=limit, includeTools=False)
        except Exception:
            return {"status": "failed", "events": [], "error": "session_history_unavailable"}
        messages = result.get("messages")
        if not isinstance(messages, list):
            return {"status": "failed", "events": [], "error": "malformed_session_history_response"}
        return {"status": "ok", "events": messages, "error": None}

    session_file = _load_session_file(session_key)
    if session_file is None:
        return {"status": "failed", "events": [], "error": "session_history_unavailable"}

    try:
        rows: List[Dict[str, Any]] = []
        for line in session_file.read_text(encoding='utf-8').splitlines():
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if row.get('type') != 'message':
                continue
            msg = row.get('message')
            if not isinstance(msg, dict):
                continue
            out = {
                'role': msg.get('role'),
                'timestamp': row.get('timestamp') or msg.get('timestamp'),
                'content': msg.get('content', []),
                '__openclaw': {'id': row.get('id')},
            }
            # derive senderLabel for user messages when possible from metadata text
            if msg.get('role') == 'user':
                text_chunks = []
                for part in msg.get('content', []):
                    if isinstance(part, dict) and part.get('type') == 'text':
                        text_chunks.append(part.get('text', ''))
                text_blob = '\n'.join(text_chunks)
                if 'Sender (untrusted metadata):' in text_blob:
                    try:
                        marker = 'Sender (untrusted metadata):\n```json\n'
                        start = text_blob.index(marker) + len(marker)
                        end = text_blob.index('\n```', start)
                        meta = json.loads(text_blob[start:end])
                        out['senderLabel'] = meta.get('label', '')
                    except Exception:
                        out['senderLabel'] = ''
            rows.append(out)
        if not isinstance(rows, list):
            return {"status": "failed", "events": [], "error": "malformed_session_history_response"}
        return {"status": "ok", "events": rows[-limit:], "error": None}
    except Exception:
        return {"status": "failed", "events": [], "error": "session_history_unavailable"}
