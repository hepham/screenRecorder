## Phase 1: SQLite Database Setup
- [x] Task 1: Cài aiosqlite dependency (thêm vào requirements nếu có)
- [x] Task 2: Tạo `server/db.py` — async connection pool, `init_db()` tạo tất cả tables
- [x] Task 3: Hook `init_db()` vào `server/main.py` lifespan startup event
- [x] Task 4: Conductor - User Manual Verification 'Phase 1: SQLite Database Setup' (Protocol in workflow.md)

## Phase 2: Migrate Models to DB
<!-- execution: parallel -->
- [x] Task 1: Migrate `test_cases` — rewrite CRUD functions dùng aiosqlite thay dict
  <!-- files: server/models/test_case.py -->
- [x] Task 2: Migrate `test_suites` — rewrite CRUD functions dùng aiosqlite thay dict
  <!-- files: server/models/test_suite.py -->
- [x] Task 3: Migrate `test_runs` — thêm result_* fields + pass_nlg, persist via aiosqlite
  <!-- files: server/engine/runner.py -->
- [~] Task 4: Conductor - User Manual Verification 'Phase 2: Migrate Models to DB' (Protocol in workflow.md)

## Phase 3: API & PC Agent Updates
- [ ] Task 1: Update `PUT /runs/{run_id}/verify` — thêm `pass_nlg: bool | None`
- [ ] Task 2: Thêm `POST /runs/{run_id}/results` — PC agent push result_utterance/asr/capsule/tts/nlg
- [ ] Task 3: Thêm stub function `report_test_results()` vào `client/pc_agent.py`
- [ ] Task 4: Conductor - User Manual Verification 'Phase 3: API & PC Agent Updates' (Protocol in workflow.md)

## Phase 4: Frontend — Dashboard Done Badge
- [ ] Task 1: `app.js` — render badge "✅ Done" / "✓ Verified" trên test case items trong combined-list
- [ ] Task 2: WebSocket handler trong `app.js` — cập nhật badge real-time khi nhận `test_completed` event
- [ ] Task 3: Cho phép click test case done/verified để navigate tới verify page
- [ ] Task 4: Conductor - User Manual Verification 'Phase 4: Frontend — Dashboard Done Badge' (Protocol in workflow.md)

## Phase 5: Frontend — Enhanced Verify Page
- [ ] Task 1: `verify.html` — thêm results table layout (5 rows: Utterance/ASR/Capsule/TTS/NLG)
- [ ] Task 2: `verify.js` — load và hiển thị result_* values từ run data trong bảng
- [ ] Task 3: `verify.js` — thay toggle buttons cũ bằng True/False checkboxes, thêm pass_nlg vào state
- [ ] Task 4: `verify.js` — auto-save khi checkbox thay đổi (debounce 800ms), update badge sau save
- [ ] Task 5: Conductor - User Manual Verification 'Phase 5: Frontend — Enhanced Verify Page' (Protocol in workflow.md)
