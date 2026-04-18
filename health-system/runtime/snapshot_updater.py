from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from .error_log import log_error

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "runtime" / "data"
SNAP = DATA / "snapshots" / "current_state_snapshot.json"
SNAP.parent.mkdir(parents=True, exist_ok=True)

DEFAULT = {
    "snapshot_id": "snap_initial",
    "updated_at": "",
    "state": {
        "adherence": {"value": None, "confidence": "unsupported", "updated_at": "", "evidence_event_ids": [], "staleness": "stale"},
        "fatigue": {"value": None, "confidence": "unsupported", "updated_at": "", "evidence_event_ids": [], "staleness": "stale"},
        "motivation": {"value": None, "confidence": "unsupported", "updated_at": "", "evidence_event_ids": [], "staleness": "stale"},
        "hunger": {"value": None, "confidence": "unsupported", "updated_at": "", "evidence_event_ids": [], "staleness": "stale"},
        "training_load": {"value": None, "confidence": "unsupported", "updated_at": "", "evidence_event_ids": [], "staleness": "stale"},
        "nutrition_consistency": {"value": None, "confidence": "unsupported", "updated_at": "", "evidence_event_ids": [], "staleness": "stale"},
        "weight_trend": {"value": None, "confidence": "unsupported", "updated_at": "", "evidence_event_ids": [], "staleness": "stale"},
        "behavior_state": {"value": None, "confidence": "unsupported", "updated_at": "", "evidence_event_ids": [], "staleness": "stale"},
        "recent_misses": 0,
        "streak_days": 0,
        "last_training_event_at": None,
        "last_meal_log_at": None,
        "last_weight_at": None,
    },
    "risk_flags": [],
    "simplification_level": "normal",
    "active_modes": [],
    "open_ambiguities": [],
    "tone_adaptation": {
        "suggested_style": "neutral_supportive",
        "evidence": [],
        "reflection_notes": [],
    },
    "outcome_tracking": {
        "last_outcome_at": None,
        "last_outcome_label": None,
        "completion_score_rolling": None,
        "observed_outcomes": 0,
    },
}


def _load() -> Dict[str, Any]:
    if SNAP.exists():
        return json.loads(SNAP.read_text())
    return json.loads(json.dumps(DEFAULT))


def _save(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    SNAP.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False))
    return snapshot


