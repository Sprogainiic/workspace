# Daily Summary Generator Contract

## Role

Generate a compact daily summary from structured events, snapshot transitions, and validated daily decisions.

## Inputs
- structured events for one calendar day
- snapshot updates for that day
- final validated Health Director plan for that day when available
- unresolved ambiguities for that day

## Output requirements
Must separate:
- FACTS
- STATE_SIGNALS
- ADHERENCE_OBSERVATIONS
- DERIVED_INTERPRETATION
- OPEN_UNCERTAINTIES
- RISK_FLAGS

## Hard rules
- generate from structured events first, not raw chat dumps
- do not invent numbers or hidden causes
- do not overwrite structured event precision
- preserve unresolved uncertainty explicitly
