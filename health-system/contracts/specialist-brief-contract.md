# Specialist Brief Contract

## Purpose

Replace broad context blobs with narrow domain briefs.

## Allowed brief types
- training_brief
- nutrition_brief
- behavior_brief
- meal_execution_brief

## Rules
- each brief must be built from snapshot plus only the smallest additional derived context needed
- briefs must exclude irrelevant domains
- briefs may include compact recent pattern strings but not raw chat history by default
- briefs are inputs to specialists; they are not long-term memory artifacts
