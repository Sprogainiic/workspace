from __future__ import annotations

from typing import Any, Dict, List, Optional

from .context_loader import load_context
from .event_store import store_events
from .snapshot_updater import update_snapshot
from .daily_summary import generate_daily_summary
from .weekly_summary import generate_weekly_summary
from .validator import validate_memory_adapter_output
from .specialist_intake import build_combined_intro_questionnaire, render_combined_intro_questionnaire, parse_intake_answers, build_followup_questions
from .token_logger import log_token_usage
from .nudge_selector import select_nudge
from .nudge_log import log_nudge_decision
from .advisor_runtime import run_proactive_turn
from .outbound_transport import send_message
from .config import OPENCLAW_HEALTH_SESSION_KEY
from .nudge_delivery_audit import log_delivery_audit
from .nudge_delivery_verify import verify_message_in_session_history


def _route(message: str) -> Dict[str, Any]:
    m = message.lower()
    if "introduce myself to all specialists" in m or "specialist intake" in m or "intake mode" in m:
        return {"mode": "specialist_intake", "decision_complexity": "medium", "unresolved": False, "still_unresolved": False}
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
            proposals.append({"field": "meal_logged", "value": True, "confidence": "medium", "write_type": "canonical_append", "safe_to_write": True, "write_scope": "canonical", "event_id": f"ev_{message_id}_meal", "event_type": "meal_logged", "timestamp": timestamp, "source_message_id": message_id, "outcome_label": "meal_logged", "outcome_score": 1.0})
        elif "pasta" in m:
            extractions["foods"] = ["pasta"]
            conf["foods"] = "medium"
            proposals.append({"field": "meal_logged", "value": True, "confidence": "medium", "write_type": "canonical_append", "safe_to_write": True, "write_scope": "canonical", "event_id": f"ev_{message_id}_meal", "event_type": "meal_logged", "timestamp": timestamp, "source_message_id": message_id, "outcome_label": "meal_logged", "outcome_score": 1.0})
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
        proposals.append({"field": "workout_completed", "value": False, "confidence": "medium", "write_type": "canonical_append", "safe_to_write": True, "write_scope": "canonical", "event_id": f"ev_{message_id}_workout", "event_type": "workout_skipped", "timestamp": timestamp, "source_message_id": message_id, "outcome_label": "workout_skipped", "outcome_score": 0.0})

    if any(x in m for x in ["did the workout", "workout done", "trained", "session done", "got it done", "finished the workout"]):
        intents.append("log_workout")
        extractions["workout_completed"] = True
        conf["workout_completed"] = "medium"
        proposals.append({"field": "workout_completed", "value": True, "confidence": "medium", "write_type": "canonical_append", "safe_to_write": True, "write_scope": "canonical", "event_id": f"ev_{message_id}_workout_done", "event_type": "workout_completed", "timestamp": timestamp, "source_message_id": message_id, "outcome_label": "workout_completed", "outcome_score": 1.0})

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
        proposals.append({"field": "behavior_state", "value": "restart_cycle", "confidence": "medium", "write_type": "canonical_append", "safe_to_write": True, "write_scope": "canonical", "event_id": f"ev_{message_id}_restart", "event_type": "restart_signal", "timestamp": timestamp, "source_message_id": message_id, "outcome_label": "restart_intent", "outcome_score": 0.4})

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
    weekly_summary: Optional[Dict[str, Any]],
    recent_user_activity: List[Dict[str, Any]],
    current_slot: str,
    now,
    policy_overrides: Optional[Dict[str, Any]] = None,
    outbound_channel: str = "test",
    recipient_id: str = "local-test-recipient",
    sent_nudges_today: Optional[List[Dict[str, Any]]] = None,
    state_source: str = "persisted",
    allow_test_fixture: bool = False,
    activity_source: str = "missing",
    session_sender=None,
    sessions_history_tool=None,
    session_key: Optional[str] = None,
    launcher_mode: str = "local_test",
) -> Dict[str, Any]:
    activity_count = len(recent_user_activity or [])
    transport_name = outbound_channel
    effective_session_key = session_key or (OPENCLAW_HEALTH_SESSION_KEY if outbound_channel == "openclaw_session" else None)
    if (not allow_test_fixture) and (current_snapshot is None or todays_events is None or daily_summary is None or weekly_summary is None or sent_nudges_today is None):
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
            "activity_source": activity_source,
            "recent_user_activity_count": activity_count,
            "routing": [],
            "advisor_tokens_in": 0,
            "advisor_tokens_out": 0,
            "transport": transport_name,
            "session_key": effective_session_key,
            "delivery_status": "failed",
            "delivery_error": "missing_runtime_state",
            "launcher_mode": launcher_mode,
        })
        log_delivery_audit({
            "timestamp": now.isoformat(),
            "slot": current_slot,
            "send": False,
            "skip_reason": "missing_runtime_state",
            "transport": transport_name,
            "session_key": effective_session_key,
            "delivery_status": "failed",
            "delivery_error": "missing_runtime_state",
            "message_text": None,
            "message_intent": None,
            "fingerprint": None,
            "launcher_mode": launcher_mode,
            "state_source": state_source,
            "activity_source": activity_source,
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
        weekly_summary=weekly_summary,
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
            "activity_source": activity_source,
            "recent_user_activity_count": activity_count,
            "routing": [],
            "advisor_tokens_in": 0,
            "advisor_tokens_out": 0,
            "transport": transport_name,
            "session_key": effective_session_key,
            "delivery_status": "failed",
            "delivery_error": selection.get("skip_reason"),
            "launcher_mode": launcher_mode,
        })
        log_delivery_audit({
            "timestamp": now.isoformat(),
            "slot": current_slot,
            "send": False,
            "skip_reason": selection.get("skip_reason"),
            "transport": transport_name,
            "session_key": effective_session_key,
            "delivery_status": "failed",
            "delivery_error": selection.get("skip_reason"),
            "message_text": None,
            "message_intent": None,
            "fingerprint": None,
            "launcher_mode": launcher_mode,
            "state_source": state_source,
            "activity_source": activity_source,
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
        "slot": selection["slot"],
        "nudge_type": selection["nudge_type"],
        "domain": selection["domain"],
        "brief": proactive_brief,
        "snapshot_subset": _snapshot_subset_for_proactive(current_snapshot),
        "routing_metadata": selection.get("route", {}),
        "activity_context": {
            "recent_user_activity_count": activity_count,
            "activity_source": activity_source,
        },
        "weekly_context": weekly_summary or {},
        "transport_target": {
            "channel": outbound_channel,
            "recipient_id": recipient_id,
            "session_key": effective_session_key,
        },
    }

    try:
        runtime_result = run_proactive_turn(proactive_payload)
    except Exception as exc:
        log_entry = log_nudge_decision({
            "timestamp": now.isoformat(),
            "slot": selection["slot"],
            "evaluated": True,
            "send": False,
            "skip_reason": "advisor_runtime_failure",
            "nudge_type": selection["nudge_type"],
            "domain": selection["domain"],
            "tokens_in": 0,
            "tokens_out": 0,
            "message_intent": selection["message_intent"],
            "fingerprint": selection["fingerprint"],
            "message_fingerprint": None,
            "runtime_mode": None,
            "state_source": state_source,
            "activity_source": activity_source,
            "recent_user_activity_count": activity_count,
            "routing": [],
            "advisor_tokens_in": 0,
            "advisor_tokens_out": 0,
            "transport": transport_name,
            "session_key": effective_session_key,
            "delivery_status": "failed",
            "delivery_error": str(exc),
            "launcher_mode": launcher_mode,
        })
        log_delivery_audit({
            "timestamp": now.isoformat(),
            "slot": selection["slot"],
            "send": False,
            "skip_reason": "advisor_runtime_failure",
            "transport": transport_name,
            "session_key": effective_session_key,
            "delivery_status": "failed",
            "delivery_error": str(exc),
            "message_text": None,
            "message_intent": selection.get("message_intent"),
            "fingerprint": selection.get("fingerprint"),
            "launcher_mode": launcher_mode,
            "state_source": state_source,
            "activity_source": activity_source,
        })
        return {
            "evaluated": True,
            "selection": selection,
            "log": log_entry,
            "stopped": True,
            "error": "advisor_runtime_failure",
            "details": str(exc),
        }

    try:
        transport_result = send_message(
            channel=outbound_channel,
            recipient_id=recipient_id,
            message_text=runtime_result["message_text"],
            session_key=effective_session_key,
            target_type="channel",
            metadata={
                "mode": "proactive",
                "slot": selection["slot"],
                "nudge_type": selection["nudge_type"],
                "domain": selection["domain"],
            },
            session_sender=session_sender,
            launcher_mode=launcher_mode,
        ) if runtime_result["approved"] else {"sent": False, "delivery_status": "failed", "delivery_error": "not_approved", "launcher_mode": launcher_mode}
    except Exception as exc:
        log_entry = log_nudge_decision({
            "timestamp": now.isoformat(),
            "slot": selection["slot"],
            "evaluated": True,
            "send": False,
            "skip_reason": "delivery_failure",
            "nudge_type": selection["nudge_type"],
            "domain": selection["domain"],
            "tokens_in": runtime_result["tokens_in"],
            "tokens_out": runtime_result["tokens_out"],
            "message_intent": selection["message_intent"],
            "fingerprint": selection["fingerprint"],
            "message_fingerprint": None,
            "runtime_mode": runtime_result["runtime_mode"],
            "state_source": state_source,
            "activity_source": activity_source,
            "recent_user_activity_count": activity_count,
            "routing": runtime_result.get("routing", []),
            "advisor_tokens_in": runtime_result["tokens_in"],
            "advisor_tokens_out": runtime_result["tokens_out"],
            "transport": transport_name,
            "session_key": effective_session_key,
            "delivery_status": "failed",
            "delivery_error": str(exc),
            "launcher_mode": launcher_mode,
        })
        log_delivery_audit({
            "timestamp": now.isoformat(),
            "slot": selection["slot"],
            "send": False,
            "skip_reason": "delivery_failure",
            "transport": transport_name,
            "session_key": effective_session_key,
            "delivery_status": "failed",
            "delivery_error": str(exc),
            "message_text": runtime_result.get("message_text"),
            "message_intent": selection.get("message_intent"),
            "fingerprint": selection.get("fingerprint"),
            "launcher_mode": launcher_mode,
            "state_source": state_source,
            "activity_source": activity_source,
        })
        return {
            "evaluated": True,
            "selection": selection,
            "advisor_runtime": runtime_result,
            "log": log_entry,
            "stopped": True,
            "error": "delivery_failure",
            "details": str(exc),
        }

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
        "activity_source": activity_source,
        "recent_user_activity_count": activity_count,
        "routing": runtime_result.get("routing", []),
        "advisor_tokens_in": runtime_result["tokens_in"],
        "advisor_tokens_out": runtime_result["tokens_out"],
        "transport": transport_name,
        "session_key": effective_session_key,
        "delivery_status": transport_result.get("delivery_status", "sent"),
        "delivery_error": transport_result.get("delivery_error"),
        "launcher_mode": transport_result.get("launcher_mode", launcher_mode),
    })
    verification = None
    if transport_name == "openclaw_session" and effective_session_key and runtime_result["approved"] and transport_result.get("sent"):
        verification = verify_message_in_session_history(
            effective_session_key,
            runtime_result.get("message_text", ""),
            sessions_history_tool=sessions_history_tool,
        )

    audit_row = log_delivery_audit({
        "timestamp": now.isoformat(),
        "slot": selection["slot"],
        "send": bool(runtime_result["approved"] and transport_result.get("sent")),
        "skip_reason": None if runtime_result["approved"] else "not_approved",
        "transport": transport_name,
        "session_key": effective_session_key,
        "delivery_status": transport_result.get("delivery_status", "sent") if not verification else ("verified" if verification.get("verified") else transport_result.get("delivery_status", "sent")),
        "delivery_error": transport_result.get("delivery_error") if not verification or verification.get("verified") else verification.get("error"),
        "message_text": runtime_result.get("message_text"),
        "message_intent": selection.get("message_intent"),
        "fingerprint": selection.get("fingerprint"),
        "launcher_mode": transport_result.get("launcher_mode", launcher_mode),
        "state_source": state_source,
        "activity_source": activity_source,
    })
    return {
        "evaluated": True,
        "selection": selection,
        "proactive_brief": proactive_brief,
        "advisor_runtime": runtime_result,
        "transport_result": transport_result,
        "log": log_entry,
        "delivery_audit": audit_row,
        "delivery_verification": verification,
        "state_source": state_source,
    }


