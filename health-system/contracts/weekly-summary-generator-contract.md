# Weekly Summary Generator Contract

## Role

Generate a weekly summary from structured events, daily summaries, and metric trends.

## Inputs
- seven-day structured event aggregates
- daily summaries in range
- metric trends
- latest snapshot transition history
- validated Progress Analyst output when available

## Output requirements
Must separate:
- WEEK_FACTS
- TREND_SIGNALS
- INTERPRETATION
- CONFIDENCE_NOTES
- RISK_FLAGS
- NEXT_WEEK_IMPLICATIONS

## Hard rules
- do not prescribe plans
- do not collapse noise into false certainty
- plateau claims require stable adherence and adequate duration
- weekly summary is derived and never overwrites event records
