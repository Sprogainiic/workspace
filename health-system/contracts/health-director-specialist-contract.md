# Health Director <-> Specialist Contract

## Purpose

Define the compact interface between Health Director and specialists.

## Core runtime rule

Specialists are called with narrow briefs, not open-ended history.
Default specialist context comes from:
- current state snapshot
- latest relevant derived summary only if needed
- one task-specific brief

## Allowed brief types
- training_brief
- nutrition_brief
- behavior_brief
- meal_execution_brief

## Standard response envelope

```yaml
contract_version: specialist_contract_v1
specialist: string
request_id: string
status: ok|needs_clarification|unsafe_to_recommend
summary: short string
recommendations: []
risk_flags: []
fallback: optional object
modification_notes: []
confidence: low|medium|high
handoff_note: short string
```

## Hard rules
- specialist output is intermediate system data, not user-facing prose
- specialists stay domain-bounded
- validation is deterministic-first
- Health Director ingests validated payloads only
- raw specialist output must not bypass validation

## Context minimization rule
Do not include:
- full raw chat history
- broad daily log dumps
- unrelated domain memory

Include only the smallest safe context package required for the task.
