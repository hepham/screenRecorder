import subprocess
import json

epic_id = "recordScreen-2dj"

phases = [
    {
        "key": "phase1",
        "name": "Phase 1: Layout & Core CSS Structure",
        "tasks": [
            "Update the main dashboard HTML template to define the new structural layout (Left column, Right column, Bottom section).",
            "Apply CSS styling for the two-column layout and the bottom section container.",
            "Conductor - User Manual Verification 'Layout & Core CSS Structure' (Protocol in workflow.md)"
        ]
    },
    {
        "key": "phase2",
        "name": "Phase 2: Left Column (PC Agents List)",
        "tasks": [
            "Implement the HTML structure for the agent list within the left column.",
            "Integrate/update the WebSocket client logic to populate the agent list with real-time status (Online/Offline, Idle/Running).",
            "Implement logic to display the current running Test Suite name and test progress (\"Đang làm test thứ X\") for active agents.",
            "Conductor - User Manual Verification 'Left Column (PC Agents List)' (Protocol in workflow.md)"
        ]
    },
    {
        "key": "phase3",
        "name": "Phase 3: Right Column (Test Creation & Excel Upload)",
        "tasks": [
            "Implement the \"Tạo testcase\" button and the associated Modal popup structure and CSS.",
            "Implement the Drag & Drop zone UI for Excel file uploads in the right column.",
            "Add JavaScript logic to handle drag & drop events, file selection via click, and displaying the selected file name and upload status.",
            "Conductor - User Manual Verification 'Right Column (Test Creation & Excel Upload)' (Protocol in workflow.md)"
        ]
    },
    {
        "key": "phase4",
        "name": "Phase 4: Bottom Section (Test Results & Suites)",
        "tasks": [
            "Implement the HTML structure for displaying the list of Test Suites and individual Test Cases.",
            "Fetch data to populate the list and visually indicate the verification status of each item.",
            "Add click event listeners to the list items to navigate the user to the Verification page.",
            "Conductor - User Manual Verification 'Bottom Section (Test Results & Suites)' (Protocol in workflow.md)"
        ]
    }
]

beads_tasks = {}
previous_phase_id = None

for i, phase in enumerate(phases):
    # create phase
    cmd = ["wsl", "bd", "create", phase["name"], "--parent", epic_id, "--json"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    try:
        data = json.loads(res.stdout.strip().split('\n')[-1])
        phase_id = data["id"]
        beads_tasks[phase["key"]] = phase_id
        print(f"Created {phase['key']}: {phase_id}")
    except Exception as e:
        print(f"Failed parsing: {res.stdout}")
        continue
    
    # dependencies between phases (sequential)
    if previous_phase_id:
        subprocess.run(["wsl", "bd", "dep", "add", phase_id, previous_phase_id])
    
    previous_task_id = None
    for j, task in enumerate(phase["tasks"]):
        t_cmd = ["wsl", "bd", "create", task, "--parent", phase_id, "--json"]
        t_res = subprocess.run(t_cmd, capture_output=True, text=True)
        try:
            t_data = json.loads(t_res.stdout.strip().split('\n')[-1])
            task_id = t_data["id"]
            beads_tasks[f"{phase['key']}_task{j+1}"] = task_id
            print(f"  Created task {j+1}: {task_id}")
            
            # task dependencies
            if previous_task_id:
                subprocess.run(["wsl", "bd", "dep", "add", task_id, previous_task_id])
            previous_task_id = task_id
            
        except Exception as e:
            print(f"Failed parsing task: {t_res.stdout}")
            
    previous_phase_id = phase_id

# Update metadata.json
with open("conductor/tracks/dashboard_ui_20260422/metadata.json", "r") as f:
    meta = json.load(f)

meta["beads_epic"] = epic_id
meta["beads_tasks"] = beads_tasks

with open("conductor/tracks/dashboard_ui_20260422/metadata.json", "w") as f:
    json.dump(meta, f, indent=2)

print("Done. Metadata updated.")
