import subprocess
import json
import sys

epic_id = "recordScreen-rz8"

def run_bd(args):
    cmd = ["wsl", "bd"] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running bd: {result.stderr}", file=sys.stderr)
        return None
    try:
        lines = result.stdout.strip().split('\n')
        # Find the line that looks like valid JSON
        for line in reversed(lines):
            try:
                data = json.loads(line)
                if 'id' in data: return data['id']
            except: pass
        # If the whole stdout is JSON
        data = json.loads(result.stdout)
        return data.get('id')
    except Exception as e:
        print(f"Failed to parse json: {e}, output: {result.stdout}", file=sys.stderr)
        return None

phases = [
    {
        "name": "Phase 1: PC Agent Status Reporting",
        "tasks": [
            "Task 1: Update PC Agent to send status",
            "Task 2: Enhance Server WebSocket Manager",
            "Task 3: Create GET /api/agents endpoint",
            "Task: Conductor Verification Phase 1"
        ]
    },
    {
        "name": "Phase 2: Hybrid Test Suite Assignment",
        "tasks": [
            "Task 1: Modify assignment endpoint to accept agent_id",
            "Task 2: Implement Auto-assign logic",
            "Task 3: Handle state transitions and errors",
            "Task: Conductor Verification Phase 2"
        ]
    },
    {
        "name": "Phase 3: Dashboard UI & Agent Selection",
        "tasks": [
            "Task 1: Build PC Agent list UI",
            "Task 2: Update Run Test Suite UI modal",
            "Task 3: Integrate API with agent_id",
            "Task: Conductor Verification Phase 3"
        ]
    }
]

phase_ids = []
task_ids_dict = {}

for p_idx, p in enumerate(phases):
    p_id = run_bd(["create", p["name"], "--parent", epic_id, "--json"])
    phase_ids.append(p_id)
    print(f"Created phase {p_idx+1}: {p_id}")
    task_ids_dict[f"phase{p_idx+1}"] = p_id
    
    prev_task_id = None
    for t_idx, t in enumerate(p["tasks"]):
        t_id = run_bd(["create", t, "--parent", p_id, "--json"])
        task_ids_dict[f"phase{p_idx+1}_task{t_idx+1}"] = t_id
        print(f"  Created task {t_idx+1}: {t_id}")
        if prev_task_id:
            subprocess.run(["wsl", "bd", "dep", "add", t_id, prev_task_id])
        prev_task_id = t_id

# Phase dependencies (Sequential)
if len(phase_ids) >= 2:
    subprocess.run(["wsl", "bd", "dep", "add", phase_ids[1], phase_ids[0]])
if len(phase_ids) >= 3:
    subprocess.run(["wsl", "bd", "dep", "add", phase_ids[2], phase_ids[1]])

metadata = {
    "beads_epic": epic_id,
    "beads_tasks": task_ids_dict
}
print("METADATA:", json.dumps(metadata))
