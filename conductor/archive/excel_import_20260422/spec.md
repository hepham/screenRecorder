# Overview
Track này triển khai tính năng cho phép import hàng loạt các Bộ test (Test Suites) cùng với các test case của chúng thông qua một file Excel, giúp tiết kiệm thời gian thao tác thủ công.

# Functional Requirements
1. **Excel Import Interface:** Cung cấp giao diện upload file Excel (`.xlsx` hoặc `.csv`) trên trang quản lý Test Suite.
2. **File Format Parsing:** Hệ thống phân tích cú pháp file Excel dựa trên 3 cột bắt buộc: `tên bộ test` (Test Suite Name), `utterance`, và `audio` (chứa URL/đường dẫn đến các file audio đã có sẵn trên server).
3. **Data Preview:** Sau khi đọc file Excel, hệ thống hiển thị một bảng xem trước (preview) dữ liệu trên UI để người dùng kiểm tra độ chính xác trước khi lưu chính thức.
4. **Duplicate Validation:** Kiểm tra `tên bộ test` có bị trùng lặp với dữ liệu đã có trong database hay không. Nếu trùng, hệ thống báo lỗi ngay tại bảng preview và yêu cầu người dùng đổi tên bộ test trong file rồi upload lại.
5. **Confirmation & Save:** Người dùng nhấn nút "Xác nhận" (Confirm) ở bảng preview để lưu toàn bộ các bộ test hợp lệ vào cơ sở dữ liệu.

# Non-Functional Requirements
1. Trình đọc file Excel phải xử lý tốt các dòng trống hoặc bị thiếu dữ liệu mà không làm crash ứng dụng (ví dụ: báo lỗi dòng cho người dùng).
2. Bảng preview trên UI cần hỗ trợ phân trang (pagination) hoặc cuộn (scroll) nếu file Excel có số lượng dòng quá lớn.

# Acceptance Criteria
- [ ] UI có nút chức năng để chọn và upload file Excel/CSV.
- [ ] Hệ thống trích xuất thành công dữ liệu từ 3 cột định sẵn.
- [ ] Bảng preview hiện ra chính xác với dữ liệu vừa import.
- [ ] Hệ thống chặn lưu và báo lỗi rõ ràng nếu `tên bộ test` đã tồn tại.
- [ ] Khi nhấn "Xác nhận", các bộ test và test case tương ứng được tạo chính xác trong database.

# Out of Scope
- Upload trực tiếp file âm thanh từ máy tính cùng lúc với file Excel (mặc định file âm thanh đã được upload hoặc có sẵn URL).
- Chỉnh sửa trực tiếp dữ liệu (edit inline) ngay trên bảng preview của UI (người dùng cần sửa file Excel và upload lại).
