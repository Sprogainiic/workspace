from __future__ import annotations

from typing import Any, Dict, List, Optional

from .context_loader import load_context
from .event_store import store_events
from .snapshot_updater import update_snapshot
from .daily_summary import generate_daily_summary
from .validator import validate_memory_adapter_output
from .token_logger import log_token_usage
from .nudge_selector import select_nudge
from .nudge_log import log_nudge_decision
from .advisor_runtime import run_proactive_turn
from .outbound_transport import send_message


def _route(message: str) -> Dict[str, Any]:
    m = message.lower()
    if "lol" in m and len(m.split()) <= 2:
        return {"mode": "log_only", "decision_complexity": "low", "unresolved": False, "still_unresolved": False}
    if any(x in m for x in ["what should i eat", "what should i eat tonight", "can't be bothered to cook"]):
        return {"mode": "specialist_single", "decision_complexity": "medium", "unresolved": False, "still_unresolved": False}
    if any(x in m for x in ["should i still train", "minimum", "what's the absolute minimum"]):
        return {"mode": "director_merge", "decision_complexity": "medium", "unresolved": False, "still_unresolved": False}
    if any(x in m for x in ["week", "plateau", "progress"]):
        return {"mode": "weekly_analysis", "decision_complexity": "high", "unresolved": False, "still_unresolved": False}
    if any(x in m for x in ["maybe", "uncertain", "maybe i'll train later"]):
        return {"mode": "state_update_only", "decision_complexity": "low", "unresolved": True, "still_unresolved": False}
    return {"mode": "state_update_only", "decision_complexity": "low", "unresolved": False, "still_unresolved": False}


