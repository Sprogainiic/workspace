from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo

from .nudge_state_loader import load_sent_nudges_today
from .user_activity_loader import load_recent_user_activity
from .nudge_schedule import DEFAULT_LOCAL_TIMEZONE

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "runtime" / "data"
SNAPSHOT_PATH = DATA / "snapshots" / "current_state_snapshot.json"
EVENTS_PATH = DATA / "events" / "events.jsonl"
DAILY_SUMMARY_PATH = DATA / "daily_summaries" / "latest.json"
WEEKLY_SUMMARY_PATH = DATA / "weekly_summaries" / "latest.json"


class MissingRuntimeStateError(RuntimeError):
    pass


def _read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows


def _parse_ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def load_runtime_state(now: datetime, *, allow_test_fixture: bool = False, fixture: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    if allow_test_fixture and fixture is not None:
        return {
            "snapshot": fixture.get("snapshot", {}),
            "today_events": fixture.get("today_events", []),
            "daily_summary": fixture.get("daily_summary", {}),
            "weekly_summary": fixture.get("weekly_summary", {}),
            "sent_nudges_today": fixture.get("sent_nudges_today", []),
            "recent_user_activity": fixture.get("recent_user_activity", []),
            "activity_source": fixture.get("activity_source", "missing"),
            "state_source": "test_fixture",
        }

    missing = []
    if not SNAPSHOT_PATH.exists():
        missing.append("snapshot")
    if not EVENTS_PATH.exists():
        missing.append("events")
    if missing:
        raise MissingRuntimeStateError("missing_runtime_state")

    snapshot = _read_json(SNAPSHOT_PATH)
    all_events = _read_jsonl(EVENTS_PATH)
    today_events = []
    local_tz = ZoneInfo(DEFAULT_LOCAL_TIMEZONE)
    now_local_date = now.astimezone(local_tz).date()
    for row in all_events:
        timestamp = row.get("timestamp")
        if not timestamp:
            continue
        try:
            ts = _parse_ts(timestamp)
        except ValueError:
            continue
        if ts.astimezone(local_tz).date() == now_local_date:
            today_events.append(row)

    daily_summary = _read_json(DAILY_SUMMARY_PATH) if DAILY_SUMMARY_PATH.exists() else {}
    weekly_summary = _read_json(WEEKLY_SUMMARY_PATH) if WEEKLY_SUMMARY_PATH.exists() else {}
    sent_nudges_today = load_sent_nudges_today(now).get("sent_nudges_today", [])
    activity = load_recent_user_activity(now)
    return {
        "snapshot": snapshot,
        "today_events": today_events,
        "daily_summary": daily_summary,
        "weekly_summary": weekly_summary,
        "sent_nudges_today": sent_nudges_today,
        "recent_user_activity": activity["recent_user_activity"],
        "activity_source": activity["activity_source"],
        "state_source": "persisted",
    }
