# Specialist Integration Workflow

## Rule 1: contract before implementation

Every specialist must have:
1. role definition
2. contract
3. compact system prompt
4. schema
5. deterministic validation path
6. brief-based intake path

## Health Director merge flow
1. Build narrow brief from snapshot
2. Send to specialist
3. Validate output using schema + deterministic rules
4. Inspect compact result:
   - status
   - risk_flags
   - fallback
   - confidence
5. Decide:
   - accept
   - modify
   - reject
   - regenerate with tighter constraints
6. Merge into unified plan

## Hard rules
- specialists do not receive open-ended memory blobs
- specialists do not receive raw chat by default
- specialist context should stay domain-bounded and compact