def memory_adapter(message: str, message_id: str, timestamp: str) -> Dict[str, Any]:
    m = message.lower()
    intents: List[str] = []
    extractions: Dict[str, Any] = {}
    conf = {}
    proposals: List[Dict[str, Any]] = []
    routing = []

    if any(x in m for x in ["ate", "meal", "salad", "pasta", "bread", "sweets", "pizza", "burgers"]):
        intents.append("log_meal")
        extractions["meal_logged"] = True
        if "tuna salad" in m:
            extractions["foods"] = ["tuna salad", "bread"] if "bread" in m else ["tuna salad"]
            extractions["protein_present"] = True
            conf["foods"] = "medium"
            proposals.append({"field": "meal_logged", "value": True, "confidence": "medium", "write_type": "canonical_append", "safe_to_write": True, "write_scope": "canonical", "event_id": f"ev_{message_id}_meal", "event_type": "meal_logged", "timestamp": timestamp, "source_message_id": message_id})
        elif "pasta" in m:
            extractions["foods"] = ["pasta"]
            conf["foods"] = "medium"
            proposals.append({"field": "meal_logged", "value": True, "confidence": "medium", "write_type": "canonical_append", "safe_to_write": True, "write_scope": "canonical", "event_id": f"ev_{message_id}_meal", "event_type": "meal_logged", "timestamp": timestamp, "source_message_id": message_id})
        elif "bad" in m:
            extractions["meal_quality_self_report"] = "poor"
            conf["meal_quality_self_report"] = "low"
            proposals.append({"field": "meal_quality_self_report", "value": "poor", "confidence": "low", "write_type": "transient_state", "safe_to_write": False, "write_scope": "transient", "event_id": f"ev_{message_id}_mealq", "event_type": "meal_quality", "timestamp": timestamp, "source_message_id": message_id})
        elif "pizza" in m:
            extractions["food_question"] = "pizza"
        elif "burgers" in m:
            extractions["craving"] = "burgers"

    if any(x in m for x in ["tired", "energy low", "sleep", "headache", "low energy", "super tired"]):
        intents.append("status_update")
        extractions["fatigue"] = "high" if "super tired" in m or "tired" in m else "low"
        conf["fatigue"] = "high"
        proposals.append({"field": "fatigue", "value": extractions["fatigue"], "confidence": "high", "write_type": "canonical_append", "safe_to_write": True, "write_scope": "canonical", "event_id": f"ev_{message_id}_fatigue", "event_type": "fatigue_report", "timestamp": timestamp, "source_message_id": message_id})

    if any(x in m for x in ["skip", "skipping workout", "didn't do the workout", "no chance", "not doing intervals"]):
        intents.append("log_workout")
        extractions["workout_completed"] = False
        conf["workout_completed"] = "medium"
        proposals.append({"field": "workout_completed", "value": False, "confidence": "medium", "write_type": "canonical_append", "safe_to_write": True, "write_scope": "canonical", "event_id": f"ev_{message_id}_workout", "event_type": "workout_skipped", "timestamp": timestamp, "source_message_id": message_id})

    if any(x in m for x in ["maybe i'll train later", "should i still train", "minimum"]):
        intents.append("decision_request")
        extractions["workout_status"] = "undecided" if "later" in m else "requested"
        conf["workout_status"] = "medium"

    if "guilty" in m:
        intents.append("emotional_signal")
        extractions["guilt_present"] = True
        conf["guilt_present"] = "high"

    if any(x in m for x in ["do not feel like doing anything", "don't feel like doing anything", "low motivation", "avoid", "shutdown"]):
        intents.extend([i for i in ["status_update", "emotional_signal"] if i not in intents])
        extractions["motivation"] = "low"
        extractions["activation_resistance"] = "high"
        conf["motivation"] = "high"
        proposals.append({"field": "motivation", "value": "low", "confidence": "medium", "write_type": "transient_state", "safe_to_write": True, "write_scope": "transient", "event_id": f"ev_{message_id}_motivation", "event_type": "motivation_signal", "timestamp": timestamp, "source_message_id": message_id})

    if any(x in m for x in ["evening check-in", "did not do much", "did not completely crash"]):
        intents.extend([i for i in ["status_update", "pattern_signal"] if i not in intents])
        extractions["adherence_signal"] = "mixed"
        extractions["behavior_signal"] = "fragile_but_not_collapsed"
        conf["adherence_signal"] = "low"
        proposals.append({"field": "behavior_state", "value": "fragile", "confidence": "low", "write_type": "transient_state", "safe_to_write": True, "write_scope": "transient", "event_id": f"ev_{message_id}_checkin", "event_type": "checkin_signal", "timestamp": timestamp, "source_message_id": message_id})

    if any(x in m for x in ["restarting tomorrow", "restart tomorrow", "messed up a bit today"]):
        intents.extend([i for i in ["status_update", "pattern_signal", "emotional_signal"] if i not in intents])
        extractions["recovery_intent"] = True
        extractions["behavior_state"] = "restart_cycle"
        conf["behavior_state"] = "medium"
        proposals.append({"field": "behavior_state", "value": "restart_cycle", "confidence": "medium", "write_type": "canonical_append", "safe_to_write": True, "write_scope": "canonical", "event_id": f"ev_{message_id}_restart", "event_type": "restart_signal", "timestamp": timestamp, "source_message_id": message_id})

    if "can\'t be bothered to cook" in m or "can't be bothered to cook" in m:
        intents.append("decision_request")
        extractions["meal_request"] = "dinner"
        extractions["motivation_for_cooking"] = "low"
        conf["motivation_for_cooking"] = "high"

    if not intents:
        intents = ["unclear"]

    if any(x in m for x in ["tuna", "salad", "pasta", "cook", "diet", "eat tonight"]):
        routing.extend(["Dietitian"])
    if any(x in m for x in ["train", "workout", "skip", "tired", "minimum"]):
        routing.extend(["Fitness Coach", "Consistency Coach"])
    if any(x in m for x in ["cook", "eat tonight", "meal"]):
        routing.append("Personal Chef")
    if any(x in m for x in ["bad", "guilty", "maybe", "skip", "low motivation", "do not feel like doing anything", "did not do much", "restarting tomorrow", "messed up a bit today"]) and "Consistency Coach" not in routing:
        routing.append("Consistency Coach")

    routing = list(dict.fromkeys(routing))
    if intents == ["unclear"]:
        routing = ["No specialist needed"]

    return {
        "INTENTS": intents,
        "EXTRACTIONS": extractions,
        "FIELD_CONFIDENCE": conf,
        "MEMORY_UPDATE_PROPOSALS": proposals,
        "AMBIGUITIES": [] if intents != ["unclear"] else ["unsupported_signal_only"],
        "UNSAFE_TO_WRITE": [],
        "FOLLOWUP_NEEDED": "no" if intents != ["unclear"] else "yes",
        "ROUTING_HINTS": routing
    }


def _snapshot_subset_for_proactive(current_snapshot: Dict[str, Any]) -> Dict[str, Any]:
    state = current_snapshot.get("state", {}) if isinstance(current_snapshot, dict) else {}
    return {
        "fatigue": state.get("fatigue", {}).get("value"),
        "motivation": state.get("motivation", {}).get("value"),
        "behavior_state": state.get("behavior_state", {}).get("value"),
        "simplification_level": current_snapshot.get("simplification_level", "normal") if isinstance(current_snapshot, dict) else "normal",
    }


