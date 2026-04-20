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
            'delivery_event_type': 'failed',
            'provider_confirmed': False,
            'provider_message_id': None,
            'provider_sent_at': None,
            'provider_error': 'command_timeout',
            'provider_cli_status': 'timeout',
            'raw': '',
        }
    if proc.returncode != 0:
        return {
            'delivery_event_type': 'failed',
            'provider_confirmed': False,
            'provider_message_id': None,
            'provider_sent_at': None,
            'provider_error': (proc.stderr or proc.stdout or '').strip() or f'command_failed:{proc.returncode}',
            'provider_cli_status': 'failed',
            'raw': proc.stdout,
        }
    parsed = None
    try:
        parsed = json.loads(proc.stdout) if proc.stdout.strip() else {}
    except Exception:
        parsed = {'raw': proc.stdout.strip()}
    provider_message_id = None
    provider_sent_at = None
    if isinstance(parsed, dict):
        provider_message_id = parsed.get('id') or parsed.get('message_id')
        provider_sent_at = parsed.get('sent_at')
    return {
        'delivery_event_type': 'delivered',
        'provider_confirmed': True,
        'provider_message_id': provider_message_id,
        'provider_sent_at': provider_sent_at,
        'provider_error': None,
        'provider_cli_status': 'sent',
        'raw': parsed,
    }
