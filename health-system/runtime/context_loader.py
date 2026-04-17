from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "runtime" / "data"


def _read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text())


def _read_jsonl(path: Path) -> List[Any]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows


def _token_estimate(payload: Any) -> int:
    text = json.dumps(payload, ensure_ascii=False)
    return max(1, (len(text) + 3) // 4)


def _latest(path: Path) -> Any:
    return _read_json(path, {})


def load_context(decision_complexity: str = "low", unresolved: bool = False, still_unresolved: bool = False) -> Dict[str, Any]:
    layers_used: List[str] = []
    context_payload: Dict[str, Any] = {}

    snapshot = _latest(DATA / "snapshots" / "current_state_snapshot.json")
    context_payload["snapshot"] = snapshot
    layers_used.append("snapshot")

    if decision_complexity == "medium":
        context_payload["daily_summary"] = _latest(DATA / "daily_summaries" / "latest.json")
        layers_used.append("daily_summary")
        events = _read_jsonl(DATA / "events" / "events.jsonl")
        strava_recent = [e for e in events if e.get('facts', {}).get('source') == 'strava'][-3:]
        if strava_recent:
            context_payload["recent_strava"] = strava_recent
            layers_used.append("recent_strava")
    elif decision_complexity == "high":
        context_payload["weekly_summary"] = _latest(DATA / "weekly_summaries" / "latest.json")
        layers_used.append("weekly_summary")
        context_payload["daily_summary"] = _latest(DATA / "daily_summaries" / "latest.json")
        layers_used.append("daily_summary")
        events = _read_jsonl(DATA / "events" / "events.jsonl")
        strava_recent = [e for e in events if e.get('facts', {}).get('source') == 'strava'][-5:]
        if strava_recent:
            context_payload["recent_strava"] = strava_recent
            layers_used.append("recent_strava")

    if unresolved:
        events = _read_jsonl(DATA / "events" / "events.jsonl")
        context_payload = {"structured_events": events[-5:]}
        layers_used = ["structured_events"]

    if still_unresolved:
        raw_chat = _read_json(DATA / "raw_chat" / "recent.json", [])
        context_payload = {"raw_chat_excerpts": raw_chat[-2:]}
        layers_used = ["raw_chat_excerpts"]

    return {
        "context_payload": context_payload,
        "token_estimate": _token_estimate(context_payload),
        "layers_used": layers_used,
    }
