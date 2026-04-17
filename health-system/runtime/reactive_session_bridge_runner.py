from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any, Dict, List

from .reactive_session_bridge import process_session_messages
from .reactive_session_bridge_state import load_bridge_checkpoint, save_bridge_checkpoint


def _extract_message_id(message: Dict[str, Any]) -> str:
    return message.get("__openclaw", {}).get("id", "")


def _eligible_messages(session_key: str, messages: List[Dict[str, Any]], checkpoint: Dict[str, Any]) -> List[Dict[str, Any]]:
    eligible: List[Dict[str, Any]] = []
    recent_ids = set(checkpoint.get('recent_message_ids', [])) if checkpoint.get('session_key') == session_key else set()
    last_ts = checkpoint.get('last_processed_timestamp', '') if checkpoint.get('session_key') == session_key else ''
    last_id = checkpoint.get('last_processed_message_id', '') if checkpoint.get('session_key') == session_key else ''
    for message in messages:
        message_id = _extract_message_id(message)
        role = message.get('role')
        msg_ts = str(message.get('timestamp') or '')
        if role != 'user':
            continue
        if not message_id or message_id in recent_ids:
            continue
        if last_ts:
            if msg_ts < last_ts:
                continue
            if msg_ts == last_ts and last_id and message_id <= last_id:
                continue
        text_parts = []
        for part in message.get('content', []):
            if isinstance(part, dict) and part.get('type') == 'text':
                text_parts.append(part.get('text', ''))
        message_text = '\n'.join(part for part in text_parts if part).strip()
        if not message_text:
            continue
        eligible.append(message)
    return eligible


def run_once(session_key: str, history_fetcher, poll_iteration: int = 0, reply_sender=None) -> Dict[str, Any]:
    checkpoint = load_bridge_checkpoint()
    data = history_fetcher(sessionKey=session_key, limit=50, includeTools=False)
    messages = data.get('messages', [])
    eligible = _eligible_messages(session_key, messages, checkpoint)
    results = process_session_messages(session_key, eligible, reply_sender=reply_sender)
    recent_ids = list(checkpoint.get('recent_message_ids', [])) if checkpoint.get('session_key') == session_key else []
    processed_ids = [_extract_message_id(message) for message in eligible if _extract_message_id(message)]
    latest_ts = checkpoint.get('last_processed_timestamp', '') if checkpoint.get('session_key') == session_key else ''
    latest_id = checkpoint.get('last_processed_message_id', '') if checkpoint.get('session_key') == session_key else ''
    if eligible:
        last_msg = eligible[-1]
        latest_ts = str(last_msg.get('timestamp') or latest_ts)
        latest_id = _extract_message_id(last_msg) or latest_id
    save_bridge_checkpoint(session_key, latest_ts, latest_id, recent_ids + processed_ids)
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
