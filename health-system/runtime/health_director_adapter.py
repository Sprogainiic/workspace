from __future__ import annotations

from typing import Any, Dict, List

from .token_logger import log_token_usage


def _route_specialists(domain: str, nudge_type: str, snapshot_subset: Dict[str, Any]) -> List[str]:
    routing: List[str] = ["Health Director"]
    fatigue = snapshot_subset.get("fatigue")
    motivation = snapshot_subset.get("motivation")

    if domain == "nutrition":
        routing.append("Dietitian")
    elif domain == "training":
        routing.append("Fitness Coach")
        if nudge_type == "coaching" or fatigue == "high" or motivation == "low":
            routing.append("Consistency Coach")
    elif domain == "behavior":
        routing.append("Consistency Coach")
    elif domain == "wrap_up":
        routing.append("Progress Analyst")
    return routing


def _render_message(slot: str, nudge_type: str, domain: str, brief: Dict[str, Any], snapshot_subset: Dict[str, Any]) -> str:
    missing = brief.get("missing_signals", [])
    target = missing[0].replace("_", " ") if missing else "how things are going"
    motivation = snapshot_subset.get("motivation")
    fatigue = snapshot_subset.get("fatigue")

    if domain == "nutrition":
        return f"Quick nutrition check: any update on {target}?"
    if domain == "training" and (nudge_type == "coaching" or fatigue == "high" or motivation == "low"):
        return "Quick reset: want the minimum version for today so the streak stays alive?"
    if domain == "wrap_up":
        return "Quick wrap-up: what got done today, even if it was the minimum?"
    return f"Quick check-in: any update on {target}?"


def run_health_director_proactive_turn(payload: Dict[str, Any]) -> Dict[str, Any]:
    slot = payload.get("slot", "")
    nudge_type = payload.get("nudge_type", "check_in")
    domain = payload.get("domain", "behavior")
    brief = payload.get("brief", {})
    snapshot_subset = payload.get("snapshot_subset", {})
    routing_metadata = payload.get("routing_metadata", {})
    activity_context = payload.get("activity_context", {})

    prompt = {
        "slot": slot,
        "nudge_type": nudge_type,
        "domain": domain,
        "brief": brief,
        "snapshot_subset": snapshot_subset,
        "routing_metadata": routing_metadata,
        "activity_context": activity_context,
    }
    prompt_text = str(prompt)
    tokens_in = max(1, (len(prompt_text) + 3) // 4)
    routing = _route_specialists(domain, nudge_type, snapshot_subset)
    message_text = _render_message(slot, nudge_type, domain, brief, snapshot_subset)
    tokens_out = max(1, (len(message_text) + 3) // 4)
    log_token_usage("health_director_orchestrated_proactive", tokens_in, tokens_out, ["proactive_brief", "snapshot_subset", "activity_context"])
    return {
        "approved": True,
        "message_text": message_text,
        "routing": routing,
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "runtime_mode": "orchestrated",
    }
