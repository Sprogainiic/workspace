from __future__ import annotations

import json
import subprocess
from typing import Any, Dict


def send_discord_direct(recipient_id: str, message_text: str) -> Dict[str, Any]:
    cmd = [
        'openclaw', 'message', 'send',
        '--channel', 'discord',
        '--target', recipient_id,
        '--message', message_text,
        '--json',
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    except subprocess.TimeoutExpired:
        return {
            'sent': False,
            'delivery_status': 'failed',
            'delivery_error': 'command_timeout',
            'raw': '',
        }
    if proc.returncode != 0:
        return {
            'sent': False,
            'delivery_status': 'failed',
            'delivery_error': (proc.stderr or proc.stdout or '').strip() or f'command_failed:{proc.returncode}',
            'raw': proc.stdout,
        }
    parsed = None
    try:
        parsed = json.loads(proc.stdout) if proc.stdout.strip() else {}
    except Exception:
        parsed = {'raw': proc.stdout.strip()}
    return {
        'sent': True,
        'delivery_status': 'sent',
        'delivery_error': None,
        'raw': parsed,
    }
