# Implementation Plan: PC Agent Management & Auto-Assignment

## Phase 1: PC Agent Status Reporting & Server Tracking
<!-- execution: sequential -->
- [x] Task 1: Cập nhật PC Agent (`client/pc_agent.py`) để gửi `status: idle` khi kết nối, và `status: running` khi đang chạy test.
- [x] Task 2: Cập nhật Server WebSocket Manager (vd: `server/ws/device_manager.py`) để lưu trữ và quản lý trạng thái của các PC Agent và thông tin test suite hiện tại.
- [x] Task 3: Tạo endpoint `GET /api/agents` trên server để trả về danh sách các PC Agent đang kết nối cùng trạng thái của chúng.
- [x] Task: Conductor - User Manual Verification 'Phase 1: PC Agent Status Reporting & Server Tracking' (Protocol in workflow.md)

## Phase 2: Hybrid Test Suite Assignment (Backend)
<!-- execution: sequential -->
- [ ] Task 1: Cập nhật logic chạy bộ test (vd: `server/routes/upload.py` hoặc runner) để nhận thêm tham số `agent_id` (ID cụ thể hoặc chuỗi `"auto"`).
- [ ] Task 2: Implement logic "Auto-assign": tự động tìm một PC Agent đang `idle` nếu yêu cầu gửi lên là `"auto"`.
- [ ] Task 3: Xử lý các luồng trả trạng thái (chuyển lại thành `idle` khi test xong/lỗi) và báo lỗi nếu không có Agent nào rảnh.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Hybrid Test Suite Assignment (Backend)' (Protocol in workflow.md)

## Phase 3: Dashboard UI & Agent Selection (Frontend)
<!-- execution: sequential -->
- [ ] Task 1: Tạo UI hiển thị danh sách PC Agent trên Dashboard (Tên/ID, Kết nối, Trạng thái, Test đang chạy).
- [ ] Task 2: Cập nhật giao diện "Run Test Suite" để thêm dropdown chọn PC Agent (gồm các Agent đang online và mục "Auto-assign").
- [ ] Task 3: Tích hợp API: truyền `agent_id` hoặc `"auto"` xuống Server khi bấm nút chạy.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Dashboard UI & Agent Selection (Frontend)' (Protocol in workflow.md)
