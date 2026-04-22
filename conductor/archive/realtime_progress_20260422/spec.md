# Track: Web Real-time Test Suite Progress

## 1. Overview
Triển khai tính năng cập nhật tiến độ chạy bộ test (Test Suite) theo thời gian thực trên giao diện Web. Việc này giúp người dùng biết được bộ test đang chạy đến đâu mà không cần tải lại (refresh) trang. Việc ghi âm điện thoại vẫn giữ nguyên cơ chế của `scrcpy`.

## 2. Functional Requirements
- **Server-side (WebSocket):** 
  - Tích hợp thêm kênh WebSocket (hoặc tận dụng kênh hiện tại) để giao tiếp với Web Client.
  - Server sẽ bắn (emit) sự kiện cập nhật mỗi khi một Test Case hoàn tất (ngay sau khi Agent upload xong video) hoặc khi trạng thái của toàn bộ Test Suite thay đổi.
- **Web-side:** 
  - Kết nối WebSocket tới server.
  - Cập nhật và hiển thị trạng thái tổng quan của Test Suite (Đang chạy, Hoàn thành, v.v.).
  - Hiển thị bộ đếm tiến độ thực tế (ví dụ: "Đã hoàn thành: 3/10 test cases").
  - Trạng thái các test case trong danh sách cũng cần đổi màu/trạng thái realtime.

## 3. Acceptance Criteria
- [ ] Giao diện Web tự động cập nhật tiến độ khi Agent đang thực thi Test Suite.
- [ ] Thông tin (trạng thái, video URL nếu có, tỉ lệ phần trăm hoặc đếm số lượng) hiện ra đúng với thực tế không bị delay hay cần F5.

## 4. Out of Scope
- Chỉnh sửa hệ thống ghi hình/ghi âm (scrcpy) trên PC Agent (hiện tại scrcpy đã tự động ghi nội bộ audio nếu thiết bị là Android 11+).
