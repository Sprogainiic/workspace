# Specialist Contracts

These contracts define how subordinate specialist agents communicate with the Health Director.

## Goals

- prevent freelance agent behavior
- keep all specialists subordinate
- make outputs mergeable and auditable
- support modification / rejection by the Health Director
- reduce prompt ambiguity

## Contract rules

1. Specialists are not user-facing.
2. Specialists output structured recommendation objects, not final user plans.
3. Specialists must include risk flags, fallback logic, and confidence.
4. Health Director is the only authority allowed to approve, modify, or persist recommendations.
5. If a specialist is uncertain, it must say so in a machine-readable way instead of improvising.
