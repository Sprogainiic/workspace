from __future__ import annotations

from datetime import datetime, time
from zoneinfo import ZoneInfo
from typing import Any, Dict, List, Optional

from .nudge_schedule import get_slot_policy
from .nudge_guard import DEFAULT_POLICY, enforce_guardrails
from .nudge_skip_rules import should_skip_for_reported_signal
from .nudge_content_guard import content_guard_decision

QUIET_HOURS = {
    "start": "21:30",
    "end": "08:00",
}

SLOT_DEFAULTS = {
    "morning_plan_check": {
        "goal": "get energy/fatigue + plan intention",
        "nudge_type": "check_in",
        "domain": "behavior",
        "missing_signals": ["energy_status", "fatigue_status", "training_intention"],
    },
    "late_morning_check": {
        "goal": "catch drift early",
        "nudge_type": "check_in",
        "domain": "behavior",
        "missing_signals": ["activity_status", "energy_status", "motivation_status"],
    },
    "lunch_check": {
        "goal": "nutrition support",
        "nudge_type": "reminder",
        "domain": "nutrition",
        "missing_signals": ["lunch_status"],
    },
    "afternoon_check": {
        "goal": "fatigue/training/adherence stabilization",
        "nudge_type": "check_in",
        "domain": "training",
        "missing_signals": ["fatigue_status", "training_status", "motivation_status"],
    },
    "dinner_check": {
        "goal": "reduce evening drift",
        "nudge_type": "reminder",
        "domain": "nutrition",
        "missing_signals": ["dinner_status"],
    },
    "evening_wrap_up": {
        "goal": "capture outcome without shame",
        "nudge_type": "check_in",
        "domain": "wrap_up",
        "missing_signals": ["day_summary", "workout_outcome"],
    },
}


def _parse_clock(value: str) -> time:
    hour, minute = value.split(":", 1)
    return time(hour=int(hour), minute=int(minute))


def _in_quiet_hours(now: datetime, timezone_name: str, quiet_hours: Dict[str, str]) -> bool:
    local_now = now.astimezone(ZoneInfo(timezone_name))
    current = local_now.time()
    start = _parse_clock(quiet_hours["start"])
    end = _parse_clock(quiet_hours["end"])
    if start <= end:
        return start <= current < end
    return current >= start or current < end


def _pick_nudge_type(slot: str, snapshot: Dict[str, Any], today_events: List[Dict[str, Any]]) -> str:
    default = SLOT_DEFAULTS[slot]["nudge_type"]
    state = snapshot.get("state", {}) if isinstance(snapshot, dict) else {}
    fatigue = state.get("fatigue", {}).get("value")
    motivation = state.get("motivation", {}).get("value")
    behavior_state = state.get("behavior_state", {}).get("value")
    repeated_misses = state.get("recent_misses", 0) or 0
    friction = behavior_state in {"restart_cycle", "drop_off", "fragile"}
    if slot == "afternoon_check" and (fatigue == "high" or motivation == "low" or repeated_misses >= 2 or friction):
        return "coaching"
    if slot == "dinner_check" and motivation == "low":
        return "check_in"
    return default


def _state_flags(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    state = snapshot.get("state", {}) if isinstance(snapshot, dict) else {}
    return {
        "fatigue": state.get("fatigue", {}).get("value"),
        "motivation": state.get("motivation", {}).get("value"),
        "simplification_level": snapshot.get("simplification_level", "normal") if isinstance(snapshot, dict) else "normal",
    }


def select_nudge(
    current_snapshot: Dict[str, Any],
    todays_events: List[Dict[str, Any]],
    daily_summary: Optional[Dict[str, Any]],
    sent_nudges_today: List[Dict[str, Any]],
    recent_user_activity: List[Dict[str, Any]],
    current_slot: str,
    now: datetime,
    policy_overrides: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    policy = get_slot_policy(current_slot)
    merged_guard_policy = {**DEFAULT_POLICY, **(policy_overrides or {})}

    if _in_quiet_hours(now, policy["local_timezone"], {"start": merged_guard_policy["quiet_hours_start"], "end": merged_guard_policy["quiet_hours_end"]}):
        return {"send": False, "skip_reason": "quiet_hours"}

    local_now = now.astimezone(ZoneInfo(policy["local_timezone"]))
    if local_now.weekday() not in policy["eligible_weekdays"]:
        return {"send": False, "skip_reason": "no_missing_signal"}

    signal_skip = should_skip_for_reported_signal(current_slot, todays_events, recent_user_activity, now)
    if signal_skip:
        return {"send": False, "skip_reason": signal_skip}

    defaults = SLOT_DEFAULTS[current_slot]
    nudge_type = _pick_nudge_type(current_slot, current_snapshot, todays_events)
    domain = defaults["domain"]
    guard_skip = enforce_guardrails(now, domain, sent_nudges_today, recent_user_activity, merged_guard_policy)
    if guard_skip:
        return {"send": False, "skip_reason": guard_skip}

    payload_brief = {
        "slot": current_slot,
        "nudge_type": nudge_type,
        "domain": domain,
        "missing_signals": defaults["missing_signals"],
        "state_flags": _state_flags(current_snapshot),
        "send_style": "short",
    }
    ok, fingerprint = content_guard_decision(current_slot, domain, nudge_type, payload_brief, sent_nudges_today)
    if not ok:
        return {"send": False, "skip_reason": "spam_guard"}

    reason = defaults["goal"]
    if nudge_type == "coaching":
        reason = "behavior friction detected"

    return {
        "send": True,
        "slot": current_slot,
        "nudge_type": nudge_type,
        "domain": domain,
        "reason": reason,
        "payload_brief": payload_brief,
        "message_intent": nudge_type,
        "fingerprint": fingerprint,
        "route": {
            "flow": "cron slot trigger -> nudge_selector -> advisor runtime -> Health Director -> Chat Gateway",
            "governance": "same_as_reactive_chat",
        },
    }
