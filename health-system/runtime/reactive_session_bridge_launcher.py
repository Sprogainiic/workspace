from __future__ import annotations

import time
from typing import Any, Dict

from .reactive_session_bridge_runner import run_once, run_loop


def launch_bridge(session_key: str, mode: str, history_fetcher, poll_seconds: int = 10, max_iterations: int | None = None) -> Dict[str, Any]:
    if not session_key:
        return {"status": "failed", "processed": 0, "accepted": 0, "ignored": 0, "failed": 1}
    try:
        if mode == "once":
            result = run_once(session_key, history_fetcher, poll_iteration=0)
            accepted = sum(1 for row in result["results"] if row["bridge_status"] == "accepted")
            ignored = sum(1 for row in result["results"] if row["bridge_status"] == "ignored")
            failed = sum(1 for row in result["results"] if row["bridge_status"] == "failed")
            return {
                "status": "ok",
                "processed": result["processed"],
                "accepted": accepted,
                "ignored": ignored,
                "failed": failed,
            }
        if mode == "loop":
            results = run_loop(session_key, history_fetcher, poll_seconds=poll_seconds, max_iterations=max_iterations)
            processed = sum(item["processed"] for item in results)
            accepted = sum(1 for item in results for row in item["results"] if row["bridge_status"] == "accepted")
            ignored = sum(1 for item in results for row in item["results"] if row["bridge_status"] == "ignored")
            failed = sum(1 for item in results for row in item["results"] if row["bridge_status"] == "failed")
            return {
                "status": "ok",
                "processed": processed,
                "accepted": accepted,
                "ignored": ignored,
                "failed": failed,
            }
        return {"status": "failed", "processed": 0, "accepted": 0, "ignored": 0, "failed": 1}
    except Exception:
        return {"status": "failed", "processed": 0, "accepted": 0, "ignored": 0, "failed": 1}
