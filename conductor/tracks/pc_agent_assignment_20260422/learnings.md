# Track Learnings: pc_agent_assignment_20260422

Patterns, gotchas, and context discovered during implementation.

## Codebase Patterns (Inherited)

- **In-memory data structures are used for persistence currently (`test_suites_db`, `test_runs`, `pending_suites_queue`)**: To be migrated to a proper database system in a future track.
- **FastAPI Modular Routers**: FastAPI routers are modularized and included in `main.py` rather than maintaining one monolith file.
- **Stateless UI Progress Polling**: Polling `/api/runs` and mapping `suite_id` allows the dashboard to compute progress `(completed/total)` dynamically without server-side tracking logic.
- **Auto-polling Decentralization**: PC Agent auto-polling makes the system resilient. When a suite is retrieved, the Agent POSTs to the server to trigger `run_suite`, shifting state management safely back to the server.

---

<!-- Learnings from implementation will be appended below -->
## [2026-04-22 13:12] - Phase 1: PC Agent Status Reporting & Server Tracking
- **Implemented:** Verified PC agent WebSocket connection status messages and added the \GET /api/agents\ endpoint to the server to list connected PC agents.
- **Files changed:** \server/routes/api.py- **Learnings:**
  - Context: PC Agent already reported \idle\ and \unning_test\ by default in \client/pc_agent.py\, so no modifications were needed on the client-side for this phase.
  - Context: Server \ConnectionManager\ handles agent connections and correctly models agents as \DeviceInfo\ using Pydantic, which made \GET /api/agents\ easy to return.
---
## [2026-04-22 13:15] - Phase 2: Hybrid Test Suite Assignment (Backend)
- **Implemented:** Updated create_suite_run and create_test_run in server/engine/runner.py to accept gent_id=" auto.
## [2026-04-22 13:15] - Phase 2: Hybrid Test Suite Assignment (Backend)
- **Implemented:** Updated create_suite_run and create_test_run in server/engine/runner.py to accept agent_id="auto". If "auto" is provided, the server scans manager.devices for a connected PC_AGENT that is currently IDLE.
- **Files changed:** server/engine/runner.py
- **Learnings:**
  - Pattern: Pushing the search logic down to create_test_run and create_suite_run means any API that initiates runs automatically gains the "auto" capability without further modification.
---
## [2026-04-22 13:18] - Phase 3: Dashboard UI & Agent Selection (Frontend)
- **Implemented:** Added a Target PC Agent dropdown to the dashboard. The dropdown dynamically populates with connected agents and defaults to "Auto-assign". Modified both \unTest\ and \unSuite\ functions to extract the target agent from this dropdown.
- **Files changed:** \server/static/index.html\, \server/static/app.js\`n- **Learnings:**
  - Context: Used the existing \enderDevices\ hook to keep the dropdown synced with the real-time WebSocket \device_update\ events.
---