def evaluate_nudge_slot(
    current_snapshot: Dict[str, Any],
    todays_events: List[Dict[str, Any]],
    daily_summary: Optional[Dict[str, Any]],
    recent_user_activity: List[Dict[str, Any]],
    current_slot: str,
    now,
    policy_overrides: Optional[Dict[str, Any]] = None,
    outbound_channel: str = "test",
    recipient_id: str = "local-test-recipient",
    sent_nudges_today: Optional[List[Dict[str, Any]]] = None,
    state_source: str = "persisted",
    allow_test_fixture: bool = False,
) -> Dict[str, Any]:
    if (not allow_test_fixture) and (current_snapshot is None or todays_events is None or daily_summary is None or sent_nudges_today is None):
        log_entry = log_nudge_decision({
            "timestamp": now.isoformat(),
            "slot": current_slot,
            "evaluated": True,
            "send": False,
            "skip_reason": "missing_runtime_state",
            "nudge_type": None,
            "domain": None,
            "tokens_in": 0,
            "tokens_out": 0,
            "message_intent": None,
            "fingerprint": None,
            "message_fingerprint": None,
            "runtime_mode": None,
            "state_source": state_source,
        })
        return {
            "evaluated": True,
            "selection": {"send": False, "skip_reason": "missing_runtime_state"},
            "log": log_entry,
            "stopped": True,
            "error": "missing_runtime_state",
        }

    selection = select_nudge(
        current_snapshot=current_snapshot,
        todays_events=todays_events,
        daily_summary=daily_summary,
        sent_nudges_today=sent_nudges_today,
        recent_user_activity=recent_user_activity,
        current_slot=current_slot,
        now=now,
        policy_overrides=policy_overrides,
    )

    if not selection.get("send"):
        log_entry = log_nudge_decision({
            "timestamp": now.isoformat(),
            "slot": current_slot,
            "evaluated": True,
            "send": False,
            "skip_reason": selection.get("skip_reason"),
            "nudge_type": None,
            "domain": None,
            "tokens_in": 0,
            "tokens_out": 0,
            "message_intent": None,
            "fingerprint": None,
            "message_fingerprint": None,
            "runtime_mode": None,
            "state_source": state_source,
        })
        return {
            "evaluated": True,
            "selection": selection,
            "log": log_entry,
            "stopped": True,
        }

    proactive_brief = selection["payload_brief"]
    proactive_payload = {
        "mode": "proactive",
        "brief": proactive_brief,
        "snapshot_subset": _snapshot_subset_for_proactive(current_snapshot),
        "routing_metadata": selection.get("route", {}),
        "transport_target": {
            "channel": outbound_channel,
            "recipient_id": recipient_id,
        },
    }
    runtime_result = run_proactive_turn(proactive_payload)
    transport_result = send_message(
        channel=outbound_channel,
        recipient_id=recipient_id,
        message_text=runtime_result["message_text"],
    ) if runtime_result["approved"] else {"sent": False}
    log_entry = log_nudge_decision({
        "timestamp": now.isoformat(),
        "slot": selection["slot"],
        "evaluated": True,
        "send": bool(runtime_result["approved"] and transport_result.get("sent")),
        "skip_reason": None if runtime_result["approved"] else "not_approved",
        "nudge_type": selection["nudge_type"],
        "domain": selection["domain"],
        "tokens_in": runtime_result["tokens_in"],
        "tokens_out": runtime_result["tokens_out"],
        "message_intent": selection["message_intent"],
        "fingerprint": selection["fingerprint"],
        "message_fingerprint": selection["fingerprint"],
        "runtime_mode": runtime_result["runtime_mode"],
        "state_source": state_source,
    })
    return {
        "evaluated": True,
        "selection": selection,
        "proactive_brief": proactive_brief,
        "advisor_runtime": runtime_result,
        "transport_result": transport_result,
        "log": log_entry,
        "state_source": state_source,
    }


def run_chat_turn(message: str, message_id: str, timestamp: str) -> Dict[str, Any]:
    adapter = memory_adapter(message, message_id, timestamp)
    validation = validate_memory_adapter_output(adapter)

    if adapter["INTENTS"] == ["unclear"] and not adapter["EXTRACTIONS"] and adapter["ROUTING_HINTS"] == ["No specialist needed"]:
        log_token_usage("chat_gateway", 8, 4, [])
        return {
            "validation": validation,
            "events": {"appended": [], "rejected": [], "event_path": None},
            "snapshot": None,
            "context": {"context_payload": {}, "token_estimate": 1, "layers_used": []},
            "daily_summary": None,
            "routing": ["no_specialist_needed"],
            "response_mode": "no_op"
        }

    log_token_usage("chat_gateway", 120, 40, ["snapshot"])
    if validation["status"] == "FAIL":
        return {"validation": validation, "stopped": True, "reason": "validation_fail"}

    event_result = store_events(adapter)
    snapshot = update_snapshot(event_result["appended"])
    context = load_context(decision_complexity="medium" if "what should i eat" in message.lower() else "low", unresolved=False, still_unresolved=False)
    daily = generate_daily_summary(event_result["appended"], snapshot)
    log_token_usage("health_director", 180, 90, context["layers_used"])
    return {
        "validation": validation,
        "events": event_result,
        "snapshot": snapshot,
        "context": context,
        "daily_summary": daily,
        "routing": adapter["ROUTING_HINTS"],
    }
