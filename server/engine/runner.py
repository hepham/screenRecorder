import asyncio
import uuid
import time
from typing import Dict
from pydantic import BaseModel
from server.ws.device_manager import manager
from server.models.device import DeviceRole, DeviceStatus
from server.models.test_case import get_test
import logging

logger = logging.getLogger(__name__)

class TestRunStatus(BaseModel):
    test_run_id: str
    test_id: str
    status: str
    timestamp: float
    video_filename: str | None = None
    suite_id: str | None = None
    executed_by: str | None = None
    verified: bool = False
    pass_lng: bool | None = None
    pass_asr: bool | None = None
    pass_capsule: bool | None = None
    pass_tts: bool | None = None
    reason: str | None = None

# Store runs
test_runs: Dict[str, TestRunStatus] = {}

async def create_test_run(test_id: str, agent_id: str, suite_id: str = None, executed_by: str = None) -> TestRunStatus:
    test_case = get_test(test_id)
    if not test_case:
        raise ValueError("Test case not found")
        
    actual_agent_id = agent_id
    if agent_id == "auto":
        actual_agent_id = None
        for dev_id, dev in manager.devices.items():
            if dev.role == DeviceRole.PC_AGENT and dev.status == DeviceStatus.IDLE:
                actual_agent_id = dev_id
                break
        if not actual_agent_id:
            raise ValueError("No idle PC agent available for auto-assignment")
    elif agent_id not in manager.devices or manager.devices[agent_id].status != DeviceStatus.IDLE:
        raise ValueError(f"Agent {agent_id} is not online or not idle")
    test_run_id = str(uuid.uuid4())
    run_status = TestRunStatus(
        test_run_id=test_run_id,
        test_id=test_id,
        status="running",
        timestamp=time.time(),
        suite_id=suite_id,
        executed_by=executed_by
    )
    test_runs[test_run_id] = run_status
    return run_status, actual_agent_id

async def execute_test_run(run_status: TestRunStatus, agent_id: str, audio_url: str):
    try:
        # Send run_test command to agent
        command = {
            "action": "run_test",
            "test_run_id": run_status.test_run_id,
            "audio_url": audio_url
        }
        await manager.send_command(agent_id, command)
        
        # The agent will handle the 60s recording and upload.
        # We don't need to block here. The status will update when upload completes.
        run_status.status = "waiting_for_upload"

    except Exception as e:
        logger.error(f"Error during test execution: {e}")
        run_status.status = "failed"
        
    return run_status

def get_test_runs():
    return list(test_runs.values())

def get_test_run(run_id: str):
    return test_runs.get(run_id)

def complete_test_run(run_id: str, video_filename: str):
    if run_id in test_runs:
        test_runs[run_id].status = "completed"
        test_runs[run_id].video_filename = video_filename
        return test_runs[run_id]
    return None

def fail_test_run(run_id: str, reason: str = None):
    if run_id in test_runs:
        test_runs[run_id].status = "failed"
        if reason:
            test_runs[run_id].reason = reason
        return test_runs[run_id]
    return None

from server.models.test_suite import get_suite

async def create_suite_run(suite_id: str, agent_id: str, executed_by: str = None) -> list[TestRunStatus]:
    suite = get_suite(suite_id)
    if not suite:
        raise ValueError("Suite not found")
        
    actual_agent_id = agent_id
    if agent_id == "auto":
        actual_agent_id = None
        for dev_id, dev in manager.devices.items():
            if dev.role == DeviceRole.PC_AGENT and dev.status == DeviceStatus.IDLE:
                actual_agent_id = dev_id
                break
        if not actual_agent_id:
            raise ValueError("No idle PC agent available for auto-assignment")
    elif agent_id not in manager.devices or manager.devices[agent_id].status != DeviceStatus.IDLE:
        raise ValueError(f"Agent {agent_id} is not online or not idle")

    run_statuses = []
    for test_id in suite.test_case_ids:
        test = get_test(test_id)
        if not test:
            continue
            
        test_run_id = str(uuid.uuid4())
        run_status = TestRunStatus(
            test_run_id=test_run_id,
            test_id=test_id,
            status="pending",
            timestamp=time.time(),
            suite_id=suite_id,
            executed_by=executed_by
        )
        test_runs[test_run_id] = run_status
        run_statuses.append(run_status)
        
    return run_statuses, actual_agent_id

async def execute_suite_run(run_statuses: list[TestRunStatus], agent_id: str):
    try:
        if not run_statuses:
            return
            
        suite_id = run_statuses[0].suite_id
        
        tests_data = []
        for run in run_statuses:
            test = get_test(run.test_id)
            if test:
                tests_data.append({
                    "test_run_id": run.test_run_id,
                    "test_id": test.id,
                    "audio_url": test.audio_url
                })
            run.status = "waiting_for_agent"
            
        command = {
            "action": "run_suite",
            "suite_id": suite_id,
            "tests": tests_data
        }
        await manager.send_command(agent_id, command)
        
        await manager.broadcast_to_web({
            "type": "suite_started",
            "suite_id": suite_id,
            "agent_id": agent_id,
            "total_tests": len(tests_data)
        })
        
    except Exception as e:
        logger.error(f"Error during suite execution: {e}")
        for run in run_statuses:
            run.status = "failed"

