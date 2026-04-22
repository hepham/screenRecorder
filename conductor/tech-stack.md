# Tech Stack

## Server (Backend)
- **Language**: Python 3.11+
- **Framework**: FastAPI
- **Data Storage**: In-memory data structures (for MVP)
- **Data Parsing**: Pandas and openpyxl for Excel/CSV import
- **WebSocket**: FastAPI native WebSocket support
- **File Storage**: Local filesystem (configurable)
- **Video Serving**: FastAPI StaticFiles / StreamingResponse

## Web Dashboard (Frontend)
- **HTML5 + Vanilla JS + CSS**
- **Video Player**: HTML5 `<video>` element
- **WebSocket Client**: Native browser WebSocket API

## Mobile App (Android)
- **Language**: Kotlin
- **Min SDK**: 21 (Android 5.0 Lollipop)
- **Screen Capture**: MediaProjection API
- **Video Encoding**: MediaRecorder API
- **Networking**: OkHttp (WebSocket client)
- **File Upload**: OkHttp multipart upload

## Communication Protocol
- **WebSocket** for real-time bidirectional messaging (commands + status)
- **HTTP REST** for video upload and retrieval
