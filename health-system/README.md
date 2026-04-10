# Health System

Single-voice health orchestration system for OpenClaw.

## Goal

Create a practical, adherence-first system where the **Health Director** is the only user-facing agent and all specialist agents operate through scratch outputs or delegated runs.

## Initial components

- `agents/health-director.md` — primary orchestrator definition
- `agents/fitness-coach.md` — first subordinate specialist
- `contracts/` — Health Director ↔ specialist interface definitions
- `schemas/` — structured output templates
- `validators/` — hard-gate validation rules
- `health/` — canonical memory + inbox layout
- `workflows/` — daily/weekly and integration playbooks
- `prompts/` — task prompts for specialist agents
- `prompts/chat-gateway-system-prompt.md` — single-chat orchestration layer
- `workflows/chat-gateway-flow.md` — top-level interaction routing
- `contracts/chat-gateway-contract.md` — interface boundary for user-facing chat
- `tests/chat-gateway-scenarios.md` — messy real-world input cases for the chat interface

## Operating model

- Chat Gateway is the live chat interface layer
- Health Director remains the sole decision authority and final planner
- Specialists are subordinate and contract-bound
- Specialists write to scratch inboxes or return structured data
- Health Director decides what becomes canonical memory
- Adherence and safety always outrank optimization
- No specialist is implemented without an explicit contract first
- No specialist output reaches Health Director without passing validation
- Chat Gateway never bypasses Health Director or validation
- Chat Gateway extraction should use confidence-aware structured memory updates when inputs are ambiguous
