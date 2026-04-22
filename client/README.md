# PC Agent Setup & Run Guide

The PC Agent (`pc_agent.py`) is a module that runs on a computer (PC) directly connected to an Android device. Its main responsibilities are connecting to the Backend Server via WebSockets, continuously polling the queue to receive new test suites, controlling the phone (playing audio, recording the screen via `scrcpy`), and uploading the resulting video file to the server upon completion.

## 📋 Prerequisites

For the PC Agent to function correctly, your computer must meet the following requirements:

1. **Python 3.8+**: Ensure Python is installed on your machine.
2. **scrcpy**: A tool used to record the Android screen from your computer.
   - [scrcpy Installation Guide](https://github.com/Genymobile/scrcpy/blob/master/doc/windows.md).
   - **Important**: After downloading and extracting, you must add the path to the directory containing `scrcpy` to your system's **Environment Variables -> PATH** so the `scrcpy` command can be executed from anywhere.
3. **ADB (Android Debug Bridge)**: Typically included in the `scrcpy` download package.
4. **Android Device**:
   - Connected to the computer via USB cable (or wireless ADB).
   - **Developer Options** enabled.
   - **USB Debugging** enabled.
   - Authorized "Allow USB debugging" (trusted device) when the prompt appears on the phone screen.

## ⚙️ Environment Setup

Open a Terminal (Command Prompt / PowerShell / WSL) at the root of the project (or inside the `client/` directory) and install the required Python libraries:

```bash
pip install websockets requests
```
*(Alternatively, you can run `pip install -r requirements.txt` from the project root to install all dependencies).*

## 🚀 Configuration & Running the Agent

### Step 1: Verify device connection
Open a terminal and run the following command to ensure your PC recognizes and has permission to control the phone:
```bash
adb devices
```
> **Note:** You should see a device ID along with the status `device`. If the status is `unauthorized`, wake up the phone screen and tap "Allow" on the prompt that appears.

### Step 2: Configure Server Address (If needed)
By default, `pc_agent.py` is configured to connect to a Backend Server running on the same computer (localhost):
- `SERVER_URL = "ws://[IP_ADDRESS]/ws/agent"`
- `API_URL = "http://[IP_ADDRESS]/api"`

> ⚠️ **Attention**: If the Backend Server (FastAPI) is running on a different machine (not the PC the phone is plugged into), you need to open `pc_agent.py` and change the IP `127.0.0.1` to the static IP of that Backend server (e.g., `[IP_ADDRESS]`).

### Step 3: Start the PC Agent
Navigate to the directory containing the file and run the Agent:
```bash
cd client
python pc_agent.py
```

### 🎉 What happens upon success?
If everything is configured correctly, the PC Agent will output logs to the Terminal similar to this:
```text
INFO:__main__:Connecting to ws://[IP_ADDRESS]/ws/agent/pc-agent-1a2b3c
INFO:__main__:Connected to server
```

**How it works**:
- Once started, the Agent will automatically ping the Server every 5 seconds to ask if there are any Test Suites waiting to be run (`Auto-polled suite...`).
- If a Test Suite is assigned, the Agent automatically spawns an `scrcpy --record` process, downloads and plays the `.mp3` audio, then closes the recording and uploads the result to the `/upload` API.
- This process is fully automated; no manual interaction with the phone is required.
