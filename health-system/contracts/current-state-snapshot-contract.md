# Current State Snapshot Contract

## Purpose

The Current State Snapshot is the default runtime context object for the health system.
It exists to replace broad loading of raw chat, multiple metric files, and long daily logs on routine turns.

## Rules

- snapshot is derived, not raw
- snapshot may inform decisions but may not overwrite more precise underlying records
- every field must carry confidence, updated_at, evidence_event_ids, and staleness
- low-confidence inputs must update transient or low-confidence state, not hardened canonical facts
- stale fields must lose priority in planning

## Default runtime use

Load this object first for:
- Chat Gateway
- Health Director
- specialist routing
- specialist briefs
- validation checks that depend on current state

## Snapshot authority boundaries

Snapshot may summarize:
- current operational state
- active risks
- simplification mode
- open ambiguities

Snapshot may not:
- replace raw message audit data
- erase structured event detail
- convert interpretation into fact
- silently overwrite higher-confidence state with weaker evidence
