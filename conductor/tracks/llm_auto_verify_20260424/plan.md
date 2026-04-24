# Implementation Plan: LLM Auto Verification & Agent Loop

## Phase 1: Database & Model Foundation
<!-- execution: sequential -->

- [ ] Task 1: Migrate test_cases table — add new columns
  <!-- files: server/db.py -->
  - [ ] Add columns to `test_cases`: `expected_result TEXT`, `precondition_type TEXT DEFAULT 'none'`, `precondition_value TEXT`, `precondition_audio_url TEXT`, `precondition_wait_seconds INTEGER DEFAULT 5`
  - [ ] Add columns to `test_runs`: `verified_by TEXT`, `agent_actions TEXT` (JSON string for action history)
  - [ ] Update `init_db()` with ALTER TABLE IF NOT EXISTS pattern for backward compatibility

- [ ] Task 2: Update Pydantic models
  <!-- files: server/models/test_case.py, server/engine/runner.py -->
  - [ ] Update `TestCaseCreate` and `TestCase` models with new fields (expected_result, precondition_*)
  - [ ] Update `TestRunStatus` model with `verified_by` and `agent_actions` fields
  - [ ] Update `create_test()` SQL to persist new fields
  - [ ] Update `update_test_run_verification()` to include `verified_by`

- [ ] Task: Conductor - User Manual Verification 'Database & Model Foundation' (Protocol in workflow.md)

---

## Phase 2: PC Agent — ADB Interaction Layer
<!-- execution: sequential -->

- [ ] Task 1: Add ADB helper functions
  <!-- files: client/pc_agent.py -->
  - [ ] `adb_screencap() -> bytes` — captures screenshot via `adb shell screencap -p`, returns PNG bytes
  - [ ] `adb_tap(x, y)` — runs `adb shell input tap x y`
  - [ ] `adb_swipe(x1, y1, x2, y2, duration)` — runs `adb shell input swipe`
  - [ ] `adb_input_text(text)` — runs `adb shell input text`
  - [ ] `adb_keyevent(keycode)` — runs `adb shell input keyevent`
  - [ ] `adb_grant_permissions(package)` — grants common permissions to a package
  - [ ] All functions: async wrappers using `asyncio.to_thread()`

- [ ] Task 2: Add precondition execution
  <!-- files: client/pc_agent.py -->
  - [ ] Before scrcpy start, check test data for precondition_type
  - [ ] If `utterance`: download + play precondition audio → wait N seconds
  - [ ] If `adb`: run each line as `adb shell {command}` → wait N seconds
  - [ ] Report precondition status via WebSocket

- [ ] Task 3: Add new WebSocket action handlers
  <!-- files: client/pc_agent.py -->
  - [ ] Handle `action: "screencap"` → capture screenshot → upload to server → respond with path
  - [ ] Handle `action: "adb_action"` → execute tap/swipe/text/key based on params → respond with status
  - [ ] Handle `action: "play_followup_audio"` → download and play audio (for SPEAK action)
  - [ ] Upload screenshot via HTTP POST to `/api/upload-screenshot`

- [ ] Task: Conductor - User Manual Verification 'PC Agent ADB Layer' (Protocol in workflow.md)

---

## Phase 3: Server — Screenshot & Agent Loop API
<!-- execution: sequential -->
<!-- depends: phase2 -->

- [ ] Task 1: Screenshot upload endpoint
  <!-- files: server/routes/upload.py -->
  - [ ] Add `POST /api/upload-screenshot` — accepts screenshot image, saves to `recordings/screenshots/<test_run_id>/`
  - [ ] Returns screenshot URL/path

- [ ] Task 2: NVIDIA NIM API client
  <!-- files: server/engine/llm_client.py -->
  - [ ] Create async client for NVIDIA NIM API (`integrate.api.nvidia.com`)
  - [ ] `send_multimodal_request(image_bytes, prompt) -> dict` — sends image + text, returns parsed JSON
  - [ ] API key from `NVIDIA_API_KEY` environment variable
  - [ ] Configurable model via `LLM_MODEL` env var (default: multimodal model with vision)
  - [ ] Retry logic with exponential backoff (max 3 retries)
  - [ ] Timeout: 10 seconds per request

