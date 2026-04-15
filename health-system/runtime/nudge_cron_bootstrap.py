from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

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
    from .nudge_schedule import get_slot_policy
    hh, mm = CRON_MAP[slot].split(":", 1)
    policy = get_slot_policy(slot)
    return f"{int(mm)} {int(hh)} * * * cd {WORKDIR} && TZ={policy['local_timezone']} /usr/bin/python3 -m runtime.nudge_cron_bootstrap --slot {slot} --channel test --recipient local-test-recipient >> {WORKDIR}/runtime/data/nudge_logs/cron_runner.log 2>&1"


def bootstrap_schedule() -> List[Dict[str, str]]:
    from .nudge_schedule import NUDGE_SLOTS, get_slot_policy
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
    from .nudge_schedule import NUDGE_SLOTS
    return {
        "cron_map": local_cron_map(),
        "cron_lines": [_cron_line(slot) for slot in NUDGE_SLOTS],
        "runner_command": RUNNER_COMMAND,
    }


def execute_slot(slot: str, channel: str, recipient: str, *, mode: str = "prod", fixture: Dict[str, Any] | None = None, session_sender=None) -> Dict[str, Any]:
    from .nudge_schedule import NUDGE_SLOTS
    from .state_loader import MissingRuntimeStateError, load_runtime_state
    from .chat_flow import evaluate_nudge_slot

    if slot not in NUDGE_SLOTS:
        raise ValueError(f"Invalid slot: {slot}")

    now = datetime.now().astimezone()
    try:
        state = load_runtime_state(now, allow_test_fixture=(mode == "test"), fixture=fixture)
    except MissingRuntimeStateError:
        return {"error": "missing_runtime_state", "slot": slot}

    result = evaluate_nudge_slot(
        current_snapshot=state.get("snapshot"),
        todays_events=state.get("today_events"),
        daily_summary=state.get("daily_summary"),
        recent_user_activity=state.get("recent_user_activity", []),
        current_slot=slot,
        now=now,
        outbound_channel=channel,
        recipient_id=recipient,
        sent_nudges_today=state.get("sent_nudges_today"),
        state_source=state.get("state_source", "persisted"),
        activity_source=state.get("activity_source", "missing"),
        session_sender=session_sender,
    )
    return result


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--slot", help="slot to evaluate")
    parser.add_argument("--channel", default="test")
    parser.add_argument("--recipient", default="local-test-recipient")
    parser.add_argument("--mode", choices=["prod", "test"], default="prod")
    args = parser.parse_args(argv)

    if not args.slot:
        print(json.dumps(bootstrap_payload(), indent=2))
        return 0

    try:
        result = execute_slot(args.slot, args.channel, args.recipient, mode=args.mode)
    except Exception as exc:
        print(json.dumps({"error": str(exc), "slot": args.slot}))
        return 1

    if result.get("error") == "missing_runtime_state":
        print(json.dumps(result))
        return 1

    print(json.dumps({
        "slot": args.slot,
        "send": result["selection"].get("send", False),
        "skip_reason": result["selection"].get("skip_reason"),
        "runtime_mode": result.get("log", {}).get("runtime_mode"),
        "state_source": result.get("log", {}).get("state_source"),
        "activity_source": result.get("log", {}).get("activity_source"),
        "recent_user_activity_count": result.get("log", {}).get("recent_user_activity_count", 0),
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
