# Specification: Test Suite Assignment & User Tracking

## Overview
Tính năng này mở rộng hệ thống hiện tại để hỗ trợ chạy thử nghiệm theo lô (batch execution) thông qua khái niệm **Test Suite** (Bộ Test) và theo dõi **User/Agent** thực hiện. Hệ thống cho phép user từ Web Dashboard gán một Test Suite cho PC Agent, hoặc PC Agent có thể tự động nhận Test Suite từ hàng đợi (queue) để thực thi.

## Functional Requirements

1. **Quản lý Test Suite & Test Case**
   - Hỗ trợ tạo Test Suite bao gồm nhiều Test Case con.
   - Một Test Suite có thể định nghĩa thứ tự chạy của các Test Case bên trong nó.

2. **User Tracking (Theo dõi người thực hiện)**
   - Web Dashboard có trường nhập `Executed By` (tên người chạy) khi kích hoạt Test Suite thủ công.
   - Hệ thống lưu trữ thông tin "Người thực hiện" (Tên user nhập từ web hoặc `agent_id` nếu PC Agent tự chạy) cho mỗi bản ghi kết quả (Test Run).

3. **Giao việc & Tự động nhận việc (Assignment)**
   - **Gán thủ công (Manual Assignment):** Trên Web, user chọn 1 Test Suite, điền tên mình, chọn 1 PC Agent đang rảnh và bấm chạy.
   - **Tự động nhận việc (Auto Polling):** PC Agent khi rảnh rỗi có thể liên tục "hỏi" Server xem có Test Suite nào đang chờ không. Nếu có, Server gán Test Suite đó cho PC Agent này chạy tự động.

4. **Theo dõi tiến độ & Lịch sử**
   - Quản lý trạng thái của Test Suite Run (Pending, In Progress, Completed, Failed).
   - Hiển thị tiến độ trực tiếp trên Dashboard (ví dụ: đã chạy xong 2/5 Test Cases).
   - Lưu trữ lịch sử phân công (PC Agent nào đã/đang xử lý Test Suite nào).

## Non-Functional Requirements
- Đảm bảo tính đồng bộ: Khi một PC Agent nhận Test Suite tự động, Suite đó phải bị lock để các PC Agent khác không nhận trùng.

## Acceptance Criteria
- [ ] Có thể tạo Test Suite với ít nhất 2 Test Case từ Web Dashboard.
- [ ] Có thể điền tên User và gán Test Suite cho PC Agent từ giao diện.
- [ ] PC Agent tự động chạy lần lượt các Test Case trong Suite và báo cáo kết quả từng cái.
- [ ] Nếu bật chế độ auto-polling, PC Agent tự động nhận Test Suite mới được đẩy vào hàng đợi mà không cần thao tác trên Dashboard.
- [ ] Dashboard hiển thị đúng tên User đã chạy, PC Agent được gán, và tiến độ hiện tại (x/y).

## Out of Scope
- Hệ thống Đăng nhập (Authentication / Authorization) phức tạp (chỉ dùng ô nhập text cơ bản).
- Quản lý phân quyền user (ai được chạy test nào).
