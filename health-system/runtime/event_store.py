from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


OUTCOME_EVENT_TYPES = {
    "workout_completed",
    "workout_skipped",
    "meal_logged",
    "restart_signal",
}

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "runtime" / "data"
EVENTS = DATA / "events" / "events.jsonl"
EVENTS.parent.mkdir(parents=True, exist_ok=True)


def store_events(validated_adapter_output: Dict[str, Any]) -> Dict[str, Any]:
    proposals: List[Dict[str, Any]] = validated_adapter_output.get("MEMORY_UPDATE_PROPOSALS", [])
    appended = []
    rejected = []

    for proposal in proposals:
        if proposal.get("safe_to_write") is False or proposal.get("write_type") == "reject":
            rejected.append(proposal)
            continue
        if proposal.get("confidence") == "low" and proposal.get("write_type") == "canonical_update":
            rejected.append(proposal)
            continue
        if proposal.get("write_scope") == "canonical" and proposal.get("confidence") == "low":
            rejected.append(proposal)
            continue
        # Normalize facts to object form (never scalar)
        event_type = proposal.get("event_type", "structured_memory_event")
        raw_value = proposal.get("value", proposal)
        if event_type == "meal_logged":
            facts = {"logged": bool(raw_value)}
        elif event_type == "fatigue_report":
            facts = {"fatigue": raw_value}
        elif event_type == "workout_skipped":
            facts = {"completed": False}
        elif event_type == "workout_completed":
            facts = {"completed": True}
        elif event_type == "outcome_signal" and isinstance(raw_value, dict):
            facts = raw_value
        else:
            # generic fallback
            facts = {"value": raw_value}

        if event_type in OUTCOME_EVENT_TYPES:
            facts["counts_as_outcome"] = True
        if proposal.get("outcome_label"):
            facts["outcome_label"] = proposal.get("outcome_label")
        if proposal.get("outcome_score") is not None:
            facts["outcome_score"] = proposal.get("outcome_score")

        event = {
            "event_id": proposal.get("event_id") or proposal.get("field", "event"),
            "timestamp": proposal.get("timestamp"),
            "event_type": event_type,
            "source_message_id": proposal.get("source_message_id", "unknown"),
            "facts": facts,
            "confidence": proposal.get("confidence", "medium"),
            "ambiguities": validated_adapter_output.get("AMBIGUITIES", []),
            "write_scope": "canonical" if proposal.get("confidence") in {"high", "medium"} else "transient",
            "safe_to_write": True,
        }
        with EVENTS.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
        appended.append(event)

    return {"appended": appended, "rejected": rejected, "event_path": str(EVENTS)}
