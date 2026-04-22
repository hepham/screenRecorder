# Implementation Plan: Test Suite Assignment & User Tracking

## Phase 1: Backend Data Models & API

- [ ] Task 1: Update Data Models
  - Add `TestSuite` model (contains list of `test_case_ids`).
  - Update `TestRunStatus` to support Suite runs and add `executed_by` (User/Agent ID) and `suite_id`.
  - Add queue state to track pending test suites waiting for agents.
- [ ] Task 2: Create Test Suite APIs
  - CRUD endpoints for `TestSuite` in `api.py`.
  - Endpoint to fetch pending test suites for auto-polling `GET /api/agent/queue`.
- [ ] Task 3: Update Execution Engine
  - Modify `runner.py` to handle a suite of tests sequentially.
  - Support receiving auto-polling assignments.
- [ ] Task: Conductor - User Manual Verification 'Backend Data Models & API' (Protocol in workflow.md)

## Phase 2: Web Dashboard UI

- [ ] Task 1: Test Suite Management
  - UI to create/view/delete Test Suites (grouping Test Cases).
- [ ] Task 2: Execution Controls
  - Add "Executed By" text input field.
  - Modify "Run" button to execute an entire Suite and assign it to a specific PC Agent or send to queue.
- [ ] Task 3: Progress & History
  - Display suite execution progress (e.g., 1/3 completed).
  - Show the name/ID of the executor in the UI and history logs.
- [ ] Task: Conductor - User Manual Verification 'Web Dashboard UI' (Protocol in workflow.md)

## Phase 3: PC Agent Updates

- [ ] Task 1: Auto-Polling Mechanism
  - Update `pc_agent.py` to optionally poll Server for pending Test Suites.
- [ ] Task 2: Suite Execution
  - Update agent logic to handle running multiple audio/video recordings in sequence if a suite is assigned.
- [ ] Task: Conductor - User Manual Verification 'PC Agent Updates' (Protocol in workflow.md)
