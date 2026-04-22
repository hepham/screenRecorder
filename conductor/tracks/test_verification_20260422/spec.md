# Overview
This track introduces a Test Verification Page for reviewing recorded test sessions. Users will navigate to this page from a specific Test Suite on the main dashboard. It provides a split-view interface: a left sidebar listing all test cases in the suite, and a right main area displaying the video, audio, utterance, and validation controls for the selected test case.

# Functional Requirements
1. **Navigation & Entry:**
   - Provide a way (e.g., a "Verify" button) on the main dashboard for a Test Suite to open its Verification Page.
2. **Left Sidebar (Test Cases List):**
   - Display a list of all test cases belonging to the selected suite.
   - Visually indicate the status of each test case (e.g., Pending vs. Verified).
   - Selecting a test case updates the main verification area.
3. **Main Verification Area:**
   - Video player to review the screen recording.
   - Audio player for the test case's audio.
   - Display the expected utterance text.
4. **Validation Controls:**
   - Pass/Fail toggle buttons for different validation stages: `Pass LNG`, `Pass ASR`, `Pass Capsule`, `Pass TTS`.
   - A text input field for providing a `Reason` or notes.
5. **Auto-Save & State Management:**
   - Auto-save the verification inputs (Pass/Fail statuses, reason) to the backend when the user switches to a different test case in the sidebar.
   - After auto-saving, automatically update the test case's status to "Verified" and reflect this in the sidebar.

# Acceptance Criteria
- User can open the Verification Page from a Test Suite.
- Sidebar accurately lists all test cases with their verification status.
- Clicking a test case loads its video, audio, utterance, and existing validation data.
- User can toggle Pass/Fail for LNG, ASR, Capsule, TTS and enter a reason.
- Switching to another test case automatically saves the inputs of the previous one and marks it as "Verified".
- The backend API correctly handles updating the verification details.

# Out of Scope
- Global search for test cases across multiple suites.
- Bulk verification (validating multiple test cases at once without checking them individually).
