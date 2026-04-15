from __future__ import annotations

from pathlib import Path
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

WORKDIR = Path(__file__).resolve().parents[1]
RUNNER_COMMAND = f"cd {WORKDIR} && /usr/bin/python3 -m runtime.nudge_cron_bootstrap --slot"


def local_cron_map() -> Dict[str, str]:
    return dict(CRON_MAP)


def _cron_line(slot: str) -> str:
    hh, mm = CRON_MAP[slot].split(":", 1)
    policy = get_slot_policy(slot)
    return f"{int(mm)} {int(hh)} * * * cd {WORKDIR} && TZ={policy['local_timezone']} /usr/bin/python3 -m runtime.nudge_cron_bootstrap --slot {slot} >> {WORKDIR}/runtime/data/nudge_logs/cron_runner.log 2>&1"


def bootstrap_schedule() -> List[Dict[str, str]]:
    jobs: List[Dict[str, str]] = []
    for slot in NUDGE_SLOTS:
        policy = get_slot_policy(slot)
        jobs.append(
            {
                "slot": slot,
                "local_time": CRON_MAP[slot],
                "timezone": policy["local_timezone"],
                "runner": f"/usr/bin/python3 -m runtime.nudge_cron_bootstrap --slot {slot}",
                "kind": "slot_evaluator",
            }
        )
    return jobs


def bootstrap_payload() -> Dict[str, object]:
    return {
        "cron_map": local_cron_map(),
        "cron_lines": [_cron_line(slot) for slot in NUDGE_SLOTS],
        "runner_command": RUNNER_COMMAND,
    }


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) > 2 and sys.argv[1] == "--slot":
        slot = sys.argv[2]
        print(json.dumps({"slot": slot, "status": "bootstrap_runner_placeholder"}))
    else:
        print(json.dumps(bootstrap_payload(), indent=2))
