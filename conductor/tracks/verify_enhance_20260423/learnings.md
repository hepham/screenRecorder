# Track Learnings: verify_enhance_20260423

Patterns, gotchas, and context discovered during implementation.

## Codebase Patterns (Inherited)

- **In-memory → SQLite Migration**: This track migrates `test_suites_db`, `test_cases_db`, `test_runs` dicts sang SQLite. Use `aiosqlite` for async compatibility with FastAPI.
- **FastAPI Modular Routers**: Keep routes in `server/routes/api.py`, DB logic in `server/db.py`, models in `server/models/`.
- **Stateless UI Progress Polling**: Dashboard polls `/api/runs` — after DB migration, ensure this endpoint still returns correctly from DB.
- **PC Agent Auto-polling**: Agent POSTs to trigger runs; stub result reporting added via `report_test_results()`.

---

<!-- Learnings from implementation will be appended below -->
## [2026-04-23 03:06] - Phase 1 Task 1: Cài aiosqlite dependency
- **Implemented:** Added aiosqlite to requirements.txt
- **Files changed:** requirements.txt
- **Commit:** 682569f
- **Learnings:**
  - Patterns: Dùng aiosqlite cho async SQLite database operations trong FastAPI.
## [2026-04-23 03:07] - Phase 1 Task 2: Tạo server/db.py
- **Implemented:** Created server/db.py with init_db to create all tables
- **Files changed:** server/db.py
- **Commit:** 230907b
- **Learnings:**
  - Patterns: Dùng aiosqlite.connect với file db lưu ở data/app.db, có function get_db dùng làm dependency injection.
## [2026-04-23 03:07] - Phase 1 Task 3: Hook init_db
- **Implemented:** Added lifespan in FastAPI to run init_db()
- **Files changed:** server/main.py
- **Commit:** 7a4b14d
## [2026-04-23 08:57] - Phase 2 Tasks 1-3: Migrate Models to DB
- **Implemented:** Migrated test_cases, test_suites, test_runs models to aiosqlite. Updated TestRunStatus with result_* fields. Made all usages async in api.py, upload.py, and ws.py.
- **Files changed:** server/models/test_case.py, server/models/test_suite.py, server/engine/runner.py, server/routes/api.py, server/routes/upload.py, server/routes/ws.py
- **Commit:** 0182e50
