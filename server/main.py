from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Remote Screen Recorder API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import os
from server.routes import ws, api, upload
from fastapi.staticfiles import StaticFiles

# Ensure recordings dir exists
os.makedirs("recordings", exist_ok=True)
os.makedirs("audios", exist_ok=True)

# Mount static files for recordings playback
app.mount("/recordings", StaticFiles(directory="recordings"), name="recordings")

# Serve audio files via explicit route to handle Unicode filenames on Windows
# (StaticFiles hangs on percent-encoded non-ASCII paths)
from fastapi.responses import FileResponse
from urllib.parse import unquote

@app.get("/audios/{filename:path}")
async def serve_audio(filename: str):
    decoded = unquote(filename)
    file_path = os.path.join("audios", decoded)
    if not os.path.isfile(file_path):
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(file_path, media_type="audio/mpeg")

app.include_router(ws.router, prefix="/ws", tags=["websocket"])
app.include_router(api.router, prefix="/api", tags=["api"])
app.include_router(upload.router, prefix="/api", tags=["upload"])

# Mount frontend
app.mount("/", StaticFiles(directory="server/static", html=True), name="static")
