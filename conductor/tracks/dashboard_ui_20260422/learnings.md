# Track Learnings: dashboard_ui_20260422

Patterns, gotchas, and context discovered during implementation.

## Codebase Patterns (Inherited)

- **In-memory data structures are used for persistence currently (`test_suites_db`, `test_runs`, `pending_suites_queue`)**: To be migrated to a proper database system in a future track.
- **FastAPI Modular Routers**: FastAPI routers are modularized and included in `main.py` rather than maintaining one monolith file.
- **Stateless UI Progress Polling**: Polling `/api/runs` and mapping `suite_id` allows the dashboard to compute progress `(completed/total)` dynamically without server-side tracking logic.
- **Auto-polling Decentralization**: PC Agent auto-polling makes the system resilient. When a suite is retrieved, the Agent POSTs to the server to trigger `run_suite`, shifting state management safely back to the server.

---

<!-- Learnings from implementation will be appended below -->
