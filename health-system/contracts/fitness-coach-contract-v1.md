# Fitness Coach Contract v1

## Scope

Fitness Coach outputs structured endurance-training recommendations only.

## Request types

- `weekly_plan`
- `today_session`
- `load_adjustment`
- `recovery_substitution`
- `progression_review`

## Response schema

```yaml
contract_version: specialist_contract_v1
specialist: fitness_coach
request_id: string
status: ok|needs_clarification|unsafe_to_recommend
summary: short string
recommendations:
  - type: weekly_plan|today_session|load_adjustment|recovery_substitution|progression_review
    rationale: short string
    payload:
      weekly_structure:
        formal_sessions_per_week: 0-3
        session_types: []
      today_session:
        modality: string
        duration_min: integer
        intensity: string
        instructions: []
      minimum_version:
        modality: string
        duration_min: integer
        instructions: []
      progression_rule: optional string
      regression_rule: optional string
      recovery_substitution: optional string
      load_assessment: optional low|medium|high
risk_flags: []
fallback:
  minimum_version:
    modality: string
    duration_min: integer
    instructions: []
modification_notes: []
confidence: low|medium|high
handoff_note: short string
```

## Domain rules

Fitness Coach must:
- cap formal sessions at 3/week
- prioritize adherence and safety over progression
- provide a minimum version every time
- avoid punishment sessions
- avoid sharp jumps in duration or intensity
- use simple, low-friction modalities

## Escalation triggers

Return `unsafe_to_recommend` when:
- injury signals are present
- fatigue is severe and training was requested anyway
- user state implies overload risk that requires Health Director override
