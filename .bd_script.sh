#!/bin/bash
epic_json=$(bd create "ui_run_controls_20260423: Bổ sung tính năng Target PC Agent và nút Run tại từng Test Suite/Case, điều chỉnh lại bố cục UI." \
  -t epic -p 0 \
  --design "Cập nhật lại bố cục UI của Dashboard để cân bằng hiển thị giữa danh sách Agent và chức năng Tạo Test. Bổ sung các nút điều khiển thực thi ngay trên từng dòng Test Suite/Test Case." \
  --acceptance "Giao diện hai phần bằng nhau. Execute by trên cùng. Dropdown chọn Agent và nút Run trên từng dòng. Chạy được auto và manual." \
  --assignee conductor \
  --json)

epic_id=$(echo "$epic_json" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)
echo "Epic ID: $epic_id"

if [ -z "$epic_id" ]; then
    echo "Failed to create epic"
    exit 1
fi

# Phase 1
phase1_json=$(bd create "Phase 1: Layout Reorganization" --parent $epic_id --json)
phase1_id=$(echo "$phase1_json" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)
echo "Phase 1 ID: $phase1_id"

task1_1_json=$(bd create "Task 1: Di chuyển cụm Execute by lên vị trí trên cùng của giao diện." --parent $phase1_id --json)
task1_2_json=$(bd create "Task 2: Điều chỉnh CSS/Grid để khu vực Connected PC Agent và Test Creation có chiều rộng bằng nhau." --parent $phase1_id --json)
task1_3_json=$(bd create "Task: Conductor - User Manual Verification 'Layout Reorganization'" --parent $phase1_id --json)

task1_1_id=$(echo "$task1_1_json" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)
task1_2_id=$(echo "$task1_2_json" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)
task1_3_id=$(echo "$task1_3_json" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)

bd dep add $task1_2_id $task1_1_id
bd dep add $task1_3_id $task1_2_id

# Phase 2
phase2_json=$(bd create "Phase 2: Target Agent Selector and Run Button" --parent $epic_id --json)
phase2_id=$(echo "$phase2_json" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)
echo "Phase 2 ID: $phase2_id"

task2_1_json=$(bd create "Task 1: Cập nhật giao diện bảng Test Suites & Test Cases, thêm cột Target PC Agent và nút Run." --parent $phase2_id --json)
task2_2_json=$(bd create "Task 2: Đổ dữ liệu các PC Agent vào dropdown Target PC Agent, mặc định là Auto." --parent $phase2_id --json)
task2_3_json=$(bd create "Task 3: CSS nút Run, thêm Loading/Disabled." --parent $phase2_id --json)
task2_4_json=$(bd create "Task: Conductor - User Manual Verification 'Target Agent Selector and Run Button'" --parent $phase2_id --json)

task2_1_id=$(echo "$task2_1_json" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)
task2_2_id=$(echo "$task2_2_json" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)
task2_3_id=$(echo "$task2_3_json" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)
task2_4_id=$(echo "$task2_4_json" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)

bd dep add $task2_2_id $task2_1_id
bd dep add $task2_3_id $task2_2_id
bd dep add $task2_4_id $task2_3_id
bd dep add $phase2_id $phase1_id

# Phase 3
phase3_json=$(bd create "Phase 3: Run Execution Logic Integration" --parent $epic_id --json)
phase3_id=$(echo "$phase3_json" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)
echo "Phase 3 ID: $phase3_id"

task3_1_json=$(bd create "Task 1: Viết logic JS bắt sự kiện click nút Run, lấy ra ID Test và Agent." --parent $phase3_id --json)
task3_2_json=$(bd create "Task 2: Gọi API/WebSocket thực thi test, nếu Auto gửi agent_id=null." --parent $phase3_id --json)
task3_3_json=$(bd create "Task 3: Cập nhật UI nút Run khi có kết quả." --parent $phase3_id --json)
task3_4_json=$(bd create "Task: Conductor - User Manual Verification 'Run Execution Logic Integration'" --parent $phase3_id --json)

task3_1_id=$(echo "$task3_1_json" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)
task3_2_id=$(echo "$task3_2_json" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)
task3_3_id=$(echo "$task3_3_json" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)
task3_4_id=$(echo "$task3_4_json" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)

bd dep add $task3_2_id $task3_1_id
bd dep add $task3_3_id $task3_2_id
bd dep add $task3_4_id $task3_3_id
bd dep add $phase3_id $phase2_id

cat << EOF > bd_output.json
{
  "beads_epic": "$epic_id",
  "beads_tasks": {
    "phase1": "$phase1_id",
    "phase1_task1": "$task1_1_id",
    "phase1_task2": "$task1_2_id",
    "phase1_task3": "$task1_3_id",
    "phase2": "$phase2_id",
    "phase2_task1": "$task2_1_id",
    "phase2_task2": "$task2_2_id",
    "phase2_task3": "$task2_3_id",
    "phase2_task4": "$task2_4_id",
    "phase3": "$phase3_id",
    "phase3_task1": "$task3_1_id",
    "phase3_task2": "$task3_2_id",
    "phase3_task3": "$task3_3_id",
    "phase3_task4": "$task3_4_id"
  }
}
EOF
