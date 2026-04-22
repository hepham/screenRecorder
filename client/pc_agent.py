import asyncio
import websockets
import json
import subprocess
import time
import uuid
import os
import requests
import logging
import signal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SERVER_URL = "ws://192.168.1.5:8000/ws/agent"
API_URL = "http://192.168.1.5:8000/api"
import socket
AGENT_ID = f"pc-agent-{socket.gethostname()}"

def _download_and_play_audio(audio_url: str):
    """Sync function to download and play audio (runs in a thread)."""
    logger.info(f"Downloading audio from {audio_url}")
    r = requests.get(audio_url, timeout=30)
    r.raise_for_status()
    filename = "temp_audio.mp3"
    with open(filename, "wb") as f:
        f.write(r.content)
    logger.info("Playing audio...")
    if os.name == 'nt':
        os.system(f"start {filename}")
    else:
        subprocess.run(["ffplay", "-nodisp", "-autoexit", filename], stderr=subprocess.DEVNULL)

async def play_audio(audio_url: str):
    try:
        await asyncio.to_thread(_download_and_play_audio, audio_url)
    except Exception as e:
        logger.error(f"Error playing audio: {e}")

agent_status = "idle"

async def run_suite(suite_id: str, tests: list, ws):
    global agent_status
    if agent_status != "idle":
        logger.warning(f"Agent busy, ignoring suite {suite_id}")
        return
        
    agent_status = "running_test"
    logger.info(f"Starting suite {suite_id} with {len(tests)} tests")
    
    total = len(tests)
    for i, test in enumerate(tests):
        test_run_id = test.get("test_run_id")
        audio_url = test.get("audio_url")
        logger.info(f"Running suite test {test_run_id}")
        await run_test_logic(test_run_id, audio_url, ws, suite_id=suite_id, progress=f"{i+1}/{total}")
        
    logger.info(f"Suite {suite_id} completed")
    agent_status = "idle"
    if ws:
        await ws.send(json.dumps({"status": "idle"}))

def check_adb_device() -> bool:
    """Check if an ADB device is connected and available."""
    try:
        result = subprocess.run(
            ["adb", "devices"], capture_output=True, text=True, timeout=5
        )
        lines = result.stdout.strip().split("\n")
        # First line is "List of devices attached", actual devices follow
        devices = [l for l in lines[1:] if l.strip() and "device" in l]
        return len(devices) > 0
    except Exception as e:
        logger.error(f"Failed to check ADB devices: {e}")
        return False

async def report_test_failure(test_run_id: str, reason: str, ws):
    """Report a test failure back to the server."""
    logger.error(f"Test {test_run_id} failed: {reason}")
    if ws:
        await ws.send(json.dumps({
            "status": "test_failed",
            "test_run_id": test_run_id,
            "reason": reason
        }))


async def start_scrcpy_with_retry(local_file: str, max_retries: int = 2):
    """Starts scrcpy and waits a few seconds to confirm it is still alive and recording."""
    for attempt in range(max_retries):
        logger.info(f"Starting scrcpy to record to {local_file} (Attempt {attempt+1}/{max_retries})")
        if os.name == 'nt':
            record_proc = subprocess.Popen(
                ["scrcpy", "--no-playback", "--record", local_file],
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )
        else:
            record_proc = subprocess.Popen(
                ["scrcpy", "--no-playback", "--record", local_file]
            )

        # Wait for scrcpy to initialise (it writes directly to the Windows console,
        # so we can't intercept its output via pipes — we just wait a fixed amount).
        await asyncio.sleep(3)

        if record_proc.poll() is None:
            # Process is still running → recording has started successfully
            logger.info("scrcpy is alive and recording.")
            return record_proc, True

        logger.warning(f"scrcpy exited early on attempt {attempt+1}.")
        if os.path.exists(local_file):
            try:
                os.remove(local_file)
            except Exception as e:
                logger.warning(f"Could not remove partial file {local_file}: {e}")

        await asyncio.sleep(1)

    return None, False


