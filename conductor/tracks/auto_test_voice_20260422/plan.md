# Implementation Plan: Auto Test Tool - Voice Assistant Screen Recorder

**Last Revised:** 2026-04-22 16:25 (PC Agent Architecture Refactor)

## Architecture Overview
- **Server:** FastAPI backend managing WebSocket connections, REST APIs, test orchestration, and video storage.
- **Client (PC Agent):** Python script running on a PC connected to an Android phone via USB. Handles audio playback and ADB screen recording.
- **Dashboard:** HTML/JS/CSS frontend for test management and result viewing.

---

## Phase 1: Server Core (FastAPI + WebSocket + REST API)

- [x] Task 1: Basic Server Setup
  - [x] Initialize FastAPI app structure (`models`, `routes`, `ws`, `engine`).
  - [x] Setup static file serving for dashboard and recordings.

- [x] Task 2: Data Models (Pydantic)
  - [x] Create `DeviceRole` (PC_AGENT) and `DeviceStatus` enums.
  - [x] Create `DeviceInfo`, `TestCase`, and `TestRunStatus` models.

- [x] Task 3: WebSocket Connection Manager
  - [x] Create `ConnectionManager` class.
  - [x] Track active connections and device status.
  - [x] Implement `/ws/agent/{agent_id}` endpoint.
  - [x] Broadcast device updates to dashboard.

- [x] Task 4: REST API & Test Cases
  - [x] CRUD endpoints for Test Cases (`/api/tests`).
  - [x] File upload endpoint (`POST /api/upload`) using `aiofiles`.

- [x] Task 5: Test Orchestration Engine
  - [x] Implement `execute_test_run` background task.
  - [x] Send `run_test` command to PC Agent via WebSocket.

- [x] Task: Conductor - User Manual Verification 'Server Core'

---

## Phase 2: Web Dashboard (HTML/JS/CSS)

- [x] Task 1: Dashboard Layout & Design
  - [x] Create `server/static/index.html` - Main dashboard page
  - [x] Create `server/static/style.css` - Styling (modern dark theme)
  - [x] Create `server/static/app.js` - Dashboard logic
  - [x] Layout sections: Device Panel, Test Cases Panel, Test Runner, Video Gallery

- [x] Task 2: Device Management UI
  - [x] Real-time PC Agent list with status indicators
  - [x] Connection status WebSocket integration

- [x] Task 3: Test Case Management UI
  - [x] Create test form (name, audio URL, description)
  - [x] Test case list with edit/delete actions

- [x] Task 4: Test Runner UI
  - [x] "Run Test" button per test case (selects available PC Agent)
  - [x] Real-time test execution progress

- [x] Task 5: Video Gallery & Player
  - [x] Grid/list view of all recorded videos
  - [x] HTML5 video player with controls

- [x] Task: Conductor - User Manual Verification 'Web Dashboard'

---

## Phase 3: PC Agent (Client)

- [x] Task 1: PC Agent Architecture
  - [x] Create `client/pc_agent.py`.
  - [x] Implement WebSocket connection to `/ws/agent/{agent_id}`.
  - [x] Handle connection lifecycle and auto-reconnect.

- [x] Task 2: Action Handlers
  - [x] Implement `run_test` logic.
  - [x] `subprocess.Popen` for `adb shell screenrecord`.
  - [x] Download audio using `requests` and play via system command.
  - [x] 60-second execution timer.

- [x] Task 3: File Management
  - [x] Stop `screenrecord` process.
  - [x] Pull video from device via `adb pull`.
  - [x] Upload video to server via `POST /api/upload`.
  - [x] Cleanup local and remote temporary files.

- [~] Task: Conductor - User Manual Verification 'PC Agent'

---

## Phase 4: Integration Testing & Finalization

- [ ] Task 1: End-to-End Test Run
  - [ ] Start server.
  - [ ] Connect Android phone via USB and start PC Agent.
  - [ ] Open Dashboard and verify agent connects.
  - [ ] Create test case and trigger run.
  - [ ] Verify audio plays, screen is recorded, and video appears in gallery.

- [ ] Task 2: Polish & Error Handling
  - [ ] Handle adb connection failures.
  - [ ] Add loading states and error toasts in UI.

- [ ] Task: Conductor - Completion Sign-off
