import asyncio
import websockets
import json

async def test_dashboard_ws():
    uri = "ws://127.0.0.1:8000/ws/dashboard"
    try:
        async with websockets.connect(uri) as ws:
            # We should immediately receive the current state
            message = await asyncio.wait_for(ws.recv(), timeout=5.0)
            data = json.loads(message)
            print("Received from dashboard WS:", json.dumps(data, indent=2))
    except Exception as e:
        print(f"Failed to connect or receive: {e}")

if __name__ == "__main__":
    asyncio.run(test_dashboard_ws())