def update_snapshot(structured_events: List[Dict[str, Any]]) -> Dict[str, Any]:
    snapshot = _load()
    snapshot.setdefault("open_ambiguities", [])
    snapshot.setdefault("risk_flags", [])
    snapshot.setdefault("active_modes", [])
    snapshot.setdefault("tone_adaptation", {"suggested_style": "neutral_supportive", "evidence": [], "reflection_notes": []})
    snapshot.setdefault(
        "outcome_tracking",
        {
            "last_outcome_at": None,
            "last_outcome_label": None,
            "completion_score_rolling": None,
            "observed_outcomes": 0,
        },
    )
    for ev in structured_events:
        facts = ev.get("facts", {})
        if not isinstance(facts, dict):
            log_error(
                timestamp=ev.get("timestamp", ""),
                component="snapshot_updater",
                error_type="bad_event_shape",
                event_id=ev.get("event_id", ""),
                event_type=ev.get("event_type", ""),
                reason="structured event facts must be an object",
                raw_event=ev,
            )
            continue
        conf = ev.get("confidence", "low")
        ts = ev.get("timestamp", "")
        # direct field updates from normalized events only
        if ev.get('event_type') == 'training_load_signal' and 'load_level' in facts:
            field = 'training_load'
            conf_use = 'medium' if conf == 'medium' else conf
            prev = snapshot['state'].get(field, {})
            if conf_use == 'high' or prev.get('confidence') in {'low', 'unsupported', None}:
                snapshot['state'][field] = {
                    'value': facts['load_level'],
                    'confidence': conf_use,
                    'updated_at': ts,
                    'evidence_event_ids': [ev.get('event_id', '')],
                    'staleness': 'fresh',
                }
            snapshot['state']['last_training_event_at'] = ts
        for field in ("adherence", "fatigue", "motivation", "hunger", "training_load", "nutrition_consistency", "weight_trend", "behavior_state"):
            if field not in facts:
                continue
            if conf == "high":
                snapshot["state"][field] = {
                    "value": facts[field],
                    "confidence": conf,
                    "updated_at": ts,
                    "evidence_event_ids": [ev.get("event_id", "")],
                    "staleness": "fresh",
                }
            elif conf == "medium":
                prev = snapshot["state"].get(field, {})
                if prev.get("confidence") in {"low", "unsupported", None}:
                    snapshot["state"][field] = {
                        "value": facts[field],
                        "confidence": conf,
                        "updated_at": ts,
                        "evidence_event_ids": [ev.get("event_id", "")],
                        "staleness": "fresh",
                    }
            else:
                snapshot["open_ambiguities"].append(f"{field}:{facts[field]}")
        if facts.get("counts_as_outcome"):
            prior_count = snapshot.get("outcome_tracking", {}).get("observed_outcomes", 0) or 0
            prior_score = snapshot.get("outcome_tracking", {}).get("completion_score_rolling")
            new_score = facts.get("outcome_score") if isinstance(facts.get("outcome_score"), (int, float)) else None
            if new_score is not None:
                if isinstance(prior_score, (int, float)) and prior_count > 0:
                    rolling = round(((prior_score * prior_count) + new_score) / (prior_count + 1), 3)
                else:
                    rolling = round(new_score, 3)
                snapshot["outcome_tracking"]["completion_score_rolling"] = rolling
            snapshot["outcome_tracking"]["observed_outcomes"] = prior_count + 1
            snapshot["outcome_tracking"]["last_outcome_at"] = ts
            snapshot["outcome_tracking"]["last_outcome_label"] = facts.get("outcome_label") or ev.get("event_type")

        tone = snapshot.setdefault("tone_adaptation", {"suggested_style": "neutral_supportive", "evidence": [], "reflection_notes": []})
        if facts.get("counts_as_outcome") and facts.get("outcome_score") == 0.0:
            tone["suggested_style"] = "gentle_low_pressure"
            tone["evidence"] = list(dict.fromkeys((tone.get("evidence") or []) + ["recent_missed_outcome"]))[-5:]
            tone["reflection_notes"] = list(dict.fromkeys((tone.get("reflection_notes") or []) + ["Missed outcomes suggest softer wording and smaller asks."]))[-5:]
        elif ev.get("event_type") == "workout_completed":
            tone["suggested_style"] = "direct_encouraging"
            tone["evidence"] = list(dict.fromkeys((tone.get("evidence") or []) + ["recent_completion"]))[-5:]
            tone["reflection_notes"] = list(dict.fromkeys((tone.get("reflection_notes") or []) + ["Completion evidence supports slightly more direct encouragement."]))[-5:]
            snapshot['state']['last_training_event_at'] = ts
        elif ev.get("event_type") == "fatigue_report" and facts.get("fatigue") == "high":
            tone["suggested_style"] = "gentle_low_pressure"
            tone["evidence"] = list(dict.fromkeys((tone.get("evidence") or []) + ["high_fatigue"]))[-5:]
        elif ev.get("event_type") == "restart_signal":
            tone["suggested_style"] = "reset_oriented"
            tone["evidence"] = list(dict.fromkeys((tone.get("evidence") or []) + ["restart_signal"]))[-5:]
            tone["reflection_notes"] = list(dict.fromkeys((tone.get("reflection_notes") or []) + ["Restart cycles may need non-shaming outcome review."]))[-5:]

        if "risk_flags" in facts and isinstance(facts["risk_flags"], list):
            snapshot["risk_flags"] = sorted(set(snapshot["risk_flags"] + list(facts["risk_flags"])))
        if "simplification_level" in facts and isinstance(facts["simplification_level"], str):
            snapshot["simplification_level"] = facts["simplification_level"]
        if "active_modes" in facts and isinstance(facts["active_modes"], list):
            snapshot["active_modes"] = list(dict.fromkeys(snapshot["active_modes"] + facts["active_modes"]))
    valid_timestamps = [ev.get("timestamp") for ev in structured_events if isinstance(ev, dict) and ev.get("timestamp")]
    if valid_timestamps:
        snapshot["updated_at"] = valid_timestamps[-1]
    return _save(snapshot)
