# Health System Codebase Audit (A–Z)

Date: 2026-04-18 (UTC)
Scope: `health-system/` Python runtime and adjacent test signals

## Assumptions / Constraints
- The repository appears already extracted; no `.7z` archive file was present in workspace root scan.
- Findings are based on static code review plus selective test execution.

## 1) Codebase Structure

### Observed architecture
- Runtime is split into ingest (`reactive_session_ingest.py`), decisioning (`nudge_selector.py`), orchestration (`chat_flow.py`), delivery (`outbound_transport.py`), and persistence (`event_store.py`, `snapshot_updater.py`).
- This is a clean conceptual separation on paper, but implementation boundaries are violated by hard-coded heuristics and direct file I/O in many layers.

### Structural strengths
- Distinct modules for proactive vs reactive flows exist (`evaluate_nudge_slot` and `run_chat_turn`), with explicit logs (`nudge_log`, `delivery_audit`).
- Snapshot/event approach is coherent with the README architecture claims.

### Structural weaknesses
- Core runtime depends on missing modules (`runtime.validator`, `runtime.token_logger`, `runtime.error_log`) that are imported directly from production code.
- Test collection fails out-of-the-box unless path hacks are manually applied.
- No packaging/installation metadata (`pyproject.toml`/`setup.py`/requirements), despite tests assuming package import semantics.

## 2) Unused / Redundant Elements

- `QUIET_HOURS` constant in `nudge_selector.py` is unused; runtime uses policy-derived quiet hours instead.
- `_pick_nudge_type(..., today_events)` accepts `today_events` but never uses it.
- `daily_summary` argument is accepted by `select_nudge(...)` but not used in decision logic.
- In `outbound_transport.send_message`, arguments `metadata` and `session_sender` are accepted but effectively ignored for real transport path (`discord_direct` / `openclaw_session` both go through same adapter).
- Route mode values from `_route` (`specialist_single`, `director_merge`, `weekly_analysis`, `log_only`) are never dispatched in `run_chat_turn`; only `specialist_intake` has explicit branching.

## 3) Bugs & Risk Findings

### Critical
1. **Runtime import breakage in production modules**
   - `chat_flow.py`, `health_director_adapter.py`, `snapshot_updater.py`, and `reactive_session_ingest.py` import non-existent local modules.
   - This is not theoretical; tests explicitly monkeypatch these missing modules to make imports work.

2. **Package not importable by default test command**
   - `pytest -q` fails with 33 collection errors (`ModuleNotFoundError: No module named 'runtime'`).
   - This is a release/process blocker and indicates missing Python packaging contract.

3. **Reactive dedupe is race-prone and non-atomic**
   - `check_and_mark()` uses read-modify-write JSON file with no lock.
   - Concurrent bridge runners can accept same message, duplicating ingestion and state mutation.

### High
4. **Time-window policy is defined but bypassed in slot evaluation path**
   - `nudge_schedule.should_evaluate_slot(...)` exists but is never called by `execute_slot` or `select_nudge`.
   - Result: manual/cron misfire can send nudges outside intended slot windows.

5. **Timezone/date mismatch risk for “today events”**
   - `load_runtime_state()` compares `ts.date() == now.date()` without normalizing both into same business timezone.
   - Cross-timezone events around midnight can be attributed to wrong day.

6. **`nudge_skip_rules` can throw on common timestamp shapes**
   - `_parse_ts` uses bare `datetime.fromisoformat(value)` (no `Z` handling) and callers do not catch exceptions.
   - One bad timestamp in events/activity can crash skip-rule evaluation.

7. **Transport abstraction leaks / wrong behavior for session channel**
   - `openclaw_session` path still sends via `send_discord_direct`, ignoring session sender boundary.
   - This breaks expected distinction between direct message transport and session transport.

### Medium
8. **Business logic hard-coded and brittle in memory adapter**
   - Intent extraction relies on string containment lists with overlapping triggers and no precedence model.
   - Contradictory signals in one message can produce conflicting proposals (e.g., workout skipped + completed markers in one turn).

9. **Context loader overwrites context layers on unresolved states**
   - `unresolved` and `still_unresolved` replace `context_payload` entirely, discarding already loaded snapshot/summaries.
   - This can remove useful context unexpectedly and create unstable behavior.

10. **Potential command hang risk in Discord transport**
   - `subprocess.run(..., capture_output=True)` has no timeout; blocked CLI call stalls proactive pipeline.

