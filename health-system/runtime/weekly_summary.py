from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "runtime" / "data"
DAILY_DIR = DATA / "daily_summaries"
WEEKLY_OUT = DATA / "weekly_summaries" / "latest.json"
WEEKLY_OUT.parent.mkdir(parents=True, exist_ok=True)


def _read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _parse_date(value: str) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _collect_daily_summaries(window_end: datetime, days: int = 7) -> List[Dict[str, Any]]:
    latest = _read_json(DAILY_DIR / "latest.json", {})
    dated_rows: List[Dict[str, Any]] = []
    if latest:
        dated_rows.append(latest)

    cutoff = window_end.date() - timedelta(days=days - 1)
    for path in sorted(DAILY_DIR.glob("*.json")):
        if path.name == "latest.json":
            continue
        row = _read_json(path, {})
        if not row:
            continue
        dt = _parse_date(row.get("date", ""))
        if dt is None:
            continue
        if cutoff <= dt.date() <= window_end.date():
            dated_rows.append(row)

    unique: Dict[str, Dict[str, Any]] = {}
    for row in dated_rows:
        date_key = row.get("date")
        if date_key:
            unique[date_key] = row
    return [unique[k] for k in sorted(unique.keys())]


def generate_weekly_summary(window_end: datetime, daily_summaries: List[Dict[str, Any]] | None = None) -> Dict[str, Any]:
    rows = daily_summaries if daily_summaries is not None else _collect_daily_summaries(window_end)
    dates = [row.get("date") for row in rows if row.get("date")]
    week_start = min(dates) if dates else str((window_end.date() - timedelta(days=6)))
    week_end = max(dates) if dates else str(window_end.date())

    total_events = sum((row.get("facts", {}) or {}).get("events_count", 0) for row in rows)
    behavior_signals = [
        ((row.get("adherence_observations", {}) or {}).get("behavior_signal"))
        for row in rows
        if (row.get("adherence_observations", {}) or {}).get("behavior_signal")
    ]
    adherence_signals = [
        ((row.get("adherence_observations", {}) or {}).get("adherence_signal"))
        for row in rows
        if (row.get("adherence_observations", {}) or {}).get("adherence_signal")
    ]
    outcome_scores = [
        ((row.get("outcome_tracking", {}) or {}).get("completion_score"))
        for row in rows
        if isinstance((row.get("outcome_tracking", {}) or {}).get("completion_score"), (int, float))
    ]
    observed_counts = [
        ((row.get("outcome_tracking", {}) or {}).get("observed_outcomes_count", 0))
        for row in rows
    ]
    risk_flags = sorted({flag for row in rows for flag in (row.get("risk_flags", []) or [])})
    explicit_reflection_notes = [
        note
        for row in rows
        for note in ((row.get("weekly_reflection_inputs", {}) or {}).get("reflection_notes", []) or [])
        if note
    ]

    avg_completion = round(sum(outcome_scores) / len(outcome_scores), 3) if outcome_scores else None
    frequent_behavior = max(set(behavior_signals), key=behavior_signals.count) if behavior_signals else None
    frequent_adherence = max(set(adherence_signals), key=adherence_signals.count) if adherence_signals else None

    trend_signals = {
        "days_with_data": len(rows),
        "avg_completion_score": avg_completion,
        "dominant_behavior_signal": frequent_behavior,
        "dominant_adherence_signal": frequent_adherence,
        "observed_outcomes_total": sum(observed_counts),
    }

    interpretation_summary = []
    if avg_completion is not None:
        if avg_completion >= 0.7:
            interpretation_summary.append("Observed completion held up reasonably well on days with outcome evidence.")
        elif avg_completion >= 0.4:
            interpretation_summary.append("Observed completion was mixed; some outcomes landed, but consistency was uneven.")
        else:
            interpretation_summary.append("Observed completion stayed low across the available evidence.")
    if frequent_behavior:
        interpretation_summary.append(f"Most common behavior pattern this week: {frequent_behavior}.")
    if explicit_reflection_notes:
        interpretation_summary.append("Reflection inputs captured repeated friction or wins worth carrying into next week.")
    if not interpretation_summary:
        interpretation_summary.append("Weekly reflection is limited because only sparse daily evidence is available.")

    confidence_notes = []
    if len(rows) < 4:
        confidence_notes.append("Weekly reflection is low confidence because fewer than four daily summaries were available.")
    if not outcome_scores:
        confidence_notes.append("No completion scores were available, so outcome-trend interpretation is limited.")
    if sum(observed_counts) == 0:
        confidence_notes.append("No explicit observed outcomes were logged in daily summaries.")

    next_week_implications: List[str] = []
    if frequent_behavior == "restart_cycle":
        next_week_implications.append("Bias toward simpler restarts and lower-friction recovery after misses.")
    if frequent_behavior == "fragile_but_not_collapsed" or frequent_behavior == "fragile":
        next_week_implications.append("Preserve momentum with shorter check-ins and minimum-viable asks.")
    if avg_completion is not None and avg_completion < 0.5:
        next_week_implications.append("Track smaller daily outcomes so progress is visible before motivation drops.")
    if not next_week_implications:
        next_week_implications.append("Keep using outcome-based check-ins to separate effort from actual follow-through.")

    summary = {
        "week_start": week_start,
        "week_end": week_end,
        "week_facts": {
            "days_with_data": len(rows),
            "total_events": total_events,
            "observed_outcomes_total": sum(observed_counts),
            "reflection_note_count": len(explicit_reflection_notes),
        },
        "trend_signals": trend_signals,
        "interpretation": {
            "summary": " ".join(interpretation_summary),
            "reflection_notes": explicit_reflection_notes[-5:],
        },
        "confidence_notes": confidence_notes,
        "risk_flags": risk_flags,
        "next_week_implications": next_week_implications,
    }
    WEEKLY_OUT.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    return summary
