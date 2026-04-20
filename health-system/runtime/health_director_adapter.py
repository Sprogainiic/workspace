from __future__ import annotations

from typing import Any, Dict, List

from .token_logger import log_token_usage


def _choose_model(slot: str, payload: Dict[str, Any]) -> str:
    model_routing = payload.get("model_routing", {}) if isinstance(payload, dict) else {}
    primary = model_routing.get("primary_model") or "openai/gpt-5.4"
    fallback = model_routing.get("fallback_model") or primary
    simple_slot = bool(model_routing.get("simple_slot", False))
    if simple_slot:
        return primary
    return primary or fallback




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
    send_style = brief.get("send_style", "short")
    state_flags = brief.get("state_flags", {})
    last_outcome = state_flags.get("last_outcome_label")
    weekly_reflection = brief.get("weekly_reflection", {})
    reflection_summary = weekly_reflection.get("summary")

    if domain == "nutrition":
        if send_style == "gentle":
            return f"Low-pressure nutrition check: any update on {target}?"
        if send_style == "direct":
            return f"Quick nutrition update: did {target.replace(' status', '')} happen?"
        return f"Quick nutrition check: any update on {target}?"
    if domain == "training" and (nudge_type == "coaching" or fatigue == "high" or motivation == "low"):
        if send_style == "gentle":
            return "Gentle reset: want the smallest doable version for today?"
        if send_style == "reset":
            return "Reset check: want to call today a restart and pick the minimum viable training win?"
        return "Quick reset: want the minimum version for today so the streak stays alive?"
    if domain == "wrap_up":
        if send_style == "gentle":
            return "Gentle wrap-up: what actually got done today, even if it was small?"
        if send_style == "direct":
            return "Quick wrap-up: what got done today?"
        if send_style == "reset" and reflection_summary:
            return "Reset wrap-up: what was today's actual outcome, so we can break the restart loop cleanly?"
        if last_outcome:
            return f"Quick wrap-up: what was the actual outcome today after {last_outcome.replace('_', ' ')}?"
        return "Quick wrap-up: what got done today, even if it was the minimum?"
    if send_style == "gentle":
        return f"Low-pressure check-in: any update on {target}?"
    if send_style == "direct":
        return f"Quick update: did {target.replace(' status', '')} happen?"
    if send_style == "reset":
        if reflection_summary:
            return f"Reset check: where does {target} stand now, and is this another restart-loop day or a clean reset?"
        return f"Reset check: where does {target} stand now?"
    return f"Quick check-in: any update on {target}?"


def run_health_director_proactive_turn(payload: Dict[str, Any]) -> Dict[str, Any]:
    slot = payload.get("slot", "")
    nudge_type = payload.get("nudge_type", "check_in")
    domain = payload.get("domain", "behavior")
    brief = payload.get("brief", {})
    snapshot_subset = payload.get("snapshot_subset", {})
    routing_metadata = payload.get("routing_metadata", {})
    activity_context = payload.get("activity_context", {})
    model_routing = payload.get("model_routing", {}) if isinstance(payload, dict) else {}
    selected_model = _choose_model(slot, payload)

    prompt = {
        "slot": slot,
        "nudge_type": nudge_type,
        "domain": domain,
        "brief": brief,
        "snapshot_subset": snapshot_subset,
        "routing_metadata": routing_metadata,
        "activity_context": activity_context,
        "selected_model": selected_model,
    }
    prompt_text = str(prompt)
    tokens_in = max(1, (len(prompt_text) + 3) // 4)
    routing = _route_specialists(domain, nudge_type, snapshot_subset)
    message_text = _render_message(slot, nudge_type, domain, brief, snapshot_subset)
    tokens_out = max(1, (len(message_text) + 3) // 4)
    log_token_usage(f"health_director_orchestrated_proactive:{selected_model}", tokens_in, tokens_out, ["proactive_brief", "snapshot_subset", "activity_context", selected_model])
    return {
        "approved": True,
        "message_text": message_text,
        "routing": routing,
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "runtime_mode": "orchestrated",
        "selected_model": selected_model,
        "model_routing": model_routing,
    }
