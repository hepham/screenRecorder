# Spec: Fix asyncio.create_task in Background Thread

## Overview
The `/tests/{test_id}/run` and `/suites/{suite_id}/run` endpoints crash with `Exception in ASGI application` because `asyncio.create_task()` is called inside a lambda passed to `BackgroundTasks.add_task()`. Starlette runs background tasks in a thread pool via `run_in_threadpool`, where there is no active asyncio event loop — causing `RuntimeError`.

## Root Cause
```python
# BROKEN: lambda runs in a thread pool — no event loop available
background_tasks.add_task(
    lambda: asyncio.create_task(execute_test_run(run_status, agent, test.audio_url))
)
```

## Functional Requirements
1. Both endpoints must execute test/suite runs asynchronously in the background without blocking the HTTP response.
2. Use FastAPI's native async background task support — `add_task()` accepts async coroutines directly.

## Fix
```python
# CORRECT: FastAPI handles async tasks natively
background_tasks.add_task(execute_test_run, run_status, agent, test.audio_url)
```

## Acceptance Criteria
- [ ] `POST /tests/{test_id}/run` returns 200 and test executes in background
- [ ] `POST /suites/{suite_id}/run` returns 200 and suite executes in background
- [ ] No `Exception in ASGI application` traceback in server logs

## Out of Scope
- Changes to runner logic, WebSocket handling, or agent management
