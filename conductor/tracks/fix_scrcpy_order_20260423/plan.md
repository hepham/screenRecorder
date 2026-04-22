# Plan: Fix Execution Order — scrcpy Must Be Ready Before Audio Playback

## Phase 1: Implement scrcpy Readiness Detection

- [x] Task 1: Create `wait_for_scrcpy_ready()` async helper function
  - [x] Sub-task: Read scrcpy stderr in a non-blocking thread (`asyncio.to_thread`)
  - [x] Sub-task: Poll for "Recording started" pattern with 10s timeout
  - [x] Sub-task: Return `True` if ready, `False` if timeout

- [x] Task 2: Create `start_scrcpy_with_retry()` async function
  - [x] Sub-task: Launch scrcpy subprocess
  - [x] Sub-task: Call `wait_for_scrcpy_ready()`
  - [x] Sub-task: On timeout — kill process, cleanup partial file, retry (max 2 retries)
  - [x] Sub-task: Return `(process, success)` tuple after all attempts

- [x] Task 3: Refactor `run_test_logic()` to use new functions
  - [x] Sub-task: Replace inline scrcpy launch + 2s sleep with `start_scrcpy_with_retry()`
  - [x] Sub-task: Only call `play_audio()` after confirmed readiness
  - [x] Sub-task: Call `report_test_failure()` if all retries exhausted

- [x] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md)
