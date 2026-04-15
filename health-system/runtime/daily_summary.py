from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "runtime" / "data"
OUT = DATA / "daily_summaries" / "latest.json"
OUT.parent.mkdir(parents=True, exist_ok=True)


def generate_daily_summary(structured_events: List[Dict[str, Any]], snapshot_delta: Dict[str, Any]) -> Dict[str, Any]:
    strava_activities = [e for e in structured_events if e.get('event_type') == 'activity_logged' and e.get('facts', {}).get('source') == 'strava']
    outcome_events = [e for e in structured_events if e.get('facts', {}).get('counts_as_outcome')]
    completion_scores = [e.get('facts', {}).get('outcome_score') for e in outcome_events if isinstance(e.get('facts', {}).get('outcome_score'), (int, float))]
    facts = {
        "events_count": len(structured_events),
        "event_types": [e.get("event_type") for e in structured_events],
        "strava_activities": [
            {
                'source_id': e.get('facts', {}).get('source_id'),
                'sport_type': e.get('facts', {}).get('sport_type'),
                'duration_sec': e.get('facts', {}).get('duration_sec'),
                'distance_m': e.get('facts', {}).get('distance_m')
            } for e in strava_activities
        ]
    }
    state_signals = {
        "snapshot_delta_fields": list(snapshot_delta.get("state", {}).keys()) if snapshot_delta else [],
    }
    adherence_observations = {
        "adherence_signal": snapshot_delta.get("state", {}).get("adherence", {}).get("value") if snapshot_delta else None,
        "behavior_signal": snapshot_delta.get("state", {}).get("behavior_state", {}).get("value") if snapshot_delta else None,
    }
    risk_flags = snapshot_delta.get("risk_flags", []) if snapshot_delta else []
    tone_state = snapshot_delta.get("tone_adaptation", {}) if snapshot_delta else {}
    summary = {
        "date": structured_events[-1]["timestamp"][:10] if structured_events else "",
        "facts": facts,
        "state_signals": state_signals,
        "adherence_observations": adherence_observations,
        "risk_flags": risk_flags,
        "outcome_tracking": {
            "observed_outcomes_count": len(outcome_events),
            "outcome_labels": [e.get('facts', {}).get('outcome_label') for e in outcome_events if e.get('facts', {}).get('outcome_label')],
            "completion_score": round(sum(completion_scores) / len(completion_scores), 3) if completion_scores else None,
        },
        "tone_adaptation": {
            "suggested_style": tone_state.get("suggested_style"),
            "evidence": tone_state.get("evidence", []),
        },
        "weekly_reflection_inputs": {
            "reflection_notes": tone_state.get("reflection_notes", []),
            "behavior_state": snapshot_delta.get("state", {}).get("behavior_state", {}).get("value") if snapshot_delta else None,
        },
        "derived_interpretation": {
            "note": "derived from structured events only",
            "confidence": "medium" if structured_events else "low",
        },
        "open_uncertainties": snapshot_delta.get("open_ambiguities", []) if snapshot_delta else [],
    }
    OUT.write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    return summary
