# Weekly Summary Flow

End of week
-> gather seven-day event aggregates
-> load daily summaries for week
-> load metric trends
-> load latest snapshot transition history
-> request Progress Analyst if trend interpretation is needed
-> generate weekly summary
-> validate weekly summary
-> persist under health/weekly_summaries/

Rules:
- weekly summary is derived decision support
- keep facts, interpretation, and confidence notes separate
