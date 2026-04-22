from enum import Enum
from pydantic import BaseModel
from typing import Optional
from fastapi import WebSocket

class DeviceRole(str, Enum):
    PC_AGENT = "pc_agent"

class DeviceStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    IDLE = "idle"
    RUNNING_TEST = "running_test"
    UPLOAD_COMPLETE = "upload_complete"

class DeviceInfo(BaseModel):
    device_id: str
    role: DeviceRole
    status: DeviceStatus
    current_suite_name: Optional[str] = None
    current_test_progress: Optional[str] = None
