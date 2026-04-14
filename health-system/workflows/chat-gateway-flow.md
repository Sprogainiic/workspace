# Chat Gateway Flow

User Message
-> Chat Gateway
-> Load current state snapshot only
-> Route turn using `workflows/decision-routing-flow.md`

If mode = log_only | state_update_only:
-> Conversation Memory Adapter on current message only
-> deterministic memory write guard
-> approved structured events
-> snapshot update
-> optional micro-response

If mode = specialist_single | director_merge:
-> build only required specialist briefs
-> call only required specialists
-> deterministic validation
-> Health Director final decision

If mode = weekly_analysis:
-> load latest weekly summary before broader retrieval
-> Progress Analyst only if needed
-> Health Director final decision

Raw chat excerpts are loaded only for ambiguity_review or contradiction resolution.
