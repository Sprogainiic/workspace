# Snapshot Update Flow

User message
-> lightweight intent routing
-> Conversation Memory Adapter on current message only
-> deterministic memory write guard
-> approved structured events
-> Current State Snapshot updater
-> persist snapshot delta

Rules:
- update snapshot on event approval, not on raw message arrival
- preserve confidence, evidence links, and staleness
- do not force certainty where ambiguity remains
