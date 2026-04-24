# Track Learnings: llm_auto_verify_20260424

Patterns, gotchas, and context discovered during implementation.

## Codebase Patterns (Inherited)

- **In-memory → SQLite migration**: DB uses `aiosqlite` with raw SQL. Schema changes via ALTER TABLE in `init_db()`.
- **FastAPI Modular Routers**: Routes in `server/routes/`, models in `server/models/`, engine logic in `server/engine/`.
- **PC Agent WebSocket protocol**: Commands sent as JSON `{"action": "run_test", ...}`. Agent responds with status updates.
- **Stateless UI Polling**: Frontend polls `/api/runs` to compute progress. WebSocket used for real-time push updates.
- **Test flow**: Server → WS command → PC Agent (scrcpy + audio) → upload video → complete_test_run → broadcast.

## Design Decisions

- **NVIDIA NIM API** chosen over local Ollama because server may not have GPU. NIM provides hosted multimodal inference.
- **Frame extraction + OCR** (dual approach) for post-hoc verification — visual context for UI state, text for specific values.
- **Precondition Cách 1+2**: Utterance preconditions reuse existing audio playback. ADB preconditions for reliable state setup.
- **LLM Agent Loop (Cách C)**: Core feature — LLM acts as interactive QA tester during test execution. Screenshot → analyze → decide action → execute via ADB → loop. Handles permission dialogs, option selection, confirmations, follow-up questions.
- **Permission Pre-Grant (Cách A)**: One-time ADB `pm grant` to eliminate permission dialogs. Combined with Agent Loop for remaining interactive scenarios.
- **Agent Loop architecture**: Server orchestrates loop (LLM calls), PC Agent executes ADB actions. Communication via existing WebSocket channel. Actions: TAP, SWIPE, TYPE, KEY, WAIT, SPEAK, DONE.
- **Action history**: Each iteration (screenshot + action + reasoning) saved as JSON in test_runs.agent_actions for QA review in Verify Page.

---

<!-- Learnings from implementation will be appended below -->
