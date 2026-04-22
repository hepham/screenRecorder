# Implementation Plan: Layout & Run Execution Controls

## Phase 1: Layout Reorganization
<!-- execution: sequential -->
<!-- depends: -->

- [x] Task 1: Di chuyển cụm "Execute by" lên vị trí trên cùng của giao diện.
- [x] Task 2: Điều chỉnh CSS/Grid để khu vực "Connected PC Agent" và "Test Creation" có chiều rộng bằng nhau (50-50).
- [x] Task: Conductor - User Manual Verification 'Layout Reorganization' (Protocol in workflow.md)

## Phase 2: Target Agent Selector and Run Button
<!-- execution: sequential -->
<!-- depends: phase1 -->

- [x] Task 1: Cập nhật giao diện bảng "Test Suites & Test Cases", thêm cột "Target PC Agent" và cột chứa nút "Run".
- [x] Task 2: Đổ dữ liệu các PC Agent đang kết nối vào dropdown "Target PC Agent", thêm tùy chọn mặc định là "Auto".
- [x] Task 3: Bổ sung CSS cho nút Run, bao gồm trạng thái Loading/Disabled khi đang chạy.
- [x] Task: Conductor - User Manual Verification 'Target Agent Selector and Run Button' (Protocol in workflow.md)

## Phase 3: Run Execution Logic Integration
<!-- execution: sequential -->
<!-- depends: phase2 -->

- [x] Task 1: Viết logic JS bắt sự kiện click nút Run, lấy ra ID của Test Suite/Case và giá trị Agent được chọn.
- [x] Task 2: Gửi request gọi API/WebSocket thực thi test. Nếu chọn "Auto", gửi `agent_id = null` để hệ thống tự phân công.
- [x] Task 3: Cập nhật trạng thái Loading UI của nút Run và hiển thị thông báo thành công/lỗi khi nhận kết quả.
- [x] Task: Conductor - User Manual Verification 'Run Execution Logic Integration' (Protocol in workflow.md)
