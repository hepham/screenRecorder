# Plan: Web Real-time Test Suite Progress

## Phase 1: WebSocket Backend Foundation
<!-- execution: sequential -->

- [x] Task 1: Quản lý kết nối WebSocket từ trình duyệt Web (Web Clients)
  - Thêm endpoint WebSocket mới trong `server/routes/ws.py` dành riêng cho Web (ví dụ: `/ws/web`).
  - Xây dựng `WebClientManager` (hoặc mở rộng `DeviceManager`) để lưu trữ danh sách các tab Web đang kết nối.
- [x] Task 2: Viết hàm Broadcast tới Web
  - Thêm phương thức `broadcast_to_web` để gửi dữ liệu JSON (cập nhật trạng thái) tới tất cả các Web Client.
- [x] Task: Conductor - User Manual Verification 'WebSocket Backend Foundation' (Protocol in workflow.md)

## Phase 2: Status Publishing (Gửi sự kiện cập nhật)
<!-- execution: sequential -->
<!-- depends: phase1 -->

- [x] Task 1: Bắn sự kiện khi Video Upload xong
  - Sửa đổi `server/routes/upload.py` (hoặc `runner.py`): gọi `broadcast_to_web` ngay khi video của một test case upload thành công.
- [x] Task 2: Bắn sự kiện thay đổi trạng thái của Test Suite
  - Bắn sự kiện báo hiệu khi Test Suite bắt đầu chạy, thay đổi tiến độ, và khi kết thúc hoàn toàn.
- [x] Task: Conductor - User Manual Verification 'Status Publishing' (Protocol in workflow.md)

## Phase 3: Frontend Integration (Giao diện Web)
<!-- execution: sequential -->
<!-- depends: phase1, phase2 -->

- [x] Task 1: Kết nối WebSocket trên `index.html`
  - Viết mã JavaScript để mở kết nối tới `/ws/web`.
  - Thiết lập cơ chế lắng nghe sự kiện từ Server.
- [x] Task 2: Cập nhật DOM (Giao diện) Real-time
  - Xử lý tin nhắn JSON nhận được từ WebSocket.
  - Cập nhật con số đếm tiến độ "Đã hoàn thành X/Y test cases" trực tiếp trên màn hình.
  - Đổi màu/trạng thái các dòng Test Case trong bảng (Đang chờ -> Hoàn thành) mà không cần F5 trang.
- [x] Task: Conductor - User Manual Verification 'Frontend Integration' (Protocol in workflow.md)
