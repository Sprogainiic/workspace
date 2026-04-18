from __future__ import annotations

from typing import Any, Dict, List

REQUIRED_TOP_LEVEL_KEYS = {
    "INTENTS",
    "EXTRACTIONS",
    "FIELD_CONFIDENCE",
    "MEMORY_UPDATE_PROPOSALS",
    "AMBIGUITIES",
    "UNSAFE_TO_WRITE",
    "FOLLOWUP_NEEDED",
    "ROUTING_HINTS",
}

ALLOWED_CONFIDENCE = {"low", "medium", "high", "unsupported"}


def _validate_proposals(proposals: List[Dict[str, Any]]) -> List[str]:
    violations: List[str] = []
    for idx, proposal in enumerate(proposals):
        if not isinstance(proposal, dict):
            violations.append(f"proposal_{idx}_not_object")
            continue
        if not proposal.get("event_type"):
            violations.append(f"proposal_{idx}_missing_event_type")
        if not proposal.get("timestamp"):
            violations.append(f"proposal_{idx}_missing_timestamp")
        confidence = proposal.get("confidence")
        if confidence is not None and confidence not in ALLOWED_CONFIDENCE:
            violations.append(f"proposal_{idx}_bad_confidence")
    return violations


def validate_memory_adapter_output(payload: Dict[str, Any]) -> Dict[str, Any]:
    violations: List[str] = []
    if not isinstance(payload, dict):
        return {
            "status": "FAIL",
            "violations": ["payload_not_object"],
            "safe_to_ingest": False,
            "suggested_action": "reject",
            "notes": [],
        }

    missing = sorted(REQUIRED_TOP_LEVEL_KEYS - set(payload.keys()))
    violations.extend([f"missing_{key.lower()}" for key in missing])

    proposals = payload.get("MEMORY_UPDATE_PROPOSALS", [])
    if not isinstance(proposals, list):
        violations.append("memory_update_proposals_not_list")
        proposals = []

    routing = payload.get("ROUTING_HINTS", [])
    if not isinstance(routing, list):
        violations.append("routing_hints_not_list")

    followup_needed = payload.get("FOLLOWUP_NEEDED")
    if followup_needed not in {"yes", "no"}:
        violations.append("followup_needed_invalid")

    violations.extend(_validate_proposals(proposals))

    status = "FAIL" if violations else "PASS"
    return {
        "status": status,
        "violations": violations,
        "safe_to_ingest": status == "PASS",
        "suggested_action": "accept" if status == "PASS" else "reject",
        "notes": [],
    }
