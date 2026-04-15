from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set

DEFAULT_POLICY = {
    "max_proactive_messages_per_day": 4,
    "min_minutes_between_proactive_messages": 90,
    "domain_cooldown_minutes": 180,
    "recent_user_activity_suppression_minutes": 45,
    "quiet_hours_start": "21:30",
    "quiet_hours_end": "08:00",
}

NUDGE_DOMAINS = ["training", "nutrition", "behavior", "wrap_up"]

SLOT_RELEVANT_SIGNALS = {
    "morning_plan_check": {"status_update", "checkin_reply", "decision_request", "energy", "fatigue", "training_intention"},
    "late_morning_check": {"status_update", "checkin_reply", "activity_status", "motivation_status", "activity"},
    "lunch_check": {"meal_log", "nutrition_update", "meal_request", "lunch_status", "nutrition"},
    "afternoon_check": {"status_update", "decision_request", "fatigue_status", "training_status", "motivation_status", "training"},
    "dinner_check": {"meal_log", "nutrition_update", "meal_request", "dinner_status", "nutrition"},
    "evening_wrap_up": {"checkin_reply", "status_update", "day_summary", "workout_outcome", "wrap_up"},
}

DOMAIN_SIGNAL_MAP = {
    "nutrition": {"meal_log", "nutrition_update", "meal_request", "nutrition", "lunch_status", "dinner_status"},
    "training": {"training", "training_status", "fatigue_status", "decision_request", "status_update"},
    "behavior": {"status_update", "checkin_reply", "motivation_status", "activity_status", "activity"},
    "wrap_up": {"wrap_up", "day_summary", "workout_outcome", "checkin_reply"},
}


def _parse_ts(value: str) -> datetime:
    return datetime.fromisoformat(value)


def nudges_sent_today(sent_nudges_today: List[Dict[str, Any]]) -> int:
    return sum(1 for row in sent_nudges_today if row.get("send"))


def check_daily_cap(sent_nudges_today: List[Dict[str, Any]], policy: Dict[str, Any]) -> Optional[str]:
    if nudges_sent_today(sent_nudges_today) >= policy["max_proactive_messages_per_day"]:
        return "spam_guard"
    return None


def check_gap_rule(now: datetime, sent_nudges_today: List[Dict[str, Any]], policy: Dict[str, Any]) -> Optional[str]:
    sent = [row for row in sent_nudges_today if row.get("send") and row.get("timestamp")]
    if not sent:
        return None
    last = max(_parse_ts(row["timestamp"]) for row in sent)
    if now - last < timedelta(minutes=policy["min_minutes_between_proactive_messages"]):
        return "spam_guard"
    return None


def check_domain_cooldown(now: datetime, domain: str, sent_nudges_today: List[Dict[str, Any]], policy: Dict[str, Any]) -> Optional[str]:
    relevant = [
        row for row in sent_nudges_today
        if row.get("send") and row.get("domain") == domain and row.get("timestamp")
    ]
    if not relevant:
        return None
    last = max(_parse_ts(row["timestamp"]) for row in relevant)
    if now - last < timedelta(minutes=policy["domain_cooldown_minutes"]):
        return "spam_guard"
    return None


def _activity_relevant_to_slot(activity: Dict[str, Any], slot: str, domain: str) -> bool:
    signal = activity.get("signal_type", "other")
    activity_domain = activity.get("domain")
    relevant_signals: Set[str] = SLOT_RELEVANT_SIGNALS.get(slot, set()) | DOMAIN_SIGNAL_MAP.get(domain, set())
    if activity_domain and activity_domain == domain:
        return True
    return signal in relevant_signals


def check_recent_user_activity(now: datetime, recent_user_activity: List[Dict[str, Any]], policy: Dict[str, Any], slot: str, domain: str) -> Optional[str]:
    if not recent_user_activity:
        return None
    threshold = timedelta(minutes=policy["recent_user_activity_suppression_minutes"])
    relevant_recent = []
    for row in recent_user_activity:
        if not row.get("timestamp"):
            continue
        ts = _parse_ts(row["timestamp"])
        if now - ts >= threshold:
            continue
        if _activity_relevant_to_slot(row, slot, domain):
            relevant_recent.append(ts)
    if relevant_recent:
        return "recent_user_activity"
    return None


def enforce_guardrails(
    now: datetime,
    domain: str,
    sent_nudges_today: List[Dict[str, Any]],
    recent_user_activity: List[Dict[str, Any]],
    policy: Dict[str, Any] | None = None,
    slot: str | None = None,
) -> Optional[str]:
    applied = {**DEFAULT_POLICY, **(policy or {})}
    return (
        check_daily_cap(sent_nudges_today, applied)
        or check_gap_rule(now, sent_nudges_today, applied)
        or check_domain_cooldown(now, domain, sent_nudges_today, applied)
        or check_recent_user_activity(now, recent_user_activity, applied, slot or "", domain)
    )
