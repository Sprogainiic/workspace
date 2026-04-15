from __future__ import annotations

from typing import Dict, List

from .nudge_schedule import NUDGE_SLOTS, get_slot_policy

CRON_MAP = {
    "morning_plan_check": "08:05",
    "late_morning_check": "10:30",
    "lunch_check": "12:30",
    "afternoon_check": "15:30",
    "dinner_check": "18:30",
    "evening_wrap_up": "20:30",
}


def local_cron_map() -> Dict[str, str]:
    return dict(CRON_MAP)


def bootstrap_schedule() -> List[Dict[str, str]]:
    jobs: List[Dict[str, str]] = []
    for slot in NUDGE_SLOTS:
        policy = get_slot_policy(slot)
        jobs.append(
            {
                "slot": slot,
                "local_time": CRON_MAP[slot],
                "timezone": policy["local_timezone"],
                "runner": f"python -m runtime.nudge_cron_bootstrap {slot}",
                "kind": "slot_evaluator",
            }
        )
    return jobs


def bootstrap_payload() -> Dict[str, object]:
    return {
        "cron_map": local_cron_map(),
        "jobs": bootstrap_schedule(),
        "notes": "One evaluator call per slot window in local timezone; evaluator decides send or skip.",
    }


if __name__ == "__main__":
    import json
    print(json.dumps(bootstrap_payload(), indent=2))