- [ ] Task 3: Agent Loop orchestrator
  <!-- files: server/engine/agent_loop.py -->
  - [ ] Create `AgentAction` dataclass: action type, params, reasoning, screen_state
  - [ ] Create `AgentLoopResult` dataclass: verdict, action_history, total_iterations, screenshots
  - [ ] Create `async run_agent_loop(test_run_id, agent_id, utterance, expected_result) -> AgentLoopResult`
    - [ ] Loop: send screencap command to PC Agent → receive screenshot → send to LLM → parse action → send action to PC Agent → repeat
    - [ ] Max iterations: 10, total timeout: 60 seconds
    - [ ] Break on action=DONE or max iterations reached
    - [ ] Record action history for each iteration
  - [ ] Build agent prompt with: utterance, expected_result, iteration count, previous actions, screenshot

- [ ] Task 4: Integrate agent loop into test execution flow
  <!-- files: server/engine/runner.py -->
  - [ ] After audio playback, if `NVIDIA_API_KEY` is set → start agent loop
  - [ ] Pass precondition data in WebSocket command to PC Agent
  - [ ] After agent loop completes → save verdict + action history to test_run
  - [ ] If no API key → fallback to current behavior (just record + manual verify)

- [ ] Task: Conductor - User Manual Verification 'Server Agent Loop API' (Protocol in workflow.md)

---

## Phase 4: Video Frame Extraction & OCR (Post-hoc)
<!-- execution: sequential -->
<!-- depends: phase1 -->

- [ ] Task 1: Install dependencies
  <!-- files: requirements.txt -->
  - [ ] Add `opencv-python-headless` for frame extraction
  - [ ] Add `easyocr` or `pytesseract` for OCR
  - [ ] Add `httpx` for async NVIDIA API calls
  - [ ] Add `Pillow` for image processing

- [ ] Task 2: Build frame extraction module
  <!-- files: server/engine/frame_extractor.py -->
  - [ ] Create `extract_key_frames(video_path, num_frames=8) -> List[Path]`
  - [ ] Evenly sample frames across video duration
  - [ ] Save frames as JPEG to `recordings/frames/<test_run_id>/`

- [ ] Task 3: Build OCR module
  <!-- files: server/engine/ocr_engine.py -->
  - [ ] Create `extract_text_from_frames(frame_paths) -> List[str]`
  - [ ] Support Vietnamese text recognition
  - [ ] Deduplicate repeated text across consecutive frames

- [ ] Task: Conductor - User Manual Verification 'Frame Extraction & OCR' (Protocol in workflow.md)

---

## Phase 5: Excel Import Update
<!-- execution: parallel -->
<!-- depends: phase1 -->

- [ ] Task 1: Update Excel parser
  <!-- files: server/routes/api.py -->
  - [ ] Support optional columns: `expected_result`/`kết quả mong đợi`, `precondition_type`/`loại điều kiện`, `precondition_value`/`điều kiện tiên quyết`, `precondition_audio`/`audio điều kiện`, `precondition_wait`/`thời gian chờ`
  - [ ] Map Vietnamese column names to English field names
  - [ ] Validate `precondition_type` values (none/utterance/adb)
  - [ ] Pass new fields through to `create_test()`

- [ ] Task: Conductor - User Manual Verification 'Excel Import Update' (Protocol in workflow.md)

---

## Phase 6: Permission Pre-Grant
<!-- execution: parallel -->
<!-- depends: phase2 -->

- [ ] Task 1: Permission grant API + PC Agent handler
  <!-- files: server/routes/api.py, client/pc_agent.py -->
  - [ ] Add `POST /api/agents/{agent_id}/grant-permissions` endpoint
  - [ ] Server sends WebSocket command to PC Agent with target package name
  - [ ] PC Agent runs `adb shell pm grant` for common permissions list:
    - READ_CONTACTS, SEND_SMS, CALL_PHONE, CAMERA, RECORD_AUDIO
    - READ_CALENDAR, WRITE_CALENDAR, ACCESS_FINE_LOCATION
  - [ ] Add "Grant Permissions" button on dashboard for each connected agent

