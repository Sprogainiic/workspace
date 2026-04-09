# Health System

Single-voice health orchestration system for OpenClaw.

## Goal

Create a practical, adherence-first system where the **Health Director** is the only user-facing agent and all specialist agents operate through scratch outputs or delegated runs.

## Initial components

- `agents/health-director.md` — primary orchestrator definition
- `schemas/` — structured output contracts
- `health/` — canonical memory + inbox layout
- `workflows/` — daily/weekly execution playbooks
- `prompts/` — task prompts for specialist agents

## Operating model

- Health Director is the sole user-facing voice
- Specialists write to scratch inboxes or return structured data
- Health Director decides what becomes canonical memory
- Adherence and safety always outrank optimization
