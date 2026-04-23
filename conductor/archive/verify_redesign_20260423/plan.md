# Implementation Plan: Verification Page Redesign

## Phase 1: Setup and Layout Structure
- [x] Task 1: Generate `ui-ux-pro-max` dark mode design system parameters.
- [x] Task 2: Create the full-screen master layout for the verification view.
- [x] Task 3: Implement the Left Sidebar for listing test cases (visible when viewing a suite).
- [x] Task 4: Conductor - User Manual Verification 'Setup and Layout Structure' (Protocol in workflow.md)

## Phase 2: Main Content Area Components
- [x] Task 1: Implement the Header to display the current Test Case name.
- [x] Task 2: Add the Video Player component for screen recordings.
- [x] Task 3: Add the Audio Player component beneath the video.
- [x] Task 4: Add the Utterance text display block.
- [x] Task 5: Implement the Capsule ID display as a hyperlinked component to navigate to details.
- [x] Task 6: Conductor - User Manual Verification 'Main Content Area Components' (Protocol in workflow.md)

## Phase 3: Validation Row & Auto-Save
- [x] Task 1: Build the Validation Row containing ASR, Capsule, Lng, and TTS Yes/No toggles inline.
- [x] Task 2: Implement the "Reason" input field at the very bottom of the view.
- [x] Task 3: Wire up JavaScript auto-save event listeners for toggles and reason input to send backend requests instantly.
- [x] Task 4: Conductor - User Manual Verification 'Validation Row & Auto-Save' (Protocol in workflow.md)
