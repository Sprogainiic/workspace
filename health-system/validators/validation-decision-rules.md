# Validation Decision Rules

## Status mapping

### pass
- schema is valid
- contract is valid
- no priority conflict that requires regeneration
- safe_to_ingest = true

### warn
- schema is valid
- contract is valid
- one or more priority conflicts exist, but output can be modified safely by Health Director
- safe_to_ingest may still be true
- recommended_action should usually be `accept_with_modification`

### fail
- schema invalid
- contract violation present
- unsafe policy conflict
- missing fallback
- missing minimum version
- any hard failure rule triggered

## Recommended action mapping

- `accept` → pass with no meaningful concerns
- `accept_with_modification` → warn, but salvageable
- `regenerate` → contract mostly intact but needs corrected output
- `reject` → unsafe or badly malformed output

## Health Director ingestion rule

Health Director may ingest specialist output only if:
- `safe_to_ingest = true`
- validator status is `pass` or `warn`
- warning reasons are explicit and logged

If `fail`, Health Director must reject or request regeneration.
