from __future__ import annotations

import argparse
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from .reactive_session_bridge_runner import run_once
from .session_history_client import fetch_session_history

ROOT = Path(__file__).resolve().parents[1]
INGEST_DIR = ROOT / "runtime" / "data" / "ingest"
INGEST_DIR.mkdir(parents=True, exist_ok=True)
HEARTBEAT_LOG = INGEST_DIR / "reactive_bridge_heartbeat.jsonl"
ACCEPTED_PRE_INGEST_LOG = INGEST_DIR / "reactive_bridge_pre_ingest.jsonl"
STATUS_FILE = INGEST_DIR / "reactive_bridge_status.json"


def _append_jsonl(path: Path, row: Dict[str, Any]) -> Dict[str, Any]:
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row


def _write_status(row: Dict[str, Any]) -> Dict[str, Any]:
    STATUS_FILE.write_text(json.dumps(row, ensure_ascii=False, indent=2), encoding="utf-8")
    return row


def log_heartbeat(entry: Dict[str, Any]) -> Dict[str, Any]:
    row = {
        "timestamp": entry.get("timestamp", ""),
        "session_key": entry.get("session_key", ""),
        "runner_mode": entry.get("runner_mode", "loop"),
        "poll_iteration": int(entry.get("poll_iteration", 0) or 0),
        "history_fetch_ok": bool(entry.get("history_fetch_ok", False)),
        "events_seen": int(entry.get("events_seen", 0) or 0),
        "eligible_events": int(entry.get("eligible_events", 0) or 0),
        "stage": entry.get("stage"),
        "last_accepted_message_id": entry.get("last_accepted_message_id", ""),
    }
    _write_status(row)
    return _append_jsonl(HEARTBEAT_LOG, row)


def log_accepted_pre_ingest(session_key: str, discord_message_id: str) -> Dict[str, Any]:
    row = {
        "timestamp": datetime.now().astimezone().isoformat(),
        "session_key": session_key,
        "discord_message_id": discord_message_id,
        "bridge_stage": "accepted_pre_ingest",
    }
    return _append_jsonl(ACCEPTED_PRE_INGEST_LOG, row)


def _eligible(messages):
    return [m for m in messages if m.get("role") == "user" and m.get("__openclaw", {}).get("id") and any((isinstance(p, dict) and p.get("type") == "text" and p.get("text", "").strip()) for p in m.get("content", []))]


