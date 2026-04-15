from __future__ import annotations

from typing import Any, Dict, List

from .token_logger import log_token_usage


def _build_stub_message(brief: Dict[str, Any]) -> str:
    nudge_type = brief.get("nudge_type", "check_in")
    missing_signals = brief.get("missing_signals", [])
    if nudge_type == "coaching":
        return "Quick reset option: want the minimum version for this block so it still counts?"
    if nudge_type == "reminder":
        target = missing_signals[0].replace("_", " ") if missing_signals else "that"
        return f"Quick check: any update on {target}?"
    target = missing_signals[0].replace("_", " ") if missing_signals else "how things are going"
    return f"Quick check-in: any update on {target}?"


def run_proactive_turn(payload: Dict[str, Any]) -> Dict[str, Any]:
    mode = payload.get("mode")
    brief = payload.get("brief", {})
    snapshot_subset = payload.get("snapshot_subset", {})
    routing_metadata = payload.get("routing_metadata", {})
    transport_target = payload.get("transport_target", {})

    prompt = {
        "mode": mode,
        "brief": brief,
        "snapshot_subset": snapshot_subset,
        "routing_metadata": routing_metadata,
        "transport_target": transport_target,
    }
    prompt_text = str(prompt)
    tokens_in = max(1, (len(prompt_text) + 3) // 4)
    message_text = _build_stub_message(brief)
    tokens_out = max(1, (len(message_text) + 3) // 4)
    runtime_mode = "stub"
    routing: List[str] = ["advisor_runtime_boundary", "health_director_proactive"]
    log_token_usage("advisor_runtime_proactive", tokens_in, tokens_out, ["proactive_brief", "snapshot_subset"])
    return {
        "approved": True,
        "message_text": message_text,
        "routing": routing,
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "runtime_mode": runtime_mode,
    }
