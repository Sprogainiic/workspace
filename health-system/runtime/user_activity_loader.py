from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "runtime" / "data"
EVENTS_PATH = DATA / "events" / "events.jsonl"
TURN_LOG_PATH = DATA / "turn_logs" / "reactive_turns.jsonl"
CHAT_LOG_PATH = DATA / "raw_chat" / "recent.json"

EVENT_SIGNAL_MAP = {
    "meal_logged": "meal_log",
    "fatigue_report": "status_update",
    "motivation_signal": "status_update",
    "restart_signal": "decision_request",
    "checkin_signal": "checkin_reply",
    "workout_skipped": "status_update",
}


def _parse_ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _read_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    rows: List[Dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows


def _read_json(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def load_recent_user_activity(now: datetime, lookback_minutes: int = 45) -> Dict[str, Any]:
    cutoff = now - timedelta(minutes=lookback_minutes)
    activity: List[Dict[str, Any]] = []
    found_source = False

    if EVENTS_PATH.exists():
        found_source = True
        for row in _read_jsonl(EVENTS_PATH):
            ts_raw = row.get("timestamp")
            if not ts_raw:
                continue
            try:
                ts = _parse_ts(ts_raw)
            except ValueError:
                continue
            if ts < cutoff:
                continue
            activity.append(
                {
                    "timestamp": ts_raw,
                    "source": "event",
                    "signal_type": EVENT_SIGNAL_MAP.get(row.get("event_type"), "other"),
                }
            )

    if TURN_LOG_PATH.exists():
        found_source = True
        for row in _read_jsonl(TURN_LOG_PATH):
            ts_raw = row.get("timestamp")
            if not ts_raw:
                continue
            try:
                ts = _parse_ts(ts_raw)
            except ValueError:
                continue
            if ts < cutoff:
                continue
            activity.append(
                {
                    "timestamp": ts_raw,
                    "source": "turn_log",
                    "signal_type": row.get("signal_type", "other"),
                }
            )

    if CHAT_LOG_PATH.exists():
        found_source = True
        for row in _read_json(CHAT_LOG_PATH):
            ts_raw = row.get("timestamp")
            if not ts_raw:
                continue
            try:
                ts = _parse_ts(ts_raw)
            except ValueError:
                continue
            if ts < cutoff:
                continue
            activity.append(
                {
                    "timestamp": ts_raw,
                    "source": "chat",
                    "signal_type": row.get("signal_type", "other"),
                }
            )

    activity.sort(key=lambda row: row["timestamp"])
    return {
        "recent_user_activity": activity,
        "activity_source": "persisted" if found_source else "missing",
    }
