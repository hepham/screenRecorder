from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from server.ws.device_manager import manager
from server.models.device import DeviceRole, DeviceStatus
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.websocket("/agent/{agent_id}")
async def websocket_agent_endpoint(websocket: WebSocket, agent_id: str):
    await manager.connect_device(websocket, agent_id, DeviceRole.PC_AGENT)
    try:
        while True:
            data = await websocket.receive_json()
            if "status" in data:
                try:
                    status = DeviceStatus(data["status"])
                    await manager.update_device_status(agent_id, status)
                except ValueError:
                    logger.warning(f"Invalid status received from {agent_id}: {data['status']}")
    except WebSocketDisconnect:
        await manager.handle_disconnect(agent_id)

@router.websocket("/dashboard")
async def websocket_dashboard_endpoint(websocket: WebSocket):
    await manager.connect_dashboard(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            # Handle dashboard commands
            pass
    except WebSocketDisconnect:
        manager.disconnect_dashboard(websocket)