async def run_test_logic(test_run_id: str, audio_url: str, ws, suite_id: str = None, progress: str = None):
    if ws:
        msg = {"status": "running_test"}
        if suite_id:
            msg["suite_id"] = suite_id
        if progress:
            msg["progress"] = progress
        await ws.send(json.dumps(msg))
    
    # Pre-check: is an ADB device connected?
    if not check_adb_device():
        await report_test_failure(
            test_run_id,
            "No ADB device found. Connect an Android device via USB or wireless ADB.",
            ws
        )
        return
    
    local_file = f"{test_run_id}.mp4"
    
    record_proc, success = await start_scrcpy_with_retry(local_file)
    if not success:
        await report_test_failure(
            test_run_id,
            "scrcpy failed to start and initialize recording after multiple retries.",
            ws
        )
        return
    
    # Only start playing audio AFTER scrcpy is fully ready and recording
    asyncio.create_task(play_audio(audio_url))
    
    logger.info("Waiting 15 seconds for test to complete (shortened for demo)...")
    await asyncio.sleep(15)
    
    logger.info("Stopping scrcpy")
    if os.name == 'nt':
        record_proc.send_signal(signal.CTRL_BREAK_EVENT)
    else:
        record_proc.terminate()
        
    try:
        record_proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        logger.warning("scrcpy did not stop gracefully, killing process")
        record_proc.kill()
    
    await asyncio.sleep(2)
    
    if os.path.exists(local_file):
        logger.info("Uploading video to server...")
        with open(local_file, "rb") as f:
            files = {"file": (local_file, f, "video/mp4")}
            data = {"device_id": AGENT_ID, "test_run_id": test_run_id}
            res = requests.post(f"{API_URL}/upload", files=files, data=data, timeout=30)
            if res.status_code == 200:
                logger.info("Upload complete!")
                if ws:
                    await ws.send(json.dumps({"status": "upload_complete"}))
            else:
                logger.error(f"Upload failed: {res.text}")
                
        os.remove(local_file)
    else:
        await report_test_failure(
            test_run_id,
            "Recording file not found after scrcpy finished.",
            ws
        )

async def run_test(test_run_id: str, audio_url: str, ws):
    global agent_status
    if agent_status != "idle":
        logger.warning(f"Agent busy, ignoring test {test_run_id}")
        return
        
    agent_status = "running_test"
    await run_test_logic(test_run_id, audio_url, ws)
    agent_status = "idle"
    if ws:
        await ws.send(json.dumps({"status": "idle"}))

async def auto_poll_queue(ws):
    global agent_status
    while True:
        await asyncio.sleep(5)
        if agent_status == "idle":
            try:
                res = requests.get(f"{API_URL}/agent/queue")
                if res.status_code == 200:
                    data = res.json()
                    suite = data.get("suite")
                    if suite:
                        executed_by = data.get("executed_by")
                        logger.info(f"Auto-polled suite {suite['id']}")
                        # We need to tell the server to create test runs for this suite!
                        # Wait, the queue just pops the suite. We need to "run" it via the server to get test_run_ids.
                        # Wait, we can just POST to /api/suites/{suite_id}/run with our agent_id
                        logger.info(f"Triggering suite run on server...")
                        requests.post(f"{API_URL}/suites/{suite['id']}/run?agent_id={AGENT_ID}&executed_by={executed_by}")
                        # The server will then send us a "run_suite" command over WebSocket!
                        # We don't run it here directly. We just triggered it.
            except Exception as e:
                logger.error(f"Error polling queue: {e}")

async def main():
    url = f"{SERVER_URL}/{AGENT_ID}"
    logger.info(f"Connecting to {url}")
    
    poll_task = None
    
    while True:
        try:
            async with websockets.connect(url) as ws:
                logger.info("Connected to server")
                await ws.send(json.dumps({"status": "idle"}))
                
                if not poll_task:
                    poll_task = asyncio.create_task(auto_poll_queue(ws))
                
                async for message in ws:
                    data = json.loads(message)
                    logger.info(f"Received action: {data.get('action')}")
                    
                    if data.get("action") == "run_test":
                        test_run_id = data.get("test_run_id")
                        audio_url = data.get("audio_url")
                        asyncio.create_task(run_test(test_run_id, audio_url, ws))
                    elif data.get("action") == "run_suite":
                        suite_id = data.get("suite_id")
                        tests = data.get("tests", [])
                        asyncio.create_task(run_suite(suite_id, tests, ws))
                        
        except Exception as e:
            logger.error(f"Connection error: {e}. Reconnecting in 5s...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