def launch_bridge(session_key: str, mode: str, history_fetcher=None, poll_seconds: int = 10, max_iterations: int | None = None, runtime_mode: str = "test", sessions_history_tool=None) -> Dict[str, Any]:
    if not session_key:
        return {"status": "failed", "processed": 0, "accepted": 0, "ignored": 0, "failed": 1, "failure_point": "session_history_unavailable"}

    startup_ts = datetime.now().astimezone().isoformat()
    log_heartbeat({
        "timestamp": startup_ts,
        "session_key": session_key,
        "runner_mode": mode,
        "poll_iteration": 0,
        "history_fetch_ok": False,
        "events_seen": 0,
        "eligible_events": 0,
        "stage": "startup",
        "last_accepted_message_id": "",
    })

    if runtime_mode == "prod" and history_fetcher is not None:
        return {"status": "failed", "processed": 0, "accepted": 0, "ignored": 0, "failed": 1, "failure_point": "session_history_unavailable"}
    if runtime_mode == "test" and history_fetcher is None:
        return {"status": "failed", "processed": 0, "accepted": 0, "ignored": 0, "failed": 1, "failure_point": "session_history_unavailable"}

    def get_batch():
        if runtime_mode == "test":
            return history_fetcher(sessionKey=session_key, limit=50, includeTools=False)
        result = fetch_session_history(session_key, limit=50, sessions_history_tool=sessions_history_tool)
        if result["status"] != "ok":
            raise RuntimeError("session_history_unavailable")
        return {"messages": result["events"]}

    try:
        if mode == "once":
            log_heartbeat({
                "timestamp": datetime.now().astimezone().isoformat(),
                "session_key": session_key,
                "runner_mode": "once",
                "poll_iteration": 0,
                "history_fetch_ok": False,
                "events_seen": 0,
                "eligible_events": 0,
                "stage": "pre_fetch",
                "last_accepted_message_id": "",
            })
            raw = get_batch()
            messages = raw.get("messages")
            if not isinstance(messages, list):
                return {"status": "failed", "processed": 0, "accepted": 0, "ignored": 0, "failed": 1, "failure_point": "session_history_unavailable"}
            eligible = _eligible(messages)
            log_heartbeat({
                "timestamp": datetime.now().astimezone().isoformat(),
                "session_key": session_key,
                "runner_mode": "once",
                "poll_iteration": 0,
                "history_fetch_ok": True,
                "events_seen": len(messages),
                "eligible_events": len(eligible),
                "stage": "post_fetch",
                "last_accepted_message_id": eligible[-1].get("__openclaw", {}).get("id", "") if eligible else "",
            })
            for m in eligible:
                log_accepted_pre_ingest(session_key, m.get("__openclaw", {}).get("id", ""))
            result = run_once(session_key, lambda **kwargs: {"messages": messages}, poll_iteration=0)
            accepted = sum(1 for row in result["results"] if row["bridge_status"] == "accepted")
            ignored = sum(1 for row in result["results"] if row["bridge_status"] == "ignored")
            failed = sum(1 for row in result["results"] if row["bridge_status"] == "failed")
            return {"status": "ok", "processed": result["processed"], "accepted": accepted, "ignored": ignored, "failed": failed}
        if mode == "loop":
            processed = accepted = ignored = failed = 0
            iteration = 0
            while True:
                log_heartbeat({
                    "timestamp": datetime.now().astimezone().isoformat(),
                    "session_key": session_key,
                    "runner_mode": "loop",
                    "poll_iteration": iteration,
                    "history_fetch_ok": False,
                    "events_seen": 0,
                    "eligible_events": 0,
                    "stage": "pre_fetch",
                    "last_accepted_message_id": "",
                })
                try:
                    raw = get_batch()
                    messages = raw.get("messages")
                    fetch_ok = isinstance(messages, list)
                    if not fetch_ok:
                        raise RuntimeError("session_history_unavailable")
                except Exception:
                    return {"status": "failed", "processed": processed, "accepted": accepted, "ignored": ignored, "failed": failed + 1, "failure_point": "session_history_unavailable"}
                eligible = _eligible(messages)
                log_heartbeat({
                    "timestamp": datetime.now().astimezone().isoformat(),
                    "session_key": session_key,
                    "runner_mode": "loop",
                    "poll_iteration": iteration,
                    "history_fetch_ok": True,
                    "events_seen": len(messages),
                    "eligible_events": len(eligible),
                    "stage": "post_fetch",
                    "last_accepted_message_id": eligible[-1].get("__openclaw", {}).get("id", "") if eligible else "",
                })
                for m in eligible:
                    log_accepted_pre_ingest(session_key, m.get("__openclaw", {}).get("id", ""))
                out = run_once(session_key, lambda **kwargs: {"messages": messages}, poll_iteration=iteration)
                processed += out["processed"]
                accepted += sum(1 for row in out["results"] if row["bridge_status"] == "accepted")
                ignored += sum(1 for row in out["results"] if row["bridge_status"] == "ignored")
                failed += sum(1 for row in out["results"] if row["bridge_status"] == "failed")
                iteration += 1
                if max_iterations is not None and iteration >= max_iterations:
                    break
                time.sleep(poll_seconds)
            return {"status": "ok", "processed": processed, "accepted": accepted, "ignored": ignored, "failed": failed}
        return {"status": "failed", "processed": 0, "accepted": 0, "ignored": 0, "failed": 1, "failure_point": "session_history_unavailable"}
    except Exception as exc:
        return {"status": "failed", "processed": 0, "accepted": 0, "ignored": 0, "failed": 1, "failure_point": str(exc) or "session_history_unavailable"}


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--session-key", required=True)
    parser.add_argument("--mode", choices=["once", "loop"], default="once")
    parser.add_argument("--poll-seconds", type=int, default=10)
    parser.add_argument("--runtime-mode", choices=["test", "prod"], default="prod")
    args = parser.parse_args(argv)
    result = launch_bridge(args.session_key, args.mode, poll_seconds=args.poll_seconds, runtime_mode=args.runtime_mode)
    print(json.dumps(result))
    return 0 if result.get("status") == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
