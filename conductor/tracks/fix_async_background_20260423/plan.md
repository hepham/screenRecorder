# Plan: Fix asyncio.create_task in Background Thread

## Phase 1: Fix async background task invocation

- [x] Task 1: Replace lambda+asyncio.create_task with direct async function reference
  - File: `server/routes/api.py`
  - Line 69-71: `run_test` endpoint — change to `background_tasks.add_task(execute_test_run, run_status, agent, test.audio_url)`
  - Line 277-279: `run_suite` endpoint — change to `background_tasks.add_task(execute_suite_run, run_statuses, agent)`

- [x] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md)
