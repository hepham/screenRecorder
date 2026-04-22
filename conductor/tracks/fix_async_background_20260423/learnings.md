# Track Learnings: fix_async_background_20260423

Patterns, gotchas, and context discovered during implementation.

## Codebase Patterns (Inherited)

- FastAPI `BackgroundTasks.add_task()` natively supports async coroutines — no need for `asyncio.create_task()` wrapper
- Starlette runs sync background tasks via `run_in_threadpool`, which has no event loop — `asyncio.create_task()` will always fail there

---

<!-- Learnings from implementation will be appended below -->

## Key Discovery
- The lambda wrapping pattern `lambda: asyncio.create_task(coro)` is a common antipattern when using FastAPI background tasks
- Correct pattern: `background_tasks.add_task(async_func, arg1, arg2)` — FastAPI detects it's async and runs it on the event loop
