from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, time
from zoneinfo import ZoneInfo
from typing import Any, Dict, List

DEFAULT_LOCAL_TIMEZONE = "Europe/Riga"
NUDGE_SLOTS = [
    "morning_plan_check",
    "late_morning_check",
    "lunch_check",
    "afternoon_check",
    "dinner_check",
    "evening_wrap_up",
]


@dataclass(frozen=True)
class SlotPolicy:
    slot: str
    earliest_send_time: str
    latest_send_time: str
    local_timezone: str
    eligible_weekdays: List[int]
    intent_type: str
    max_send_count_per_day: int = 1

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


SLOT_POLICIES: Dict[str, SlotPolicy] = {
    "morning_plan_check": SlotPolicy(
        slot="morning_plan_check",
        earliest_send_time="08:05",
        latest_send_time="09:30",
        local_timezone=DEFAULT_LOCAL_TIMEZONE,
        eligible_weekdays=[0, 1, 2, 3, 4, 5, 6],
        intent_type="check_in",
    ),
    "late_morning_check": SlotPolicy(
        slot="late_morning_check",
        earliest_send_time="10:45",
        latest_send_time="11:45",
        local_timezone=DEFAULT_LOCAL_TIMEZONE,
        eligible_weekdays=[0, 1, 2, 3, 4, 5, 6],
        intent_type="check_in",
    ),
    "lunch_check": SlotPolicy(
        slot="lunch_check",
        earliest_send_time="12:15",
        latest_send_time="13:30",
        local_timezone=DEFAULT_LOCAL_TIMEZONE,
        eligible_weekdays=[0, 1, 2, 3, 4, 5, 6],
        intent_type="reminder",
    ),
    "afternoon_check": SlotPolicy(
        slot="afternoon_check",
        earliest_send_time="15:30",
        latest_send_time="17:00",
        local_timezone=DEFAULT_LOCAL_TIMEZONE,
        eligible_weekdays=[0, 1, 2, 3, 4, 5, 6],
        intent_type="check_in",
    ),
    "dinner_check": SlotPolicy(
        slot="dinner_check",
        earliest_send_time="18:00",
        latest_send_time="19:30",
        local_timezone=DEFAULT_LOCAL_TIMEZONE,
        eligible_weekdays=[0, 1, 2, 3, 4, 5, 6],
        intent_type="reminder",
    ),
    "evening_wrap_up": SlotPolicy(
        slot="evening_wrap_up",
        earliest_send_time="20:00",
        latest_send_time="21:15",
        local_timezone=DEFAULT_LOCAL_TIMEZONE,
        eligible_weekdays=[0, 1, 2, 3, 4, 5, 6],
        intent_type="check_in",
    ),
}


def _parse_clock(value: str) -> time:
    hour, minute = value.split(":", 1)
    return time(hour=int(hour), minute=int(minute))


def get_slot_policy(slot: str) -> Dict[str, Any]:
    if slot not in SLOT_POLICIES:
        raise KeyError(f"Unknown nudge slot: {slot}")
    return SLOT_POLICIES[slot].to_dict()


def list_slot_policies() -> List[Dict[str, Any]]:
    return [SLOT_POLICIES[slot].to_dict() for slot in NUDGE_SLOTS]


def should_evaluate_slot(slot: str, now: datetime) -> bool:
    policy = SLOT_POLICIES[slot]
    local_now = now.astimezone(ZoneInfo(policy.local_timezone))
    if local_now.weekday() not in policy.eligible_weekdays:
        return False
    local_t = local_now.time()
    return _parse_clock(policy.earliest_send_time) <= local_t <= _parse_clock(policy.latest_send_time)


def cron_specs() -> List[Dict[str, Any]]:
    specs: List[Dict[str, Any]] = []
    for slot in NUDGE_SLOTS:
        policy = SLOT_POLICIES[slot]
        hour, minute = policy.earliest_send_time.split(":", 1)
        specs.append(
            {
                "slot": slot,
                "cron": f"{int(minute)} {int(hour)} * * *",
                "timezone": policy.local_timezone,
                "evaluation_only": True,
            }
        )
    return specs
