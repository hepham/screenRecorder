# Implementation Plan: UI Enhancements for Dashboard & Agent List

## Phase 1: Layout & Core CSS Structure
- [ ] Task: Update the main dashboard HTML template to define the new structural layout (Left column, Right column, Bottom section).
- [ ] Task: Apply CSS styling for the two-column layout and the bottom section container.
- [ ] Task: Conductor - User Manual Verification 'Layout & Core CSS Structure' (Protocol in workflow.md)

## Phase 2: Left Column (PC Agents List)
- [ ] Task: Implement the HTML structure for the agent list within the left column.
- [ ] Task: Integrate/update the WebSocket client logic to populate the agent list with real-time status (Online/Offline, Idle/Running).
- [ ] Task: Implement logic to display the current running Test Suite name and test progress ("Đang làm test thứ X") for active agents.
- [ ] Task: Conductor - User Manual Verification 'Left Column (PC Agents List)' (Protocol in workflow.md)

## Phase 3: Right Column (Test Creation & Excel Upload)
- [ ] Task: Implement the "Tạo testcase" button and the associated Modal popup structure and CSS.
- [ ] Task: Implement the Drag & Drop zone UI for Excel file uploads in the right column.
- [ ] Task: Add JavaScript logic to handle drag & drop events, file selection via click, and displaying the selected file name and upload status.
- [ ] Task: Conductor - User Manual Verification 'Right Column (Test Creation & Excel Upload)' (Protocol in workflow.md)

## Phase 4: Bottom Section (Test Results & Suites)
- [ ] Task: Implement the HTML structure for displaying the list of Test Suites and individual Test Cases.
- [ ] Task: Fetch data to populate the list and visually indicate the verification status of each item.
- [ ] Task: Add click event listeners to the list items to navigate the user to the Verification page.
- [ ] Task: Conductor - User Manual Verification 'Bottom Section (Test Results & Suites)' (Protocol in workflow.md)