### Low
11. **Hardcoded operational identifiers**
   - Discord recipient/channel IDs are hardcoded in `config.py` and `nudge_cron_bootstrap.py`, reducing deploy portability and increasing accidental misdelivery risk.

12. **Error taxonomy conflation**
   - Many skip/fail states are logged as `delivery_status=failed` even when it’s a policy skip, making operational metrics noisy.

## 4) Business Logic Review

### Mismatch vs likely intent
- README claims deterministic-first governance and specialist routing discipline, but active routing in `chat_flow.memory_adapter` is broad keyword matching with weak disambiguation.
- Intro intake path triggers on any mention of specialist names/phrases, potentially reclassifying normal user messages into intake flow.

### Fragile assumptions
- Assumes text content is always present and parseable for activity signals.
- Assumes all timestamps are ISO parseable and timezone-compatible.
- Assumes single-process writes to JSON/JSONL state files.

### Validation gaps
- Validation pipeline is structurally present but production validator module is absent.
- Event persistence accepts many medium-confidence updates without domain-level conflict checks.

## 5) Performance & Scalability

- Entire JSONL files are repeatedly loaded and scanned (`events`, `inbound`, `turn logs`) for each decision cycle; no indexing, no bounded reads.
- Dedupe file grows unbounded and is rewritten fully on each message.
- Session history parsing loads entire session file into memory then slices tail.
- This is acceptable for tiny local datasets but will degrade under sustained use.

## 6) Maintainability

- Readability is okay in isolation, but logic density in `chat_flow.py` is too high (routing, adapter, orchestration, transport, audit, failure handling in one module).
- Inconsistent error handling strategy (some parse paths guarded, some not).
- Test suite currently relies on environment tricks (`PYTHONPATH=.`, module stubs) rather than reproducible package setup.

## 7) Top 10 Critical Findings (Ranked)

1. **Critical** — Missing runtime modules imported in production paths.
2. **Critical** — Baseline `pytest -q` fails with package import errors.
3. **Critical** — Non-atomic dedupe storage causes duplicate ingest under concurrency.
4. **High** — Slot time-window policy defined but not enforced in execution path.
5. **High** — Day-boundary timezone mismatch in runtime state loader.
6. **High** — Unhandled timestamp parse failures in skip-rules path.
7. **High** — `openclaw_session` transport semantic mismatch (uses discord direct transport).
8. **Medium** — Hard-coded heuristic adapter creates contradictory/ambiguous business outcomes.
9. **Medium** — Context layering overwritten in unresolved branches, causing hidden context loss.
10. **Medium** — External CLI transport has no timeout/circuit-breaker.

## 8) Actionable Recommendations (What to fix first)

### Priority 0 (blockers, immediate)
1. **Restore runtime integrity**
   - Add/restore `runtime/validator.py`, `runtime/token_logger.py`, and `runtime/error_log.py` or remove imports and replace with explicit interfaces.
2. **Make package importable by default**
   - Add `pyproject.toml` + editable install path, or a `pytest.ini` that sets `pythonpath = .`.

### Priority 1 (correctness)
3. **Enforce slot window gate in live execution**
   - Call `should_evaluate_slot(slot, now)` in `execute_slot()` before `evaluate_nudge_slot`.
4. **Normalize all temporal comparisons to policy timezone**
   - Convert both event ts and `now` to same timezone before `.date()`/window comparisons.
5. **Harden timestamp parsing**
   - Centralize parse helper with `Z` support and exception-safe behavior; skip malformed records, never crash decision path.

### Priority 2 (business logic and architecture)
6. **Refactor `chat_flow.py` into smaller units**
   - Separate message classification, extraction, persistence orchestration, and proactive delivery.
7. **Replace hardcoded keyword logic with rule objects and conflict resolution**
   - Define deterministic precedence and contradiction handling (e.g., skip vs complete in same message).
8. **Fix transport abstraction**
   - `openclaw_session` should use session sender contract when available; direct Discord should remain a separate path.

### Priority 3 (scalability / ops)
9. **Move hot logs/state to append-only + indexed storage (SQLite at minimum)**
   - Dedup keys, recent activity queries, and nudge logs should be queryable without full file scans.
10. **Add timeout/retry/circuit-breaker around external transport command**
   - Prevent process hangs and provide bounded failure mode.

## Validation commands run
- `pytest -q` (fails collection due to import/package issues)
- `PYTHONPATH=. pytest -q tests/test_nudge_runtime.py tests/test_memory_adapter_fatigue_mapping.py tests/test_reactive_dedupe_guard.py` (passes)
- `python -m compileall -q runtime` (passes)
