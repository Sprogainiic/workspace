# Lightweight Chat Turn Flow

User message
-> Chat Gateway loads current snapshot only
-> classify turn: log_only | state_update_only | decision_needed | trend_needed | ambiguity_review

If log_only or state_update_only:
-> Memory Adapter on current message only
-> deterministic guard
-> persist structured event
-> update snapshot
-> optional micro-response

If decision_needed:
-> build narrow specialist briefs from snapshot
-> call only required specialists
-> deterministic validation
-> Health Director adjudication
-> final response

If trend_needed:
-> load latest weekly summary before any broader history
