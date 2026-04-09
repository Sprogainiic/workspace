# Health System

Single-voice health orchestration system for OpenClaw.

## Goal

Create a practical, adherence-first system where the **Health Director** is the only user-facing agent and all specialist agents operate through scratch outputs or delegated runs.

## Initial components

- `agents/health-director.md` — primary orchestrator definition
- `agents/fitness-coach.md` — first subordinate specialist
- `contracts/` — Health Director ↔ specialist interface definitions
- `schemas/` — structured output templates
- `health/` — canonical memory + inbox layout
- `workflows/` — daily/weekly and integration playbooks
- `prompts/` — task prompts for specialist agents

## Operating model

- Health Director is the sole user-facing voice
- Specialists are subordinate and contract-bound
- Specialists write to scratch inboxes or return structured data
- Health Director decides what becomes canonical memory
- Adherence and safety always outrank optimization
- No specialist is implemented without an explicit contract first
