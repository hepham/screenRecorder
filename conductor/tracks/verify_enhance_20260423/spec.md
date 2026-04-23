# Spec: Test Execution Done-State & Enhanced Verify Page

## Overview
Sau khi PC agent hoàn thành một test case, hệ thống tự động đánh dấu trạng thái là `done` (completed) trên cả dashboard lẫn verify page sidebar. Khi người dùng bấm vào test case đó, họ được điều hướng đến verify page nơi có thể xem video, audio, và bảng kết quả chi tiết (Utterance, ASR, Capsule, TTS, NLG) gửi từ PC agent. Người dùng tick True/False cho từng mục và điền Reason — auto-save sẽ đánh dấu test là `verified`. Toàn bộ data được persist vào SQLite database.

## Functional Requirements

### 1. Auto Mark "Done" (Executed Status)
- Khi PC agent gửi completion message cho một test_run_id, server tự động set `status = "completed"`.
- Dashboard (combined-list) hiển thị badge "✅ Done" cho test case có run completed.
- Badge cập nhật real-time qua WebSocket broadcast — không cần page refresh.
- Test case có `verified=true` hiển thị badge "✓ Verified".

### 2. Click-to-Verify Navigation
- Test case có status `completed` hoặc `verified` trên dashboard có thể click để mở verify page.
- Verify page URL: `/verify.html?suite_id=<id>`

### 3. Result Data Fields (từ PC agent)
Thêm các field vào `TestRunStatus` model để lưu kết quả từ PC agent:
- `result_utterance: str | None` — utterance được nhận dạng
- `result_asr: str | None` — kết quả ASR
- `result_capsule: str | None` — kết quả Capsule/Intent
- `result_tts: str | None` — kết quả TTS
- `result_nlg: str | None` — kết quả NLG
Tất cả default = None. PC agent có stub function `report_test_results()` để implement sau.

### 4. Enhanced Verify Page — Results Table
Thêm bảng kết quả vào main verification area với các cột:
- **Label** (Utterance / ASR / Capsule / TTS / NLG)
- **Giá trị từ agent** (string hoặc "–" nếu None)
- **Pass** (True checkbox)
- **Fail** (False checkbox)

Cuối bảng có text input **Reason** chung. Auto-save khi:
- User thay đổi checkbox
- User switch sang test case khác

### 5. Verification State
- `pass_nlg: bool | None` — thêm mới (tương ứng NLG row)
- Sau khi auto-save thành công → set `verified=true`, cập nhật sidebar badge

### 6. Database Persistence (SQLite + aiosqlite)
Migrate toàn bộ in-memory storage sang SQLite:

| Table | Key Fields |
|-------|-----------|
| `test_cases` | id, name, utterance, audio_url, description |
| `test_suites` | id, name, description, test_case_ids (JSON array), queue (JSON) |
| `test_runs` | id, test_id, suite_id, status, video_filename, executed_by, timestamp, verified, pass_lng, pass_asr, pass_capsule, pass_tts, pass_nlg, reason, result_utterance, result_asr, result_capsule, result_tts, result_nlg |

- Dùng **aiosqlite** (async, no heavy ORM)
- Startup: auto-create tables nếu chưa tồn tại
- Database file: `data/app.db`

## Acceptance Criteria
- [ ] Test hoàn thành → badge "Done" xuất hiện trên dashboard không cần refresh
- [ ] Click test Done/Verified → mở verify page đúng suite
- [ ] Verify page hiển thị bảng 5 rows với giá trị từ agent (hoặc "–")
- [ ] True/False checkbox hoạt động cho từng row
- [ ] Auto-save hoạt động khi switch test hoặc change checkbox
- [ ] Sau save → sidebar cập nhật badge "Verified"
- [ ] Restart server → data vẫn còn (SQLite persist)
- [ ] Stub function `report_test_results()` tồn tại trong pc_agent.py

## Out of Scope
- Bulk verification
- Tìm kiếm cross-suite
- Edit result values từ UI (chỉ PC agent mới set)
- Migration tool cho existing in-memory data
