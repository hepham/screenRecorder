import json
from typing import Dict, List, Optional
from fastapi import WebSocket
from server.models.device import DeviceInfo, DeviceRole, DeviceStatus

class ConnectionManager:
    def __init__(self):
        # Maps device_id to WebSocket connection
        self.active_connections: Dict[str, WebSocket] = {}
        # Maps device_id to DeviceInfo
        self.devices: Dict[str, DeviceInfo] = {}
        # Maps dashboard client to WebSocket connection
        self.dashboard_connections: List[WebSocket] = []

    async def connect_device(self, websocket: WebSocket, device_id: str, role: DeviceRole):
        await websocket.accept()
        self.active_connections[device_id] = websocket
        
        if device_id not in self.devices:
            self.devices[device_id] = DeviceInfo(
                device_id=device_id,
                role=role,
                status=DeviceStatus.IDLE
            )
        else:
            self.devices[device_id].status = DeviceStatus.IDLE
            self.devices[device_id].role = role
            
        await self.broadcast_device_update()

    def disconnect_device(self, device_id: str):
        if device_id in self.active_connections:
            del self.active_connections[device_id]
        if device_id in self.devices:
            self.devices[device_id].status = DeviceStatus.OFFLINE

    async def handle_disconnect(self, device_id: str):
        self.disconnect_device(device_id)
        await self.broadcast_device_update()

    async def send_command(self, device_id: str, command: dict):
        if device_id in self.active_connections:
            websocket = self.active_connections[device_id]
            await websocket.send_json(command)

    async def update_device_status(self, device_id: str, status: DeviceStatus):
        if device_id in self.devices:
            self.devices[device_id].status = status
            await self.broadcast_device_update()

    async def connect_dashboard(self, websocket: WebSocket):
        await websocket.accept()
        self.dashboard_connections.append(websocket)
        # Send current state
        await self.send_state_to_dashboard(websocket)

    def disconnect_dashboard(self, websocket: WebSocket):
        if websocket in self.dashboard_connections:
            self.dashboard_connections.remove(websocket)

    async def broadcast_device_update(self):
        state = self._get_device_state()
        for connection in self.dashboard_connections:
            try:
                await connection.send_json({"type": "device_update", "devices": state})
            except:
                # Handle disconnected dashboards gracefully
                pass

    async def send_state_to_dashboard(self, websocket: WebSocket):
        try:
            await websocket.send_json({"type": "device_update", "devices": self._get_device_state()})
        except:
            pass

    def _get_device_state(self) -> List[dict]:
        return [device.model_dump() for device in self.devices.values()]

manager = ConnectionManager()
