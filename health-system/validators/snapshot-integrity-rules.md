# Snapshot Integrity Rules

- low confidence never overwrites high confidence
- unsupported values never enter snapshot as factual state
- stale state may remain visible but should be marked stale
- evidence_event_ids must be present for updated fields
- open ambiguities must remain explicit until resolved
- snapshot values must not be treated as more precise than source events
