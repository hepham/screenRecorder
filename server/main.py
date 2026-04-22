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

# Mount static files for recordings playback
app.mount("/recordings", StaticFiles(directory="recordings"), name="recordings")

app.include_router(ws.router, prefix="/ws", tags=["websocket"])
app.include_router(api.router, prefix="/api", tags=["api"])
app.include_router(upload.router, prefix="/api", tags=["upload"])

# Mount frontend
app.mount("/", StaticFiles(directory="server/static", html=True), name="static")
