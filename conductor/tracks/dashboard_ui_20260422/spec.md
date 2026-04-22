# Specification: UI Enhancements for Dashboard & Agent List

## Overview
This track focuses on enhancing the main dashboard UI to provide better visibility of PC agents and simplify test creation. The layout will be updated with a left column for PC agents and a right column for test creation actions. The bottom section will display a comprehensive list of Test Suites and individual Test Cases, complete with their verification statuses.

## Functional Requirements
1. **Left Column (PC Agents List):**
   - Display a list of connected PC agents.
   - Show current status of each agent (Online/Offline, Idle/Running).
   - If an agent is running a test, display the current Test Suite name and progress (e.g., "Đang làm test thứ X").

2. **Right Column (Test Creation):**
   - Provide a "Tạo testcase" button that opens a Modal popup on the current page to create a new test case.
   - Include a drag-and-drop zone to upload an Excel file for generating a Test Suite.
   - The Excel upload zone must also support clicking to browse files.
   - Display the name of the selected Excel file and its upload status (Success/Error).

3. **Bottom Section (Test Results & Suites):**
   - Display a list containing both Test Suites and individual Test Cases.
   - Show the verification status ("verified" or not) for each item.
   - When a user clicks on a Test Suite or Test Case, navigate the user to the dedicated verification page.

## Non-Functional Requirements
- UI updates for the agent list should be reflected in real-time (via existing WebSockets) without requiring a page refresh.
- The drag-and-drop zone should have clear visual feedback when a file is dragged over it.

## Acceptance Criteria
- [ ] PC agent list on the left accurately displays agent status and current test progress.
- [ ] Clicking "Tạo testcase" opens a modal on the same page.
- [ ] Users can drag-and-drop or browse to upload an Excel file, and see the file name and status.
- [ ] The bottom list correctly shows both Test Suites and Test Cases with their verification statuses.
- [ ] Clicking an item in the bottom list successfully navigates to the verify page.

## Out of Scope
- Backend logic changes for executing tests (this track focuses on UI and utilizing existing backend data).
- Changes to the Verification page itself (only navigation to it is in scope).
