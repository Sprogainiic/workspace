from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, Iterable, List, Optional

SLOT_SIGNAL_RULES = {
    "morning_plan_check": {
        "event_types": {"fatigue_report", "morning_checkin", "training_intention"},
        "keywords": {"energy", "fatigue", "plan", "train", "training", "morning check-in"},
    },
    "late_morning_check": {
        "event_types": {"activity_logged", "fatigue_report", "motivation_signal", "status_update"},
        "keywords": {"activity", "energy", "motivation", "status"},
    },
    "lunch_check": {
        "event_types": {"meal_logged", "meal_request", "nutrition_update"},
        "keywords": {"lunch", "meal", "food", "nutrition"},
    },
    "afternoon_check": {
        "event_types": {"fatigue_report", "training_status", "motivation_signal", "activity_logged"},
        "keywords": {"fatigue", "training", "motivation", "activity", "workout"},
    },
    "dinner_check": {
        "event_types": {"dinner_logged", "dinner_question", "evening_meal_update", "meal_logged", "meal_request"},
        "keywords": {"dinner", "evening meal", "meal", "food"},
    },
    "evening_wrap_up": {
        "event_types": {"day_reflection", "workout_outcome", "day_summary", "checkin_signal", "workout_skipped"},
        "keywords": {"reflection", "summary", "workout", "finished", "wrap"},
    },
}


def _parse_ts(value: str) -> datetime:
    return datetime.fromisoformat(value)


def _recent(items: List[Dict], now: datetime, minutes: int = 720) -> List[Dict]:
    cutoff = now - timedelta(minutes=minutes)
    kept = []
    for item in items:
        if not item.get("timestamp"):
            continue
        ts = _parse_ts(item["timestamp"])
        if ts >= cutoff:
            kept.append(item)
    return kept


def _contains_keywords(text: str, keywords: Iterable[str]) -> bool:
    lowered = text.lower()
    return any(word in lowered for word in keywords)


def should_skip_for_reported_signal(slot: str, today_events: List[Dict], recent_user_activity: List[Dict], now: datetime) -> Optional[str]:
    rules = SLOT_SIGNAL_RULES[slot]
    recent_events = _recent(today_events, now)
    recent_activity = _recent(recent_user_activity, now)

    for event in recent_events:
        if event.get("event_type") in rules["event_types"]:
            return "already_reported"
        facts = event.get("facts", {})
        if isinstance(facts, dict) and _contains_keywords(" ".join(f"{k} {v}" for k, v in facts.items()), rules["keywords"]):
            return "already_reported"

    for activity in recent_activity:
        if _contains_keywords(activity.get("text", ""), rules["keywords"]):
            return "already_reported"

    return None
