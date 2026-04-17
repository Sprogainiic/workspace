from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from runtime.event_store import EVENTS
from runtime.snapshot_updater import update_snapshot
from runtime.strava_client import fetch_recent_activities
from runtime.strava_normalizer import normalize_activities
from runtime.strava_index import load_seen_ids, save_seen_ids

ROOT = Path('/home/sprogainiic/.openclaw/workspace/health-system')
OUT = ROOT / 'runtime' / 'data' / 'strava_ingest_result.json'


def append_events(events):
    appended = []
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
    for ev in events:
        if str(ev.get('event_id', '')) in existing_ids:
            continue
        with EVENTS.open('a', encoding='utf-8') as f:
            f.write(json.dumps(ev, ensure_ascii=False) + '\n')
        appended.append(ev)
    return appended


def ingest_strava(per_page: int = 5, env_path: str | None = None) -> Dict[str, Any]:
    activities = fetch_recent_activities(per_page=per_page, env_path=env_path)
    seen = load_seen_ids()
    new_activities = [a for a in activities if str(a.get('id')) not in seen]
    events = normalize_activities(new_activities)
    appended = append_events(events)
    for a in new_activities:
        seen.add(str(a.get('id')))
    save_seen_ids(seen)
    snapshot = update_snapshot(appended)
    result = {
        'activities_fetched': len(activities),
        'new_activities': len(new_activities),
        'events_written': len(appended),
        'latest_event_ids': [e['event_id'] for e in appended[:6]],
        'event_store_path': str(EVENTS),
        'snapshot_updated': bool(snapshot)
    }
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False))
    return result


if __name__ == '__main__':
    print(json.dumps(ingest_strava(), indent=2, ensure_ascii=False))
