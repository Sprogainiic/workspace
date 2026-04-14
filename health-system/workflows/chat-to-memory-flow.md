# Chat -> Memory Flow

User Message
-> Chat Gateway classification
-> Conversation Memory Adapter on current message only
-> deterministic memory write guard

If FAIL:
-> reject write
-> store no canonical change
-> keep ambiguity note if useful

If WARN:
-> persist only safe structured event fields
-> update snapshot conservatively
-> keep ambiguity unresolved

If PASS:
-> persist structured event
-> update snapshot via `workflows/snapshot-update-flow.md`

Rules:
- raw chat is audit data, not default runtime context
- structured events are the primary factual substrate
- snapshot is updated from approved events, not directly from raw messages
- low-confidence ambiguous input must not harden into canonical fact
