# Specification: Verification Page Redesign

## 1. Overview
Redesign the Verification Page to use a highly professional, full-screen "Dark Mode" layout (utilizing the `ui-ux-pro-max` design system). The page allows users to review test cases (both individually and within test suites), play back recorded media, and validate the test execution results with seamless auto-saving.

## 2. Functional Requirements
* **Test Suite Sidebar:** If reviewing a test suite, a left sidebar will display a sequential list of all test cases in that suite for easy navigation.
* **Full-Screen Layout:** The interface will utilize the full browser window to maximize the viewing area for media and data.
* **Test Case Details View:** 
  * **Header:** Displays the Test Case Name.
  * **Media Players:**
    * A video player for the screen recording.
    * An audio player placed directly beneath the video.
  * **Utterance:** Displays the text of the utterance associated with the test case.
  * **Validation Row:** A single horizontal row containing Yes/No toggle inputs for:
    * ASR
    * Capsule
    * Language (lng)
    * TTS
  * **Capsule Navigation:** A specific section/link showing detail info for the Capsule ID, which navigates the user to a separate capsule details page when clicked.
  * **Reason Input:** A text input field at the bottom for the user to provide a reason for their validation choices.
* **Auto-Save Mechanism:** Any changes made to the Validation Yes/No toggles or the Reason input field are automatically saved to the backend without requiring an explicit "Submit" button click.

## 3. Non-Functional Requirements
* **Aesthetics:** Adhere to `ui-ux-pro-max` Dark Mode guidelines (sleek, accessible contrast ratios, reducing eye strain for media playback).
* **Responsiveness:** The layout should dynamically adjust the media players and validation row to fit neatly within the single full-screen view.

## 4. Acceptance Criteria
* [ ] The page occupies the full screen width and height.
* [ ] The left sidebar appears and correctly lists test cases when a suite is loaded.
* [ ] The main area correctly stacks Header > Video > Audio > Utterance.
* [ ] ASR, Capsule, Lng, and TTS Yes/No options are arranged in a single horizontal row.
* [ ] Capsule ID acts as a link to navigate away to the details page.
* [ ] Changing any Yes/No option or typing in the Reason field triggers a successful auto-save API request.
* [ ] The UI follows a cohesive Dark Mode theme.

## 5. Out of Scope
* Modifying the backend endpoints for saving validation (assuming existing endpoints can handle the auto-save requests).
* Building the destination page for the Capsule ID detail link.
