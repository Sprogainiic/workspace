# Specialist Integration Workflow

## Rule 1: contract before implementation

Every specialist must have:
1. a role definition
2. a contract document
3. a system prompt aligned to that contract
4. a Health Director intake/merge path

## Health Director merge flow

1. Build request envelope
2. Send to specialist
3. Validate specialist response against contract
4. Inspect:
   - status
   - risk flags
   - fallback
   - confidence
5. Decide:
   - accept
   - modify
   - reject
   - regenerate with tighter constraints
6. Merge into unified daily plan
7. Persist only final canonical decision

## Validation checklist

Before accepting a specialist output, Health Director checks:
- Is the output domain-bounded?
- Does it include fallback?
- Does it include risk flags?
- Does it violate hierarchy or authority boundaries?
- Is it simple enough for low-adherence conditions?
