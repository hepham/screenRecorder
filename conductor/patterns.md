# Architectural and Development Patterns

This document tracks reusable design, architectural, and development patterns discovered during track executions.

## 1. Backend Architecture
- **In-memory data structures are used for persistence currently (`test_suites_db`, `test_runs`, `pending_suites_queue`)**: To be migrated to a proper database system in a future track.
- **FastAPI Modular Routers**: FastAPI routers are modularized and included in `main.py` rather than maintaining one monolith file.

## 2. Frontend / Dashboard UI
- **Stateless UI Progress Polling**: Polling `/api/runs` and mapping `suite_id` allows the dashboard to compute progress `(completed/total)` dynamically without server-side tracking logic.

## 3. PC Agent
- **Auto-polling Decentralization**: PC Agent auto-polling makes the system resilient. When a suite is retrieved, the Agent POSTs to the server to trigger `run_suite`, shifting state management safely back to the server.
