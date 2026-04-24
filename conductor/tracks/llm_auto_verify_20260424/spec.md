# LLM Auto Verification & Agent Loop for Bixby Test Results

## Overview
Tích hợp LLM (via NVIDIA NIM API) để vừa **tự động tương tác với thiết bị** vừa **verify kết quả** test Bixby voice assistant. Hệ thống hoạt động như một AI QA Tester:

1. **Precondition setup**: ADB commands hoặc Bixby utterance để chuẩn bị trạng thái device
2. **Permission pre-grant**: ADB grant quyền 1 lần để clear permission dialogs
3. **Test execution + Agent Loop**: Phát audio Bixby command, sau đó LLM liên tục screenshot → phân tích → quyết định action (tap, swipe, chọn option, xác nhận) cho đến khi hoàn thành
4. **Auto verification**: Khi LLM xác định test đã xong, tự động verify pass/fail cho từng field

## Functional Requirements

### 1. Test Case Model — Thêm fields mới
- **`expected_result`** (text): Mô tả kết quả mong đợi khi lệnh Bixby thực hiện đúng
  - Ví dụ: "Bixby xác nhận đặt alarm 7:00, hiển thị Clock app"
  - Nếu để trống, LLM sẽ tự suy luận từ utterance
- **`precondition_type`** (enum: `none`, `utterance`, `adb`): Loại precondition
- **`precondition_value`** (text): 
  - Nếu type=`utterance`: câu nói cần phát trước
  - Nếu type=`adb`: ADB command(s) cần chạy (hỗ trợ multi-line, mỗi dòng = 1 command)
- **`precondition_audio_url`** (text, optional): URL file audio cho precondition utterance
- **`precondition_wait_seconds`** (int, default 5): Thời gian chờ sau khi chạy precondition

### 2. Permission Pre-Grant (One-time Setup)
- API endpoint hoặc ADB script để grant tất cả permissions phổ biến cho Bixby trước khi chạy test suite
- Permissions: READ_CONTACTS, SEND_SMS, CALL_PHONE, CAMERA, RECORD_AUDIO, READ_CALENDAR, WRITE_CALENDAR, SET_ALARM
- Chạy 1 lần per device, clear tất cả permission dialogs

### 3. LLM Agent Loop (Core Feature) 🧠
Sau khi phát audio Bixby command, PC Agent + Server phối hợp chạy agent loop:

```
┌─────────────────────────────────────────┐
│ 1. 🔊 Phát audio Bixby command         │
│ 2. ⏳ Đợi initial_wait (3s)            │
│ 3. 📸 ADB screencap → upload to server │
│ 4. 🧠 Server gửi screenshot cho LLM:   │
│    LLM phân tích và trả về 1 trong:    │
│    ├─ WAIT — đợi thêm (Bixby đang xử) │
│    ├─ TAP x,y — tap tại tọa độ        │
│    ├─ SWIPE x1,y1,x2,y2 — vuốt        │
│    ├─ TYPE "text" — nhập text          │
│    ├─ KEY event — bấm phím (back/home) │
│    ├─ SPEAK "utterance" — nói thêm     │
│    └─ DONE — test hoàn thành           │
│ 5. 🎮 Server gửi action cho PC Agent   │
│ 6. PC Agent thực thi ADB command       │
│ 7. → Quay lại bước 3                   │
│                                         │
│ Max iterations: 10                      │
│ Timeout: 60 seconds total              │
└─────────────────────────────────────────┘
```

#### LLM Agent Actions:
| Action | ADB Command | Khi nào |
|---|---|---|
| `WAIT` | (none, đợi 2s) | Bixby đang loading/processing |
| `TAP x y` | `adb shell input tap x y` | Permission dialog, option, button |
| `SWIPE x1 y1 x2 y2 duration` | `adb shell input swipe x1 y1 x2 y2 duration` | Scroll danh sách |
| `TYPE text` | `adb shell input text "text"` | Nhập text vào field |
| `KEY keycode` | `adb shell input keyevent keycode` | Back, Home, Enter |
| `SPEAK utterance` | Play follow-up audio | Bixby hỏi thêm |
| `DONE result` | (none) | Test hoàn thành, kèm verdict |

