# Track Learnings: fix_scrcpy_order_20260423

Patterns, gotchas, and context discovered during implementation.

## Codebase Patterns (Inherited)

- **In-memory data structures** for persistence (test_suites_db, test_runs, pending_suites_queue)
- **FastAPI Modular Routers**: Routers modularized in main.py
- **Auto-polling Decentralization**: PC Agent auto-polls queue, POSTs to server to trigger run_suite
- **asyncio.to_thread** used for blocking I/O (audio download/play)

---

<!-- Learnings from implementation will be appended below -->

## [2026-04-23] - Phase 1: Implement scrcpy Readiness Detection
- **Implemented:** Added `wait_for_scrcpy_ready` and `start_scrcpy_with_retry` to safely wait for scrcpy to be fully initialized ("Recording started") before triggering audio playback.
- **Files changed:** `client/pc_agent.py`
- **Learnings:**
  - Patterns: Reading from `subprocess.PIPE` stdout/stderr requires care. We use `asyncio.to_thread` with an `asyncio.wait_for` wrapper. If it times out, killing the subprocess gracefully closes the pipe and unblocks the orphaned thread, preventing resource leaks.
  - Gotchas: If the subprocess crashes early, `readline` might block or return empty strings; we handled it by checking `if not line: break`.
---
