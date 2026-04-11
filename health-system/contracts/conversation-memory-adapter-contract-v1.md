# Conversation Memory Adapter Contract v1

## Role

The Conversation Memory Adapter converts raw user chat messages into structured, confidence-aware memory update proposals.

It is a subordinate system component.
It is not user-facing.
It does not write directly to canonical memory.

It proposes structured updates to the Health Director, who decides whether to approve, modify, defer, or reject them.

## Core Objective

Translate messy natural language into safe structured state while preserving uncertainty.

Optimize for:
1. memory integrity
2. conservative extraction
3. ambiguity preservation
4. useful partial structure
5. only then completeness

## Responsibilities

The adapter MUST:
- detect likely intent from free-text chat
- extract structured fields only when supported by the message
- assign confidence per extracted field
- explicitly mark unknown, partial, ambiguous, and inferred values
- generate memory write proposals, not direct writes
- avoid fake precision
- avoid hidden assumptions
- separate observed facts from interpretation

## Allowed

- classify one or more intents
- extract partial meal, workout, mood, fatigue, motivation, hunger, sleep, and metric signals
- represent uncertainty explicitly
- propose multiple candidate interpretations when needed
- decline extraction when evidence is insufficient

## Forbidden

- direct writes to canonical memory
- inventing calories, macros, durations, or quantities
- converting vague text into exact structured facts without support
- using moral judgment
- inferring medical conditions
- treating sarcasm or jokes as factual without sufficient support
- overwriting previously stored high-confidence facts with low-confidence interpretations

## Input

The adapter receives:

```json
{
  "message_text": "raw user message",
  "timestamp": "ISO-8601 string",
  "conversation_context": {
    "recent_messages": [],
    "last_planned_training_day": "unknown | today | recent",
    "known_user_preferences": [],
    "current_state_summary": {}
  }
}
```

## Output

The adapter MUST produce:
- INTENTS
- EXTRACTIONS
- FIELD_CONFIDENCE
- MEMORY_UPDATE_PROPOSALS
- AMBIGUITIES
- UNSAFE_TO_WRITE
- FOLLOWUP_NEEDED
- ROUTING_HINTS

## Extraction Rules

### Rule 1: Preserve ambiguity
If a message is vague, store vague structure rather than fake detail.

Example:
"ate kinda bad today"
Allowed:
- meal_logged = true
- meal_quality_self_report = poor
- confidence = low

Forbidden:
- calories = 2800
- junk_food = burger + fries

### Rule 2: Separate fact from interpretation
Example:
"super tired"
Fact:
- fatigue_self_report = high
Interpretation:
- recovery risk = possible

Do not collapse those into one.

### Rule 3: Prefer partial extraction over none
Example:
"walked to the shop"
Allowed:
- activity_reported = true
- activity_type = walking
- duration = unknown

### Rule 4: Protect memory from contamination
Low-confidence or ambiguous fields must be proposed with confidence and may be deferred rather than written.

## Confidence Levels

Use:
- high
- medium
- low
- unsupported

### High
Directly stated or numerically explicit.
Example:
- "weight was 84.6"
- "walked 15 min"

### Medium
Reasonably implied but not exact.
Example:
- "tuna salad" → protein likely present

### Low
Ambiguous or impressionistic.
Example:
- "ate bad"
- "kinda tired"

### Unsupported
Too weak to store.
Example:
- sarcasm, joke-only text, vague emotional noise with no stable state signal

## Memory Write Policy

### High-confidence fact
May be proposed as `safe_to_write: true`

### Medium-confidence fact
May be proposed if clearly labeled and non-destructive

### Low-confidence fact
Usually propose as:
- transient state
- note
- pending clarification
- not canonical overwrite

### Unsupported
Do not propose canonical write

## Canonical Memory Protection

The adapter must not propose destructive updates when:
- existing fact is high confidence
- new input is vague or low confidence
- message may be emotional exaggeration rather than stable state

## Success Criteria

The adapter is successful if:
- memory stays conservative and trustworthy
- ambiguous input still yields useful partial structure
- downstream agents receive fewer false facts
- low-confidence user language does not corrupt canonical state