- [ ] Task: Conductor - User Manual Verification 'Permission Pre-Grant' (Protocol in workflow.md)

---

## Phase 7: Verify Page UI & API Updates
<!-- execution: sequential -->
<!-- depends: phase3, phase4 -->

- [ ] Task 1: Update verify API
  <!-- files: server/routes/api.py -->
  - [ ] Add `POST /api/runs/{run_id}/ai-verify` — manually trigger LLM re-verification (frame extraction + OCR + LLM)
  - [ ] Update `PUT /api/runs/{run_id}/verify` to set `verified_by='human'`
  - [ ] Add `GET /api/runs/{run_id}/agent-history` — returns action history + screenshots
  - [ ] Include `verified_by`, `agent_actions` in TestRunStatus response

- [ ] Task 2: Update Verify Page — AI badge & reasoning
  <!-- files: server/static/verify.html, server/static/verify.js -->
  - [ ] Add "AI Verified ✨" or "Human Verified 👤" badge next to test case in sidebar
  - [ ] Display LLM reasoning in a collapsible section below validation controls
  - [ ] QA manual toggle overrides AI result → badge changes to "Human Verified"
  - [ ] Add "Re-run AI Verify" button

- [ ] Task 3: Agent Loop action history viewer
  <!-- files: server/static/verify.html, server/static/verify.js -->
  - [ ] Collapsible "Agent Actions" section showing iteration timeline
  - [ ] For each iteration: thumbnail screenshot + action taken + LLM reasoning
  - [ ] Visual timeline: step 1 → step 2 → ... → DONE
  - [ ] Click on screenshot thumbnail to view full size

- [ ] Task 4: Update sidebar status indicators
  <!-- files: server/static/verify.html, server/static/verify.js -->
  - [ ] New status colors: AI-verified (cyan dot), Human-verified (green dot), AI-failed (orange dot)
  - [ ] Show precondition info in detail view

- [ ] Task: Conductor - User Manual Verification 'Verify Page UI & API Updates' (Protocol in workflow.md)

---

## Phase 8: Integration Testing & Polish
<!-- execution: sequential -->
<!-- depends: phase5, phase6, phase7 -->

- [ ] Task 1: Agent loop E2E test
  - [ ] Test: Simple Bixby command (no interaction needed) → agent loop: screencap → DONE
  - [ ] Test: Command with permission dialog → agent loop taps "Allow"
  - [ ] Test: Command with option selection → agent loop selects correct option
  - [ ] Test: Command with confirmation → agent loop taps "Confirm"
  - [ ] Test: Max iterations reached → graceful timeout

- [ ] Task 2: Precondition E2E test
  - [ ] Test: Utterance precondition → audio plays first → test runs
  - [ ] Test: ADB precondition (single command) → command runs → test runs
  - [ ] Test: ADB precondition (multi-line) → all commands run sequentially

- [ ] Task 3: Error handling & fallback
  - [ ] Test: No NVIDIA_API_KEY → graceful skip (record only, manual verify)
  - [ ] Test: API timeout/error → retry logic works, eventual fallback
  - [ ] Test: PC Agent disconnects during agent loop → cleanup, mark test as failed
  - [ ] Test: LLM returns malformed JSON → fallback parsing
  - [ ] Test: ADB device disconnected → precondition fails gracefully

- [ ] Task 4: Excel import with new fields
  - [ ] Test: Import Excel with all new columns → data persisted correctly
  - [ ] Test: Import Excel WITHOUT new columns → backward compatible
  - [ ] Test: Invalid precondition_type → validation error

- [ ] Task: Conductor - User Manual Verification 'Integration Testing & Polish' (Protocol in workflow.md)
