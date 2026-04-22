# Spec: Fix Execution Order — scrcpy Must Be Ready Before Audio Playback

## Overview
The current `run_test_logic` in `pc_agent.py` starts audio playback immediately after a 2-second sleep following scrcpy launch. This 2-second check only verifies the process is alive — not that scrcpy is actually capturing frames. As a result, audio may play before scrcpy is recording, causing the beginning of the test to be missing from the video evidence.

## Bug Description
In `client/pc_agent.py`, function `run_test_logic()`:
1. scrcpy is launched via `subprocess.Popen` (line 109-118)
2. After a 2s `asyncio.sleep`, only `poll()` is checked (process alive check)
3. `play_audio()` fires immediately via `asyncio.create_task` (line 131)

**Problem**: scrcpy may need 3-8 seconds to connect to the device and begin actual recording. Audio plays before capture is ready.

## Functional Requirements
1. **Poll scrcpy stderr** for a "recording started" indicator (e.g., `"Recording started"` or `"INFO: Recording"`) before playing audio.
2. **Timeout**: 10 seconds per attempt to detect the ready signal.
3. **Retry**: If scrcpy fails to become ready within timeout, kill the process and retry. Max 2 retries (3 total attempts).
4. **Fail gracefully**: After all retries exhausted, call `report_test_failure()` with a descriptive reason.
5. **Only play audio after confirmed scrcpy readiness**.

## Non-Functional Requirements
- stderr reading must be non-blocking (use `asyncio.to_thread` or async readline) to avoid blocking the event loop.
- Retry logic must properly clean up (kill process, remove partial files) between attempts.

## Acceptance Criteria
- [ ] Audio never plays before scrcpy outputs its recording-ready indicator
- [ ] If scrcpy fails 3 times, test is marked as failed with clear reason
- [ ] Existing test flow (recording duration, upload, cleanup) is unaffected
- [ ] No event loop blocking during stderr polling

## Out of Scope
- Changing scrcpy recording parameters
- Server-side changes (this is purely a client-side fix)
- Changing the audio playback mechanism
