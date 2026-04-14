# Context Loading Policy

## Default principle
Load the smallest safe context package.

## Retrieval ladder
1. snapshot only
2. snapshot + latest daily summary
3. snapshot + latest weekly summary
4. snapshot + filtered structured events
5. targeted raw chat excerpts

## By workflow
- simple logging: snapshot only
- state update + micro-response: snapshot only
- daily plan question: snapshot + latest daily summary
- trend / plateau question: snapshot + latest weekly summary
- contradiction / ambiguity review: snapshot + filtered events, then targeted raw excerpts if still needed

## Specialist loading
Specialists never receive open-ended history blobs.
They receive only narrow domain briefs.
