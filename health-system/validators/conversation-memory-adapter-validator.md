# Conversation Memory Adapter Validator

## Purpose

Validate that memory extraction is conservative, confidence-aware, and safe for downstream use.

## Status Levels

- PASS
- WARN
- FAIL

## FAIL Conditions

Reject output if any of the following occur:
- missing required sections
- extracted fields are not reflected in FIELD_CONFIDENCE
- proposes canonical writes for unsupported fields
- invents calories, macros, or quantities not explicitly stated
- converts vague meal reports into exact nutrition facts
- converts incidental movement into confirmed formal workout without support
- writes low-confidence fields as hard canonical updates without justification
- overwrites stronger facts with weaker ambiguous input
- no ambiguity recorded when message is clearly ambiguous
- ROUTING_HINTS omit obvious specialist involvement for multi-intent cases
- FOLLOWUP_NEEDED is "no" despite critical unresolved ambiguity affecting write safety

## WARN Conditions
- extraction is too sparse despite clear supported content
- too many fields marked medium when low would be safer
- too many low-confidence fields proposed for write
- rationale is weak or generic
- ambiguity preserved, but routing is broader than necessary
- transient state used where canonical append may be safe

## Contract Violations
- direct memory write language instead of proposal language
- hidden assumptions presented as facts
- emotional language treated as durable state without caution
- medical or diagnostic interpretation from casual user wording

## Validation Checks

### Structural
- schema validity
- confidence map present for extracted fields
- proposal objects valid

### Epistemic
- are facts supported by wording?
- is uncertainty preserved?
- is confidence level proportional to evidence?

### Memory Safety
- are writes conservative?
- are ambiguous or unstable claims kept out of canonical memory unless justified?
- are destructive overwrites avoided?

## Output

```text
status: pass | warn | fail
schema_errors: []
contract_violations: []
priority_conflicts: []
memory_safety_risks: []
safe_to_ingest: true | false
recommended_action:
 - accept
 - accept_with_modification
 - regenerate
 - reject
```