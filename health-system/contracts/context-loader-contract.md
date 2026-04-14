# Context Loader Contract

## Purpose

Load the smallest safe context bundle for each workflow.

## Retrieval ladder
1. snapshot only
2. snapshot + latest daily summary
3. snapshot + latest weekly summary
4. snapshot + filtered structured events
5. targeted raw chat excerpts

## Rules
- raw chat is exceptional, not default
- specialists receive narrow domain briefs, not open-ended history blobs
- Health Director receives snapshot first and escalates only when justified by task type or ambiguity
- validation receives payload + schema + deterministic rules; not full workflow prose
