import asyncio
import uuid
import time
from typing import Dict, List
from pydantic import BaseModel
from server.ws.device_manager import manager
from server.models.device import DeviceRole, DeviceStatus
from server.models.test_case import get_test
import logging
import os
import aiosqlite

logger = logging.getLogger(__name__)

DB_PATH = os.path.join("data", "app.db")

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
    pass_nlg: bool | None = None
    reason: str | None = None
    result_utterance: str | None = None
    result_asr: str | None = None
    result_capsule: str | None = None
    result_tts: str | None = None
    result_nlg: str | None = None

async def create_test_run(test_id: str, agent_id: str, suite_id: str = None, executed_by: str = None) -> TestRunStatus:
    test_case = await get_test(test_id)
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
    
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT INTO test_runs (id, test_id, suite_id, status, video_filename, executed_by, timestamp, verified, pass_lng, pass_asr, pass_capsule, pass_tts, pass_nlg, reason, result_utterance, result_asr, result_capsule, result_tts, result_nlg)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (test_run_id, test_id, suite_id, "running", None, executed_by, run_status.timestamp, False, None, None, None, None, None, None, None, None, None, None, None)
        )
        await db.commit()
        
    return run_status, actual_agent_id

async def execute_test_run(run_status: TestRunStatus, agent_id: str, audio_url: str):
    try:
        command = {
            "action": "run_test",
            "test_run_id": run_status.test_run_id,
            "audio_url": audio_url
        }
        await manager.send_command(agent_id, command)
        
        run_status.status = "waiting_for_upload"
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("UPDATE test_runs SET status=? WHERE id=?", ("waiting_for_upload", run_status.test_run_id))
            await db.commit()

    except Exception as e:
        logger.error(f"Error during test execution: {e}")
        run_status.status = "failed"
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("UPDATE test_runs SET status=? WHERE id=?", ("failed", run_status.test_run_id))
            await db.commit()
            
    return run_status

async def get_test_runs() -> List[TestRunStatus]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM test_runs") as cursor:
            rows = await cursor.fetchall()
            runs = []
            for row in rows:
                d = dict(row)
                d['test_run_id'] = d.pop('id')
                if d.get('verified') is None:
                    d['verified'] = False
                else:
                    d['verified'] = bool(d['verified'])
                runs.append(TestRunStatus(**d))
            return runs

async def get_test_run(run_id: str) -> TestRunStatus | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM test_runs WHERE id = ?", (run_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                d = dict(row)
                d['test_run_id'] = d.pop('id')
                if d.get('verified') is None:
                    d['verified'] = False
                else:
                    d['verified'] = bool(d['verified'])
                return TestRunStatus(**d)
            return None

async def complete_test_run(run_id: str, video_filename: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE test_runs SET status=?, video_filename=? WHERE id=?", ("completed", video_filename, run_id))
        await db.commit()
    return await get_test_run(run_id)

async def fail_test_run(run_id: str, reason: str = None):
    async with aiosqlite.connect(DB_PATH) as db:
        if reason:
            await db.execute("UPDATE test_runs SET status=?, reason=? WHERE id=?", ("failed", reason, run_id))
        else:
            await db.execute("UPDATE test_runs SET status=? WHERE id=?", ("failed", run_id))
        await db.commit()
    return await get_test_run(run_id)

from server.models.test_suite import get_suite

async def create_suite_run(suite_id: str, agent_id: str, executed_by: str = None) -> list[TestRunStatus]:
    suite = await get_suite(suite_id)
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
    async with aiosqlite.connect(DB_PATH) as db:
        for test_id in suite.test_case_ids:
            test = await get_test(test_id)
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
            
            await db.execute(
                """INSERT INTO test_runs (id, test_id, suite_id, status, video_filename, executed_by, timestamp, verified, pass_lng, pass_asr, pass_capsule, pass_tts, pass_nlg, reason, result_utterance, result_asr, result_capsule, result_tts, result_nlg)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (test_run_id, test_id, suite_id, "pending", None, executed_by, run_status.timestamp, False, None, None, None, None, None, None, None, None, None, None, None)
            )
            run_statuses.append(run_status)
        await db.commit()
        
    return run_statuses, actual_agent_id

async def execute_suite_run(run_statuses: list[TestRunStatus], agent_id: str):
    try:
        if not run_statuses:
            return
            
        suite_id = run_statuses[0].suite_id
        
        tests_data = []
        async with aiosqlite.connect(DB_PATH) as db:
            for run in run_statuses:
                test = await get_test(run.test_id)
                if test:
                    tests_data.append({
                        "test_run_id": run.test_run_id,
                        "test_id": test.id,
                        "audio_url": test.audio_url
                    })
                run.status = "waiting_for_agent"
                await db.execute("UPDATE test_runs SET status=? WHERE id=?", ("waiting_for_agent", run.test_run_id))
            await db.commit()
            
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
        async with aiosqlite.connect(DB_PATH) as db:
            for run in run_statuses:
                run.status = "failed"
                await db.execute("UPDATE test_runs SET status=? WHERE id=?", ("failed", run.test_run_id))
            await db.commit()

async def update_test_run_verification(run_id: str, verified: bool, pass_lng: bool | None, pass_asr: bool | None, pass_capsule: bool | None, pass_tts: bool | None, reason: str | None) -> TestRunStatus | None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE test_runs 
            SET verified=?, pass_lng=?, pass_asr=?, pass_capsule=?, pass_tts=?, reason=?
            WHERE id=?
        """, (verified, pass_lng, pass_asr, pass_capsule, pass_tts, reason, run_id))
        await db.commit()
    return await get_test_run(run_id)
