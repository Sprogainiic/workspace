# Health System

Single-voice health orchestration system for OpenClaw.

## Current architecture

The system is now designed around a token-efficient context model:
- **Current State Snapshot** as the default runtime context
- **Structured Events** as the primary factual substrate
- **Daily Summaries** as compact day-level derived memory
- **Weekly Summaries** as compact trend-level derived memory
- **Specialist Briefs** instead of open-ended memory blobs
- **Deterministic-first validation** before any regeneration loop

## Core operating rules
- Chat Gateway is the live user-facing layer
- Health Director remains the sole decision authority
- Raw chat is retained for audit but not loaded by default
- Specialists are subordinate and brief-driven
- Health Director decides what becomes canonical memory
- Ambiguity is preserved explicitly when evidence is weak
- No specialist output reaches planning without validation

## Main workflows
- `workflows/lightweight-chat-turn-flow.md`
- `workflows/snapshot-update-flow.md`
- `workflows/daily-summary-flow.md`
- `workflows/weekly-summary-flow.md`
- `workflows/context-loading-policy.md`

## Runtime configuration
- `OPENCLAW_SESSIONS_INDEX` (optional): absolute path to `sessions.json` used by `runtime/session_history_client.py` when verifying delivery against session history.
- Outbound proactive transport supports `discord_direct` as the canonical direct-send channel name; `openclaw_session` remains supported as a compatibility alias.
