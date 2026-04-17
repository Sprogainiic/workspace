from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any, Dict, List

from .reactive_session_bridge import process_session_messages

ROOT = Path(__file__).resolve().parents[1]
CHECKPOINT = ROOT / "runtime" / "data" / "reactive_bridge_checkpoint.json"
CHECKPOINT.parent.mkdir(parents=True, exist_ok=True)


def _load_checkpoint() -> Dict[str, Any]:
    if not CHECKPOINT.exists():
        return {"session_key": "", "last_seen_message_ids": []}
    return json.loads(CHECKPOINT.read_text(encoding="utf-8"))


def _save_checkpoint(session_key: str, message_ids: List[str]) -> None:
    CHECKPOINT.write_text(json.dumps({"session_key": session_key, "last_seen_message_ids": message_ids[-500:]}, indent=2, ensure_ascii=False), encoding="utf-8")


def _extract_message_id(message: Dict[str, Any]) -> str:
    return message.get("__openclaw", {}).get("id", "")


def _eligible_messages(session_key: str, messages: List[Dict[str, Any]], seen_ids: set[str]) -> List[Dict[str, Any]]:
    eligible: List[Dict[str, Any]] = []
    for message in messages:
        message_id = _extract_message_id(message)
        role = message.get("role")
        if role != "user":
            continue
        if not message_id or message_id in seen_ids:
            continue
        text_parts = []
        for part in message.get("content", []):
            if isinstance(part, dict) and part.get("type") == "text":
                text_parts.append(part.get("text", ""))
        message_text = "\n".join(part for part in text_parts if part).strip()
        if not message_text:
            continue
        eligible.append(message)
    return eligible


def run_once(session_key: str, history_fetcher, poll_iteration: int = 0, reply_sender=None) -> Dict[str, Any]:
    checkpoint = _load_checkpoint()
    seen_ids = set(checkpoint.get("last_seen_message_ids", [])) if checkpoint.get("session_key") == session_key else set()
    data = history_fetcher(sessionKey=session_key, limit=50, includeTools=False)
    messages = data.get("messages", [])
    eligible = _eligible_messages(session_key, messages, seen_ids)
    results = process_session_messages(session_key, eligible, reply_sender=reply_sender)
    new_ids = seen_ids | { _extract_message_id(message) for message in eligible }
    _save_checkpoint(session_key, sorted(new_ids))
    for row in results:
        row["runner_mode"] = "once"
        row["poll_iteration"] = poll_iteration
    return {
        "session_key": session_key,
        "processed": len(eligible),
        "results": results,
        "runner_mode": "once",
        "poll_iteration": poll_iteration,
    }


def run_loop(session_key: str, history_fetcher, poll_seconds: int = 10, max_iterations: int | None = None) -> List[Dict[str, Any]]:
    outputs: List[Dict[str, Any]] = []
    iteration = 0
    while True:
        outputs.append(run_once(session_key, history_fetcher, poll_iteration=iteration))
        iteration += 1
        if max_iterations is not None and iteration >= max_iterations:
            break
        time.sleep(poll_seconds)
    return outputs


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--session-key", required=True)
    parser.add_argument("--mode", choices=["once", "loop"], default="once")
    parser.add_argument("--poll-seconds", type=int, default=10)
    args = parser.parse_args(argv)
    print(json.dumps({
        "status": "runner_requires_tool_host",
        "session_key": args.session_key,
        "mode": args.mode,
        "poll_seconds": args.poll_seconds,
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
