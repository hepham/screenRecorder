import os
import time
import aiofiles
from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse
from server.engine.runner import complete_test_run

router = APIRouter()

RECORDINGS_DIR = "recordings"

@router.post("/upload")
async def upload_video(
    device_id: str = Form(...),
    test_run_id: str = Form(...),
    file: UploadFile = File(...)
):
    if not file.filename.endswith('.mp4'):
        raise HTTPException(status_code=400, detail="Only MP4 files are allowed")

    timestamp = int(time.time())
    filename = f"{test_run_id}_{device_id}_{timestamp}.mp4"
    file_path = os.path.join(RECORDINGS_DIR, filename)

    try:
        async with aiofiles.open(file_path, 'wb') as out_file:
            while content := await file.read(1024 * 1024):  # async read chunk
                await out_file.write(content)
                
        # Mark test run as completed
        complete_test_run(test_run_id, filename)
        
        return {"success": True, "filename": filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recordings")
async def list_recordings():
    try:
        files = os.listdir(RECORDINGS_DIR)
        mp4_files = [f for f in files if f.endswith('.mp4')]
        # Sort by creation time (newest first)
        mp4_files.sort(key=lambda x: os.path.getctime(os.path.join(RECORDINGS_DIR, x)), reverse=True)
        return mp4_files
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Note: Streaming is handled by StaticFiles in main.py
