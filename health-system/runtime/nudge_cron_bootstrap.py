from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from .chat_flow import evaluate_nudge_slot
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
    return f"{int(mm)} {int(hh)} * * * cd {WORKDIR} && TZ={policy['local_timezone']} /usr/bin/python3 -m runtime.nudge_cron_bootstrap --slot {slot} --channel test --recipient local-test-recipient >> {WORKDIR}/runtime/data/nudge_logs/cron_runner.log 2>&1"


def bootstrap_schedule() -> List[Dict[str, str]]:
    jobs: List[Dict[str, str]] = []
    for slot in NUDGE_SLOTS:
        policy = get_slot_policy(slot)
        jobs.append(
            {
                "slot": slot,
                "local_time": CRON_MAP[slot],
                "timezone": policy["local_timezone"],
                "runner": f"/usr/bin/python3 -m runtime.nudge_cron_bootstrap --slot {slot} --channel test --recipient local-test-recipient",
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


def _default_snapshot() -> Dict[str, Any]:
    return {
        "state": {
            "fatigue": {"value": None},
            "motivation": {"value": None},
            "behavior_state": {"value": None},
            "recent_misses": 0,
        },
        "simplification_level": "normal",
    }


def execute_slot(slot: str, channel: str, recipient: str) -> Dict[str, Any]:
    if slot not in NUDGE_SLOTS:
        raise ValueError(f"Invalid slot: {slot}")
    policy = get_slot_policy(slot)
    local_time = CRON_MAP[slot]
    today = datetime.now().astimezone().date().isoformat()
    now = datetime.fromisoformat(f"{today}T{local_time}:00+03:00")
    return evaluate_nudge_slot(
        current_snapshot=_default_snapshot(),
        todays_events=[],
        daily_summary=None,
        recent_user_activity=[],
        current_slot=slot,
        now=now,
        outbound_channel=channel,
        recipient_id=recipient,
    )


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--slot", help="slot to evaluate")
    parser.add_argument("--channel", default="test")
    parser.add_argument("--recipient", default="local-test-recipient")
    args = parser.parse_args(argv)

    if not args.slot:
        print(json.dumps(bootstrap_payload(), indent=2))
        return 0

    try:
        result = execute_slot(args.slot, args.channel, args.recipient)
    except Exception as exc:
        print(json.dumps({"error": str(exc), "slot": args.slot}))
        return 1

    print(json.dumps({
        "slot": args.slot,
        "send": result["selection"].get("send", False),
        "skip_reason": result["selection"].get("skip_reason"),
        "runtime_mode": result.get("log", {}).get("runtime_mode"),
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