#### LLM Agent Prompt:
```
You are a QA tester interacting with a Samsung phone running Bixby voice assistant.

Test Goal: "{utterance}"
Expected Result: "{expected_result}"
Iteration: {n}/{max}
Previous actions: [{action_history}]

Current screenshot is attached.

Analyze the screenshot and decide the next action. Return JSON:
{
  "action": "TAP|SWIPE|TYPE|KEY|WAIT|SPEAK|DONE",
  "params": {"x": 540, "y": 1650},  // for TAP
  "reasoning": "I see a permission dialog asking for contacts access. Tapping Allow.",
  "screen_state": "permission_dialog|option_list|confirmation|processing|result|error",
  
  // Only when action is DONE:
  "verdict": {
    "pass_asr": true,
    "pass_capsule": true,
    "pass_tts": true,
    "pass_lng": true,
    "reasoning": "Bixby correctly processed the command..."
  }
}
```

### 4. PC Agent — ADB Interaction Layer
PC Agent cần hỗ trợ thêm các actions mới qua WebSocket:
- `screencap` → chụp screenshot, upload về server, trả về URL/path
- `adb_tap` → `adb shell input tap x y`
- `adb_swipe` → `adb shell input swipe x1 y1 x2 y2 duration`
- `adb_input_text` → `adb shell input text "text"`
- `adb_keyevent` → `adb shell input keyevent KEYCODE`
- `play_audio` → phát audio file (cho follow-up utterances)

### 5. Video Recording During Agent Loop
- scrcpy vẫn recording toàn bộ quá trình (bao gồm cả agent interactions)
- Kết quả video = full recording từ phát audio đến khi DONE
- Frame extraction + OCR vẫn chạy post-hoc cho archival/review

### 6. Excel Import — Thêm cột mới
- Hỗ trợ thêm các cột optional:
  - `expected_result` / `kết quả mong đợi`
  - `precondition_type` / `loại điều kiện`
  - `precondition_value` / `điều kiện tiên quyết`
  - `precondition_audio` / `audio điều kiện`
  - `precondition_wait` / `thời gian chờ`
- Backward-compatible với format Excel hiện tại

### 7. Verify Page UI Updates
- Hiển thị badge "AI Verified ✨" hoặc "Human Verified 👤"
- Hiển thị LLM reasoning và action history (collapsible)
- Show screenshot timeline: mỗi iteration với screenshot + action taken
- QA có thể override kết quả LLM (manual verify vẫn ưu tiên hơn)
- Nút "Re-run AI Verify" để chạy lại
- Thêm field `verified_by` (llm/human) vào test_runs

## Non-Functional Requirements
- Agent loop phải hoàn thành trong < 60 giây per test case (max 10 iterations)
- Mỗi iteration (screencap + LLM call) < 8 giây
- API key quản lý an toàn (environment variable)
- Fallback gracefully nếu NVIDIA API không available (skip agent loop, chỉ record + manual verify)
- Screenshot resolution: match device native (thường 1080x2400)

## Acceptance Criteria
- [ ] Test case model có thêm fields: expected_result, precondition_type/value/audio/wait
- [ ] Permission pre-grant endpoint hoạt động
- [ ] PC Agent thực thi precondition trước khi chạy test
- [ ] Agent loop: PC Agent screencap → Server → LLM → action → PC Agent thực thi → loop
- [ ] LLM xử lý đúng: permission dialogs, option selection, confirmation, follow-up questions
- [ ] Agent loop tự động dừng sau DONE hoặc max iterations
- [ ] Video recording bao gồm toàn bộ agent loop interactions
- [ ] Verify Page hiển thị AI/Human badge, reasoning, action history
- [ ] Excel import hỗ trợ cột mới (backward-compatible)
- [ ] Graceful fallback khi không có API key

## Out of Scope
- Training custom model cho Bixby-specific verification
- Multi-device parallel agent loops
- Agent loop cho non-Bixby apps (chỉ focus Bixby testing)
- Voice response verification (chỉ verify UI, không verify audio output)
