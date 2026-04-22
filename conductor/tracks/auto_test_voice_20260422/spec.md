# Spec: Auto Test Tool - Voice Assistant Screen Recorder

## Overview

Automated testing tool for voice assistant QA. The system uses a **PC Agent**:
- **PC Agent**: Downloads and plays test audio through its speakers, and simultaneously records the connected Android phone's screen via ADB while the voice assistant responds.

A **Python FastAPI server** orchestrates the entire flow, stores test cases, receives recorded videos, and provides a web dashboard for playback and review.

## Core Components

1.  **FastAPI Server (The Orchestrator)**
    *   Manages WebSocket connections from PC Agents.
    *   Provides a REST API for test configuration and triggering.
    *   Serves the Web Dashboard UI.
    *   Stores and serves recorded video files.
2.  **PC Agent (The Client)**
    *   A Python script running on a PC connected to an Android phone via USB.
    *   Connects to the Server via WebSocket.
    *   Executes `adb shell screenrecord` to capture the phone's screen.
    *   Downloads and plays the stimulus audio using the PC's speakers.
    *   Uploads the recorded video back to the Server upon completion.
3.  **Web Dashboard (The Interface)**
    *   A single-page web application (HTML/JS/CSS).
    *   Displays connected PC Agents and their real-time statuses.
    *   Provides controls to start tests and view the recorded video gallery.

## Test Execution Flow

```
1. Server sends "start_recording" → Phone B
2. Phone B starts MediaProjection recording → replies "ready"
3. Server sends "play_audio" + audio_url → Phone A
4. Phone A downloads audio from URL → plays through speaker
5. Phone B's voice assistant hears and responds (captured on screen)
6. After 1 minute timeout → Server sends "stop_recording" → Phone B
7. Phone B stops recording → uploads video to Server via HTTP
8. Server stores video → available for playback on web dashboard
```

## Functional Requirements

### FR1: Server - Test Orchestration
- Store test cases: each test has an `audio_url` and metadata (name, description)
- Manage device pairs (Phone A ↔ Phone B)
- Execute test flow: recording → audio → timeout → stop → upload
- Fixed 1-minute recording duration per test

### FR2: Server - WebSocket Device Management
- Maintain WebSocket connections with all devices
- Each device registers with: `device_id`, `role` ("player" or "recorder")
- Server pairs devices and tracks their status (online/recording/playing/offline)
- Commands sent to devices:
  - To recorder: `{"action": "start_recording"}`, `{"action": "stop_recording"}`
  - To player: `{"action": "play_audio", "audio_url": "https://..."}`
- Device status updates received:
  - From recorder: `{"status": "recording_ready"}`, `{"status": "recording_stopped"}`, `{"status": "uploading"}`, `{"status": "upload_complete"}`
  - From player: `{"status": "playing"}`, `{"status": "play_complete"}`

### FR3: Server - Web Dashboard
- View connected devices with real-time status
- Manage device pairs (assign player + recorder)
- Create/manage test cases (name + audio URL)
- Run tests with one click
- View test results: video gallery with playback
- HTML5 video player for in-browser playback

### FR4: Server - Video Storage & API
- Accept video uploads via `POST /api/upload` (multipart)
- Store videos in `recordings/` directory
- Serve videos for browser playback
- Associate each video with: test_id, device_id, timestamp

### FR5: Android App - Recorder Role (Phone B)
- Connect to server via WebSocket
- Register as "recorder" device
- On "start_recording": trigger MediaProjection screen capture
- On "stop_recording": stop recording, save MP4 locally
- Auto-upload recorded video to server via HTTP POST
- Handle screen capture permission overlay
- WebSocket auto-reconnect on disconnect

### FR6: Android App - Player Role (Phone A)
- Connect to server via WebSocket
- Register as "player" device
- On "play_audio": download audio from URL, play through speaker at max volume
- Report play status (playing/complete) back to server
- WebSocket auto-reconnect on disconnect

## Non-Functional Requirements
- Video format: MP4 (H.264)
- Recording duration: Fixed 1 minute per test
- WebSocket reconnect: exponential backoff (1s, 2s, 4s, max 30s)
- Dashboard: desktop browser responsive design
- Single Android APK with role selection (player/recorder) on first launch

## Acceptance Criteria
1. Two Android phones connect to server, one as "player", one as "recorder"
2. Dashboard shows both devices online with correct roles
3. Creating a test case with an audio URL works
4. Running a test: recorder starts → ready → player plays audio → 1 min → stop → upload
5. Uploaded video appears in test results on dashboard
6. Video plays correctly in browser
7. Multiple test runs are stored and reviewable

## Out of Scope (v1)
- iOS support
- User authentication
- Cloud storage (local filesystem only)
- Video compression/transcoding on server
- Parallel test execution (one test at a time for v1)
- Audio recording on Phone B (screen capture only)
