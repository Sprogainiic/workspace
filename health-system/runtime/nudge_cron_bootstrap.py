from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

WORKDIR = Path(__file__).resolve().parents[1]
RUNNER_COMMAND = f"cd {WORKDIR} && /usr/bin/python3 -m runtime.nudge_cron_bootstrap --slot"


def local_cron_map() -> Dict[str, str]:
    from .nudge_schedule import NUDGE_SLOTS, get_slot_policy
    return {slot: get_slot_policy(slot)["earliest_send_time"] for slot in NUDGE_SLOTS}


def _cron_line(slot: str) -> str:
    from .nudge_schedule import get_slot_policy
    policy = get_slot_policy(slot)
    hh, mm = policy["earliest_send_time"].split(":", 1)
    return f"{int(mm)} {int(hh)} * * * cd {WORKDIR} && TZ={policy['local_timezone']} /usr/bin/python3 -m runtime.nudge_cron_bootstrap --slot {slot} --exec-mode live_session --channel openclaw_session --recipient scheduled-health-session >> {WORKDIR}/runtime/data/nudge_logs/cron_runner.log 2>&1"


def bootstrap_schedule() -> List[Dict[str, str]]:
    from .nudge_schedule import NUDGE_SLOTS, get_slot_policy
    jobs: List[Dict[str, str]] = []
    for slot in NUDGE_SLOTS:
        policy = get_slot_policy(slot)
        jobs.append(
            {
                "slot": slot,
                "local_time": policy["earliest_send_time"],
                "timezone": policy["local_timezone"],
                "runner": f"/usr/bin/python3 -m runtime.nudge_cron_bootstrap --slot {slot} --exec-mode live_session --channel openclaw_session --recipient scheduled-health-session",
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


def execute_slot(
    slot: str,
    channel: str,
    recipient: str,
    *,
    exec_mode: str = "local_test",
    fixture: Dict[str, Any] | None = None,
    session_sender=None,
    sessions_send_tool=None,
) -> Dict[str, Any]:
    from .nudge_schedule import NUDGE_SLOTS
    from .state_loader import MissingRuntimeStateError, load_runtime_state
    from .chat_flow import evaluate_nudge_slot

    if slot not in NUDGE_SLOTS:
        raise ValueError(f"Invalid slot: {slot}")
    if exec_mode == "live_session" and channel != "openclaw_session":
        raise ValueError("live_session mode requires channel=openclaw_session")
    if exec_mode == "local_test" and channel not in {"test", "console"}:
        raise ValueError("local_test mode requires channel=test|console")

    now = datetime.now().astimezone()
    try:
        state = load_runtime_state(now, allow_test_fixture=(exec_mode == "local_test" and fixture is not None), fixture=fixture)
    except MissingRuntimeStateError:
        return {"error": "missing_runtime_state", "slot": slot}

    effective_session_sender = session_sender
    if effective_session_sender is None and channel == "openclaw_session" and sessions_send_tool is not None:
        effective_session_sender = sessions_send_tool

    return evaluate_nudge_slot(
        current_snapshot=state.get("snapshot"),
        todays_events=state.get("today_events"),
        daily_summary=state.get("daily_summary"),
        weekly_summary=state.get("weekly_summary"),
        recent_user_activity=state.get("recent_user_activity", []),
        current_slot=slot,
        now=now,
        outbound_channel=channel,
        recipient_id=recipient,
        sent_nudges_today=state.get("sent_nudges_today"),
        state_source=state.get("state_source", "persisted"),
        activity_source=state.get("activity_source", "missing"),
        session_sender=effective_session_sender,
        allow_test_fixture=(exec_mode == "local_test" and fixture is not None),
        launcher_mode=exec_mode,
    )


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--slot", help="slot to evaluate")
    parser.add_argument("--channel", default="openclaw_session")
    parser.add_argument("--recipient", default="scheduled-health-session")
    parser.add_argument("--exec-mode", choices=["local_test", "live_session"], default="local_test")
    args = parser.parse_args(argv)

    if not args.slot:
        print(json.dumps(bootstrap_payload(), indent=2))
        return 0

    try:
        sessions_send_tool = None
        if args.exec_mode == "live_session" and args.channel == "openclaw_session":
            try:
                from functions import sessions_send as sessions_send_tool  # type: ignore
            except Exception:
                sessions_send_tool = None
        result = execute_slot(
            args.slot,
            args.channel,
            args.recipient,
            exec_mode=args.exec_mode,
            sessions_send_tool=sessions_send_tool,
        )
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
        "transport": result.get("log", {}).get("transport"),
        "launcher_mode": result.get("log", {}).get("launcher_mode"),
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
