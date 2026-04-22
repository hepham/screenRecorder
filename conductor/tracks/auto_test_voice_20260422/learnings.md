# Track Learnings: auto_test_voice_20260422

Patterns, gotchas, and context discovered during implementation.

## Codebase Patterns (Inherited)

- Fresh project, no existing patterns yet.

---

<!-- Learnings from implementation will be appended below -->
## [2026-04-22 15:42] - Phase 1 Task 1: Project Setup & Dependencies
- **Implemented:** Initialized Python project, added requirements.txt, created project structure and recordings directory.
- **Files changed:** requirements.txt, server/main.py
- **Learnings:**
  - Patterns: Basic FastAPI project structure with models, routes, and ws directories.
---
## [2026-04-22 15:43] - Phase 1 Task 2: WebSocket Device Manager
- **Implemented:** Created Device Manager for WebSocket connections and device registry.
- **Files changed:** server/models/device.py, server/ws/device_manager.py, server/routes/ws.py, server/main.py
- **Learnings:**
  - Patterns: In-memory dictionary for device state mapping via WebSocket.
## [2026-04-22 15:44] - Phase 1 Task 4: Test Case Management API
- **Implemented:** Added REST endpoints for test case management.
- **Files changed:** server/models/test_case.py, server/routes/api.py, server/main.py
- **Learnings:**
  - Patterns: In-memory dictionary for test case DB.
---
## [2026-04-22 15:45] - Phase 1 Task 5: Test Execution Engine
- **Implemented:** Added Test Runner orchestrator that pairs devices, sends WebSocket commands, and manages timeouts.
- **Files changed:** server/engine/runner.py, server/routes/api.py
- **Learnings:**
  - Patterns: Background tasks in FastAPI to handle long-running WebSocket orchestration without blocking the HTTP response.
---
## [2026-04-22 15:47] - Phase 1 Task 6: Video Upload & Serving API
- **Implemented:** Added multipart upload endpoint for video and static file serving for recordings.
- **Files changed:** server/routes/upload.py, server/main.py
- **Learnings:**
  - Patterns: FastAPI StaticFiles for serving media files directly, aiofiles for async chunked writing of uploaded files.
---
## [2026-04-22 15:51] - Phase 2 Tasks 1-5: Web Dashboard
- **Implemented:** Created HTML/CSS/JS dashboard that connects to WebSocket for real-time device updates, uses REST API for tests and recordings, and plays MP4 videos.
- **Files changed:** server/static/index.html, server/static/style.css, server/static/app.js
- **Learnings:**
  - Patterns: Vanilla JS with WebSocket for a lightweight real-time dashboard without heavy frameworks.
---
## [2026-04-22 16:28] - Architecture Refactor: PC Agent
- **Implemented:** Converted from 2-phone architecture to 1-PC Agent architecture due to network policy constraints. PC Agent controls phone via ADB and plays audio directly.
- **Files changed:** server/models/device.py, server/ws/device_manager.py, server/routes/ws.py, server/engine/runner.py, server/routes/api.py, server/static/index.html, server/static/app.js, client/pc_agent.py, spec.md, plan.md
- **Learnings:**
  - Python subprocess + ADB provides a reliable local alternative to Android native MediaProjection when Wi-Fi is restricted.
---
