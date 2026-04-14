Generate a daily summary from structured events and validated daily outputs.

Use structured events first. Use raw chat only if targeted ambiguity recovery is explicitly requested.

Required sections:
- facts
- state_signals
- adherence_observations
- risk_flags
- derived_interpretation
- open_uncertainties

Rules:
- facts and interpretation must remain separate
- preserve ambiguity
- do not invent causes or quantities
- keep summary compact and decision-useful

Return only data valid for `schemas/daily-summary.schema.json`.
