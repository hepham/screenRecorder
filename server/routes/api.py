from server.engine.runner import create_test_run, execute_test_run, get_test_runs, get_test_run, TestRunStatus
import asyncio
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
from server.models.test_case import TestCase, TestCaseCreate, get_all_tests, create_test, get_test, delete_test

router = APIRouter()

@router.get("/tests", response_model=List[TestCase])
async def list_tests():
    return get_all_tests()

@router.post("/tests", response_model=TestCase)
async def add_test(test: TestCaseCreate):
    return create_test(test)

@router.get("/tests/{test_id}", response_model=TestCase)
async def retrieve_test(test_id: str):
    test = get_test(test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    return test

@router.delete("/tests/{test_id}")
async def remove_test(test_id: str):
    if delete_test(test_id):
        return {"success": True}
    raise HTTPException(status_code=404, detail="Test not found")

@router.post("/tests/{test_id}/run", response_model=TestRunStatus)
async def run_test(test_id: str, agent_id: str, background_tasks: BackgroundTasks):
    test = get_test(test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
        
    try:
        run_status, agent = await create_test_run(test_id, agent_id)
        background_tasks.add_task(
            lambda: asyncio.create_task(execute_test_run(run_status, agent, test.audio_url))
        )
        return run_status
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from server.models.test_suite import TestSuite, TestSuiteCreate, get_all_suites, create_suite, get_suite, delete_suite, enqueue_suite, dequeue_suite

@router.get("/suites", response_model=List[TestSuite])
async def list_suites():
    return get_all_suites()

@router.post("/suites", response_model=TestSuite)
async def add_suite(suite: TestSuiteCreate):
    return create_suite(suite)

@router.get("/suites/{suite_id}", response_model=TestSuite)
async def retrieve_suite(suite_id: str):
    suite = get_suite(suite_id)
    if not suite:
        raise HTTPException(status_code=404, detail="Suite not found")
    return suite

@router.delete("/suites/{suite_id}")
async def remove_suite(suite_id: str):
    if delete_suite(suite_id):
        return {"success": True}
    raise HTTPException(status_code=404, detail="Suite not found")

@router.post("/suites/{suite_id}/queue")
async def queue_suite(suite_id: str, executed_by: str = "Auto"):
    suite = get_suite(suite_id)
    if not suite:
        raise HTTPException(status_code=404, detail="Suite not found")
    if enqueue_suite(suite_id, executed_by):
        return {"success": True, "message": "Suite enqueued"}
    raise HTTPException(status_code=500, detail="Failed to enqueue suite")

@router.get("/agent/queue")
async def get_agent_queue():
    item = dequeue_suite()
    if item:
        suite = get_suite(item["suite_id"])
        if suite:
            return {"suite": suite, "executed_by": item["executed_by"]}
    return {"suite": None}

@router.post("/suites/{suite_id}/run")
async def run_suite(suite_id: str, agent_id: str, background_tasks: BackgroundTasks, executed_by: str = None):
    from server.engine.runner import create_suite_run, execute_suite_run
    suite = get_suite(suite_id)
    if not suite:
        raise HTTPException(status_code=404, detail="Suite not found")
        
    try:
        run_statuses, agent = await create_suite_run(suite_id, agent_id, executed_by)
        background_tasks.add_task(
            lambda: asyncio.create_task(execute_suite_run(run_statuses, agent))
        )
        return {"success": True, "run_statuses": run_statuses}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
