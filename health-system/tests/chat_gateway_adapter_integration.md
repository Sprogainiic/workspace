# Chat Gateway + Memory Adapter Integration Tests

## Goal

Verify that messy chat becomes trustworthy structured memory proposals without corrupting canonical memory.

## Test categories

- clean inputs
- ambiguous inputs
- conflicting signals
- low motivation / emotional inputs
- decision requests
- multi-intent messages
- edge cases

## Minimum scenarios

Use at least these messages:
- ate tuna salad and some bread
- did 15 min walk, better than nothing I guess
- energy low today
- ate kinda bad today lol
- snacked a bit, nothing major
- had some sweets at work again
- breakfast was random, coffee and whatever was around
- maybe I'll train later
- didn't do the workout
- not doing intervals today, no chance
- walked to the shop and back, does that count
- super tired but also feel guilty for skipping
- legs feel heavy today
- slept like garbage
- headache, low energy, and hungry all day
- should I still train today or just forget it
- what should I eat tonight, can't be bothered to cook
- can I eat pizza or does that ruin everything
- what's the absolute minimum I can do today
- I don't feel like doing anything

## What to inspect

For each message:
- intents
- extractions
- confidence
- memory proposals
- unsafe-to-write fields
- routing hints
- whether Health Director approval is required
- whether low-confidence fields stay non-canonical

## Success criteria

- ambiguous inputs remain ambiguous
- no fake precision enters memory
- multi-intent messages are split properly
- no direct memory write bypass exists
- health director approval remains mandatory
