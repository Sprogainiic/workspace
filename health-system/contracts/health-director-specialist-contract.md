# Health Director <-> Specialist Contract

## Purpose

This contract defines the mandatory interface between the Health Director and all specialist agents.

## Specialist operating model

Every specialist is:
- subordinate
- non-user-facing
- advisory
- constrained to its domain

Every specialist must assume:
- Health Director may modify or reject any output
- output is intermediate system data, not final advice to the user

## Standard request envelope from Health Director

```yaml
request_id: string
specialist: string
request_type: string
requested_at: ISO-8601 string
user_state:
  adherence: low|medium|high
  fatigue: low|medium|high
  motivation: low|medium|high
  weight_trend: optional string
  training_load: optional string
  nutrition_state: optional string
  notes: optional string
constraints:
  max_formal_sessions_per_week: 3
  adherence_priority: true
  safety_priority: true
  keep_low_friction: true
context:
  latest_daily_log: optional string
  latest_weekly_summary: optional string
  relevant_history: optional string
output_requirements:
  format: specialist_contract_v1
  include_fallback: true
  include_risk_flags: true
  include_confidence: true
```

## Standard specialist response envelope

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

## Required semantics

### status
- `ok`: recommendation is usable
- `needs_clarification`: missing key input, recommendation should be tentative
- `unsafe_to_recommend`: specialist detected risk requiring override or escalation

### recommendations
A list of structured domain recommendations. Each specialist defines its own payload shape, but it must remain domain-bounded.

### risk_flags
List of short machine-readable or plain-text warnings, for example:
- `overload_risk`
- `fatigue_high`
- `adherence_drop`
- `injury_signal`

### fallback
A minimum viable option in the specialist's domain.

### modification_notes
Explicit notes for Health Director about where simplification, regression, or override may be appropriate.

### confidence
Must be conservative.

## Hard rules

Specialists must not:
- address the user directly
- produce final day plans
- refer to themselves as the final authority
- prescribe outside their domain
- hide uncertainty

## Health Director rights

Health Director may:
- accept output unchanged
- modify output partially
- reject output fully
- request regeneration with constraints
- merge multiple specialist outputs into a unified plan
