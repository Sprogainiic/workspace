from __future__ import annotations

from typing import Any, Dict, List
import json
from pathlib import Path

from .chat_flow import run_chat_turn

ROOT = Path(__file__).resolve().parents[1]
EVENTS = ROOT / 'runtime' / 'data' / 'events' / 'events.jsonl'


def _latest_recent_strava(context: Dict[str, Any]) -> Dict[str, Any] | None:
    recent = ((context or {}).get('context_payload', {}) or {}).get('recent_strava', [])
    if recent:
        return recent[-1]
    if EVENTS.exists():
        rows = []
        for line in EVENTS.read_text(encoding='utf-8').splitlines():
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if row.get('event_type') == 'activity_logged' and row.get('facts', {}).get('source') == 'strava':
                rows.append(row)
        if rows:
            return rows[-1]
    return None


def build_reactive_reply(message_text: str, message_id: str, timestamp: str) -> Dict[str, Any]:
    turn = run_chat_turn(message_text, message_id, timestamp)
    lowered = message_text.lower()
    context = turn.get('context', {}) or {}
    snapshot = turn.get('snapshot', {}) or {}
    latest_strava = _latest_recent_strava(context)

    if 'strava' in lowered or 'ride' in lowered:
        if latest_strava:
            facts = latest_strava.get('facts', {}) or {}
            name = facts.get('name') or facts.get('sport_type') or 'activity'
            distance = facts.get('distance_m')
            duration = facts.get('duration_sec')
            hr = facts.get('average_heartrate')
            details: List[str] = []
            if distance:
                details.append(f"distance about {round(float(distance)/1000, 1)} km")
            if duration:
                details.append(f"moving time about {int(float(duration)//60)} min")
            if hr:
                details.append(f"avg HR about {int(float(hr))}")
            detail_text = ', '.join(details)
            text = f"Yes — I can see your recent Strava {name.lower()} now."
            if detail_text:
                text += f" I currently have {detail_text}."
            return {
                'status': 'ok',
                'message_text': text,
                'source': 'health_runtime_reactive',
                'used_recent_strava': True,
            }
        return {
            'status': 'ok',
            'message_text': 'I do not have usable Strava activity in runtime state yet. If it should be there, the import path still needs attention.',
            'source': 'health_runtime_reactive',
            'used_recent_strava': False,
        }

    if 'message_text' in turn:
        return {
            'status': 'ok',
            'message_text': turn['message_text'],
            'source': 'health_runtime_reactive',
            'used_recent_strava': False,
        }

    routing = turn.get('routing', []) or []
    if 'Dietitian' in routing:
        return {'status': 'ok', 'message_text': 'Give me the food details and I’ll help you tighten it up.', 'source': 'health_runtime_reactive', 'used_recent_strava': False}
    if 'Fitness Coach' in routing:
        return {'status': 'ok', 'message_text': 'Give me today’s training/fatigue state and I’ll help you adjust it.', 'source': 'health_runtime_reactive', 'used_recent_strava': False}
    return {'status': 'ok', 'message_text': 'Got it.', 'source': 'health_runtime_reactive', 'used_recent_strava': False}
