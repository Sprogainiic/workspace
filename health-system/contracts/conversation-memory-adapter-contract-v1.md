# Conversation Memory Adapter Contract v2

## Role

Convert a single current user message into structured, confidence-aware event proposals.

## Purpose

The adapter exists to produce safe structured events with minimal context usage.
It is not user-facing and it does not write canonical memory directly.

## Default inputs
```json
{
  "message_text": "raw user message",
  "timestamp": "ISO-8601 string",
  "message_id": "string",
  "snapshot_context": {
    "relevant_state": {},
    "dedupe_markers": [],
    "open_ambiguities": []
  }
}
```

## Input rules
- use the current message as the primary evidence source
- do not rely on broad recent chat history by default
- request targeted raw excerpts only when ambiguity or contradiction requires it

## Output
The adapter MUST produce:
- INTENTS
- EXTRACTIONS
- FIELD_CONFIDENCE
- STRUCTURED_EVENT_PROPOSALS
- AMBIGUITIES
- UNSAFE_TO_WRITE
- FOLLOWUP_NEEDED
- ROUTING_HINTS

## Hard rules
- preserve ambiguity
- separate fact from interpretation
- prefer partial extraction over fake precision
- low-confidence input must not overwrite stronger existing state
- emit event proposals, not direct canonical writes
