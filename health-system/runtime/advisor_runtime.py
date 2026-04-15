from __future__ import annotations

from typing import Any, Dict

from .token_logger import log_token_usage


def run_advisor_runtime(input_payload: Dict[str, Any]) -> Dict[str, Any]:
    brief = input_payload.get("brief", {})
    mode = input_payload.get("mode")
    snapshot_subset = input_payload.get("snapshot_subset", {})
    routing_metadata = input_payload.get("routing_metadata", {})

    slot = brief.get("slot", "unknown_slot")
    nudge_type = brief.get("nudge_type", "check_in")
    domain = brief.get("domain", "behavior")
    missing_signals = brief.get("missing_signals", [])
    simplification = brief.get("state_flags", {}).get("simplification_level", "normal")

    prompt = {
        "mode": mode,
        "slot": slot,
        "nudge_type": nudge_type,
        "domain": domain,
        "missing_signals": missing_signals,
        "snapshot_subset": snapshot_subset,
        "routing_metadata": routing_metadata,
        "simplification_level": simplification,
    }
    prompt_text = str(prompt)
    tokens_in = max(1, (len(prompt_text) + 3) // 4)

    if nudge_type == "coaching":
        message_text = "Quick reset option: want the minimum version for this block so it still counts?"
    elif nudge_type == "reminder":
        target = missing_signals[0].replace("_", " ") if missing_signals else "that"
        message_text = f"Quick check: any update on {target}?"
    else:
        target = missing_signals[0].replace("_", " ") if missing_signals else "how things are going"
        message_text = f"Quick check-in: any update on {target}?"

    tokens_out = max(1, (len(message_text) + 3) // 4)
    log_token_usage("advisor_runtime_proactive", tokens_in, tokens_out, ["proactive_brief", "snapshot_subset"])
    return {
        "input": input_payload,
        "output": {
            "approved": True,
            "message_text": message_text,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
        },
    }
