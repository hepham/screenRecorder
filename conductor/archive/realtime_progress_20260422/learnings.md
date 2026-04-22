# Track Learnings: realtime_progress_20260422

Patterns, gotchas, and context discovered during implementation.

## Codebase Patterns (Inherited)

- **In-memory data structures are used for persistence currently (`test_suites_db`, `test_runs`, `pending_suites_queue`)**: To be migrated to a proper database system in a future track.
- **FastAPI Modular Routers**: FastAPI routers are modularized and included in `main.py` rather than maintaining one monolith file.
- **Stateless UI Progress Polling**: Polling `/api/runs` and mapping `suite_id` allows the dashboard to compute progress `(completed/total)` dynamically without server-side tracking logic. *(Note: This track will replace or augment this with WebSocket events)*.

---

<!-- Learnings from implementation will be appended below -->

## 2026-04-22 18:36 - Phase 1: WebSocket Backend Foundation
- **Implemented:** Added `broadcast_to_web` to `device_manager.py`. Leveraged existing `/ws/dashboard` endpoint which already serves as the web client manager.
- **Files changed:** `server/ws/device_manager.py`
- **Commit:** N/A (will be committed together)
- **Learnings:**
  - Context: The dashboard connection management was already implemented and mapped correctly to `/ws/dashboard`, storing connections in `dashboard_connections`. We just needed a specialized broadcast method.
---

## 2026-04-22 18:37 - Phase 2: Status Publishing
- **Implemented:** Fired `suite_started` from `server/engine/runner.py`. Added `test_run_completed` and calculated `suite_completed` logic in `server/routes/upload.py`.
- **Files changed:** `server/engine/runner.py`, `server/routes/upload.py`
- **Commit:** N/A
- **Learnings:**
  - Context: The suite progress can be naturally derived on the frontend by counting `test_run_completed` events, but the server checking `completed == total` provides a clean `suite_completed` signal.
---

## 2026-04-22 18:38 - Phase 3: Frontend Integration
- **Implemented:** Updated `ws.onmessage` in `app.js` to handle `suite_started`, `test_run_completed`, and `suite_completed` events. Triggered immediate re-fetches for DOM updates instead of waiting for the 2s polling interval.
- **Files changed:** `server/static/app.js`
- **Commit:** N/A
- **Learnings:**
  - Context: By triggering `fetchRuns()` and `fetchRecordings()` on WebSocket events, we reuse the robust DOM generation logic while still achieving immediate visual updates, avoiding duplicate DOM manipulation code.
---
