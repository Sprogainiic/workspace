Generate a weekly summary from daily summaries, event aggregates, metric trends, and validated analyst interpretation when available.

Required sections:
- week_facts
- trend_signals
- interpretation
- confidence_notes
- risk_flags
- next_week_implications

Rules:
- trend claims require evidence
- plateau claims require stable adherence and adequate duration
- do not prescribe plans
- preserve uncertainty explicitly

Return only data valid for `schemas/weekly-summary.schema.json`.
