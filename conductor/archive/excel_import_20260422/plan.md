# Implementation Plan: Excel Batch Import cho Test Suite

## Phase 1: Backend - API Phân tích File & Kiểm tra Trùng lặp
- [x] Task 1: Thiết lập thư viện xử lý Excel (`pandas` hoặc `openpyxl`).
- [x] Task 2: Tạo API endpoint (ví dụ: `POST /api/test-suites/parse-import`) để nhận file upload từ client.
- [x] Task 3: Viết logic đọc file, trích xuất 3 cột `tên bộ test`, `utterance`, `audio`.
- [x] Task 4: Viết logic truy vấn database để kiểm tra `tên bộ test` đã tồn tại chưa.
- [x] Task 5: Trả về kết quả JSON chứa dữ liệu xem trước (preview) và danh sách các bộ test bị lỗi/trùng lặp.
- [x] Task: Conductor - User Manual Verification 'Backend - API Phân tích File & Kiểm tra Trùng lặp' (Protocol in workflow.md)

## Phase 2: Frontend - UI Upload & Preview
- [x] Task 1: Thêm nút/form "Import từ Excel" trên giao diện quản lý Test Suite.
- [x] Task 2: Gọi API phân tích file khi người dùng chọn file và upload.
- [x] Task 3: Xây dựng bảng hiển thị dữ liệu xem trước (Preview Table) với tính năng cuộn (scroll).
- [x] Task 4: Hiển thị nổi bật thông báo lỗi (màu đỏ) cho những dòng bị báo trùng tên bộ test để người dùng biết.
- [x] Task: Conductor - User Manual Verification 'Frontend - UI Upload & Preview' (Protocol in workflow.md)

## Phase 3: Backend - API Lưu Dữ Liệu Chính Thức
- [x] Task 1: Tạo API endpoint (ví dụ: `POST /api/test-suites/confirm-import`) để nhận dữ liệu JSON đã được review từ frontend.
- [x] Task 2: Xử lý vòng lặp tạo mới các bản ghi Test Suite vào database.
- [x] Task 3: Tạo mới các bản ghi Test Case (bao gồm utterance và audio path) gắn với Test Suite ID tương ứng.
- [x] Task 4: Xử lý transaction (rollback nếu có lỗi) và trả về kết quả thành công.
- [x] Task: Conductor - User Manual Verification 'Backend - API Lưu Dữ thực Chính Thức' (Protocol in workflow.md)

## Phase 4: Frontend - Tích hợp Nút Xác nhận & Hoàn thiện
- [x] Task 1: Gắn nút "Xác nhận" (Confirm) trên bảng preview, chỉ cho phép bấm nếu không có lỗi trùng lặp.
- [x] Task 2: Gửi dữ liệu hợp lệ đến API lưu chính thức.
- [x] Task 3: Đóng bảng preview, hiển thị thông báo thành công và tải lại danh sách Test Suite hiện tại.
- [x] Task: Conductor - User Manual Verification 'Frontend - Tích hợp Nút Xác nhận & Hoàn thiện' (Protocol in workflow.md)