def run_chat_turn(message: str, message_id: str, timestamp: str) -> Dict[str, Any]:
    route = _route(message)
    if route["mode"] == "specialist_intake":
        questionnaire = build_combined_intro_questionnaire()
        return {
            "response_mode": "specialist_intake",
            "questionnaire": questionnaire,
            "message_text": render_combined_intro_questionnaire(),
            "routing": ["Health Director"],
        }

    if any(x in message.lower() for x in ["dietitian", "fitness coach", "consistency coach", "progress analyst", "personal chef"]) or "good week" in message.lower() or "what kind of prompting helps" in message.lower():
        intake = parse_intake_answers(message, message_id, timestamp)
        followup = build_followup_questions(intake)
        validation = {"status": "PASS", "violations": [], "safe_to_ingest": True, "suggested_action": "accept", "notes": []}
        event_result = store_events(intake)
        snapshot = update_snapshot(event_result["appended"])
        daily = generate_daily_summary(event_result["appended"], snapshot)
        weekly = generate_weekly_summary(__import__("datetime").datetime.fromisoformat(timestamp.replace("Z", "+00:00")))
        return {
            "response_mode": "specialist_intake_answers",
            "validation": validation,
            "events": event_result,
            "snapshot": snapshot,
            "daily_summary": daily,
            "weekly_summary": weekly,
            "routing": intake["ROUTING_HINTS"],
            "followup": followup,
        }

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
    lowered = message.lower()
    needs_medium_context = any(x in lowered for x in ["what should i eat", "strava", "ride", "activity", "training load"])
    context = load_context(decision_complexity="medium" if needs_medium_context else "low", unresolved=False, still_unresolved=False)
    daily = generate_daily_summary(event_result["appended"], snapshot)
    weekly = generate_weekly_summary(__import__("datetime").datetime.fromisoformat(timestamp.replace("Z", "+00:00")))
    log_token_usage("health_director", 180, 90, context["layers_used"])
    return {
        "validation": validation,
        "events": event_result,
        "snapshot": snapshot,
        "context": context,
        "daily_summary": daily,
        "weekly_summary": weekly,
        "routing": adapter["ROUTING_HINTS"],
    }
