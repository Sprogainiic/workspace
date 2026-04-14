# Daily Summary Flow

End of day or scheduled cutoff
-> gather structured events for day
-> gather snapshot transitions for day
-> gather final validated Health Director decisions for day
-> generate daily summary
-> validate daily summary
-> persist under health/daily_summaries/

Rules:
- derive from structured events first
- raw chat only by exception
- daily summary never overwrites structured events
