# Track Specification: Layout & Run Execution Controls

## Overview
Cập nhật lại bố cục UI của Dashboard để cân bằng hiển thị giữa danh sách Agent và chức năng Tạo Test. Đồng thời, bổ sung các nút điều khiển thực thi (chọn Target Agent và nút Run) ngay trên từng dòng Test Suite/Test Case, hỗ trợ cả cơ chế chọn thủ công và tự động phân công.

## Functional Requirements
1. **Thay đổi bố cục (Layout adjustments):**
   - Khu vực **"Connected PC Agent"** và **"Test Creation"** phải có kích thước/chiều rộng bằng nhau trên màn hình.
   - Mục **"Execute by"** (Cơ chế thực thi auto/manual) sẽ được đưa lên vị trí trên cùng của giao diện.
2. **Nút Run và Chọn Target PC Agent:**
   - Trong bảng danh sách "Test Suites & Test Cases" ở phía dưới, thêm mục chọn **"Target PC Agent"** (Dropdown) vào bên cạnh mỗi dòng test/suite.
   - Thêm nút **"Run"** nằm ngay cạnh mục chọn "Target PC Agent".
3. **Cơ chế hoạt động của nút Run:**
   - Khi bấm "Run", hệ thống sẽ gửi lệnh thực thi xuống backend.
   - Nếu người dùng chọn một "Target PC Agent" cụ thể, lệnh sẽ gửi thẳng tới agent đó.
   - Nếu người dùng để trống hoặc chọn "Auto", hệ thống sẽ tự động tìm PC Agent đang rảnh (Idle) để giao việc.
   - Nút Run sẽ hiển thị trạng thái "Loading/Running" để người dùng biết lệnh đang được thực thi.

## Acceptance Criteria
- [ ] Giao diện hai phần Connected PC Agent và Test Creation bằng nhau.
- [ ] Execute by được hiển thị ở trên cùng.
- [ ] Trong bảng Test Suites, mỗi hàng đều có Dropdown chọn Agent và nút Run.
- [ ] Bấm Run với Agent cụ thể -> Agent đó nhận lệnh và chạy.
- [ ] Bấm Run với Auto -> Hệ thống tự assign Agent rảnh và chạy.

## Out of Scope
- Thay đổi cấu trúc database hoặc sửa core logic tự động assign ở backend (nếu backend đã có sẵn, chỉ việc gắn vào).
