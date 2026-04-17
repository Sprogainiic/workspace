from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from runtime.event_store import EVENTS
from runtime.snapshot_updater import update_snapshot
from runtime.strava_normalizer import normalize_activities

ROOT = Path('/home/sprogainiic/.openclaw/workspace/health-system')
RECENT = ROOT / 'runtime' / 'data' / 'strava' / 'recent_activities.json'
OUT = ROOT / 'runtime' / 'data' / 'strava_backfill_result.json'


def _load_recent() -> List[Dict[str, Any]]:
    if not RECENT.exists():
        return []
    data = json.loads(RECENT.read_text(encoding='utf-8'))
    return data if isinstance(data, list) else []


def backfill_recent_strava_to_event_store() -> Dict[str, Any]:
    activities = _load_recent()
    normalized = normalize_activities(activities)
    existing_ids = set()
    if EVENTS.exists():
        for line in EVENTS.read_text(encoding='utf-8').splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except Exception:
                continue
            existing_ids.add(str(row.get('event_id', '')))

    appended = []
    for ev in normalized:
        if ev['event_id'] in existing_ids:
            continue
        with EVENTS.open('a', encoding='utf-8') as f:
            f.write(json.dumps(ev, ensure_ascii=False) + '\n')
        appended.append(ev)

    snapshot = update_snapshot(appended)
    result = {
        'activities_seen': len(activities),
        'normalized_events': len(normalized),
        'events_backfilled': len(appended),
        'snapshot_updated': bool(snapshot),
        'event_ids': [ev['event_id'] for ev in appended[:12]],
    }
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
    return result


if __name__ == '__main__':
    print(json.dumps(backfill_recent_strava_to_event_store(), indent=2, ensure_ascii=False))
