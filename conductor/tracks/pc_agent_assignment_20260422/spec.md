# Specification: PC Agent Management & Auto-Assignment

## 1. Overview
Hệ thống hiện tại thiếu giao diện để quản lý danh sách các PC Agent. Tính năng này sẽ bổ sung một danh sách hiển thị trạng thái realtime của các PC Agent trên Dashboard, đồng thời cho phép phân công chạy test suite một cách thủ công (chọn đích danh Agent) hoặc tự động (Server tự tìm Agent đang rảnh).

## 2. Functional Requirements
1. **PC Agent Status Reporting (WebSocket):**
   - PC Agent chủ động gửi message báo cáo trạng thái làm việc về Server qua WebSocket (VD: `status: idle`, `status: running`).
   - Server duy trì danh sách các PC Agent đang kết nối cùng với trạng thái hiện hành của chúng.

2. **PC Agent Dashboard UI:**
   - Hiển thị danh sách các PC Agent.
   - Các thông định cần hiển thị:
     - Tên / ID của PC Agent.
     - Trạng thái kết nối: Online / Offline.
     - Trạng thái công việc: Idle (Rảnh) / Running (Đang chạy test).
     - Thông tin chi tiết: Tên bộ test đang chạy hoặc tiến độ (nếu đang ở trạng thái Running).

3. **Test Suite Assignment Strategy (Hybrid):**
   - **Manual Assignment:** Trên giao diện, người dùng có thể chọn một PC Agent cụ thể đang Online và Idle để giao bộ test.
   - **Auto-Assignment:** Người dùng có thể chọn "Auto", Server sẽ tự động quét danh sách PC Agent đang Online & Idle để phân công bộ test.

## 3. Acceptance Criteria
- [ ] Giao diện Dashboard hiển thị đúng và realtime danh sách các PC Agent cùng với trạng thái của chúng.
- [ ] PC Agent khi khởi động, chạy test và hoàn thành test đều bắn đúng status tương ứng về Server qua WebSocket.
- [ ] Giao diện chạy Test Suite cho phép chọn "Auto-assign" hoặc chọn một PC Agent cụ thể.
- [ ] Khi chọn Auto-assign, nếu có PC Agent rảnh, bộ test sẽ được đẩy thẳng xuống PC Agent đó.

## 4. Out of Scope
- Quản lý phân quyền user cho từng PC Agent (ai được quyền dùng Agent nào).
- Lịch sử hoạt động/log chi tiết của từng PC Agent qua các ngày.
