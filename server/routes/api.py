from server.engine.runner import create_test_run, execute_test_run, get_test_runs, get_test_run, TestRunStatus
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

import os
import aiofiles
from fastapi import File, Form, UploadFile
import time

@router.post("/tests/upload", response_model=TestCase)
async def upload_test(
    name: str = Form(...),
    utterance: str = Form(...),
    description: str = Form(""),
    audio: UploadFile = File(...)
):
    timestamp = int(time.time())
    safe_filename = audio.filename.replace(" ", "_")
    filename = f"{timestamp}_{safe_filename}"
    file_path = os.path.join("audios", filename)

    async with aiofiles.open(file_path, 'wb') as out_file:
        while content := await audio.read(1024 * 1024):
            await out_file.write(content)

    audio_url = f"http://127.0.0.1:8000/audios/{filename}" # Assuming local server for now, or just /audios/filename
    
    test_case_data = TestCaseCreate(
        name=name,
        utterance=utterance,
        audio_url=audio_url,
        description=description
    )
    return create_test(test_case_data)

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
        background_tasks.add_task(execute_test_run, run_status, agent, test.audio_url)
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

import io
import pandas as pd
from fastapi import UploadFile, File
from server.models.test_suite import check_suite_name_exists

@router.post("/test-suites/parse-import")
async def parse_import_suites(file: UploadFile = File(...)):
    if not file.filename.endswith(('.xlsx', '.csv')):
        raise HTTPException(status_code=400, detail="Invalid file format. Only .xlsx and .csv are supported.")
        
    try:
        contents = await file.read()
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        else:
            df = pd.read_excel(io.BytesIO(contents))
            
        df.columns = df.columns.str.strip().str.lower()
        
        required_cols = ['tên bộ test', 'utterance', 'audio']
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")
                
        preview_data = []
        errors = []
        
        for suite_name, group in df.groupby('tên bộ test'):
            if pd.isna(suite_name) or str(suite_name).strip() == '':
                continue
                
            suite_name_str = str(suite_name).strip()
            
            is_duplicate = check_suite_name_exists(suite_name_str)
            if is_duplicate:
                errors.append(f"Bộ test '{suite_name_str}' đã tồn tại.")
                
            cases = []
            for _, row in group.iterrows():
                utt = str(row.get('utterance', '')).strip()
                aud = str(row.get('audio', '')).strip()
                if str(row.get('utterance')) != 'nan' and utt:
                    cases.append({
                        "utterance": utt,
                        "audio": aud if aud and str(row.get('audio')) != 'nan' else ""
                    })
                    
            preview_data.append({
                "suite_name": suite_name_str,
                "is_duplicate": is_duplicate,
                "test_cases": cases,
                "case_count": len(cases)
            })
            
        return {
            "success": True,
            "preview_data": preview_data,
            "errors": errors
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing file: {str(e)}")

from pydantic import BaseModel

class ImportTestCaseInfo(BaseModel):
    utterance: str
    audio: str

class ImportTestSuiteInfo(BaseModel):
    suite_name: str
    test_cases: List[ImportTestCaseInfo]

import json
import zipfile
import shutil

@router.post("/test-suites/confirm-import")
async def confirm_import_suites(
    suites_json: str = Form(...),
    zip_file: UploadFile = File(None)
):
    from server.models.test_case import create_test, TestCaseCreate
    from server.models.test_suite import create_suite, TestSuiteCreate, check_suite_name_exists
    
    try:
        suites_data = json.loads(suites_json)
        suites = [ImportTestSuiteInfo(**s) for s in suites_data]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid suites JSON: {str(e)}")

    for suite in suites:
        if check_suite_name_exists(suite.suite_name):
            raise HTTPException(status_code=400, detail=f"Suite '{suite.suite_name}' already exists.")
            
    # Handle ZIP extraction
    extracted_files = {}
    if zip_file and zip_file.filename.endswith('.zip'):
        timestamp = int(time.time())
        zip_path = os.path.join("audios", f"upload_{timestamp}.zip")
        async with aiofiles.open(zip_path, 'wb') as out_file:
            while content := await zip_file.read(1024 * 1024):
                await out_file.write(content)
                
        extract_dir = os.path.join("audios", f"extracted_{timestamp}")
        os.makedirs(extract_dir, exist_ok=True)
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            # Map filename to actual path
            for root, dirs, files in os.walk(extract_dir):
                for file in files:
                    # Map both the exact filename and just the basename without path
                    extracted_files[file] = os.path.join(root, file).replace("\\", "/")
        except Exception as e:
             raise HTTPException(status_code=400, detail=f"Invalid ZIP file: {str(e)}")

    created_suites = []
    
    try:
        for suite in suites:
            test_case_ids = []
            for tc in suite.test_cases:
                # Find matching audio file
                audio_url = tc.audio
                if tc.audio and tc.audio in extracted_files:
                    # Move or just link to it
                    rel_path = os.path.relpath(extracted_files[tc.audio], "audios").replace("\\", "/")
                    audio_url = f"http://127.0.0.1:8000/audios/{rel_path}"

                new_tc = create_test(TestCaseCreate(
                    name=tc.utterance[:50] + ("..." if len(tc.utterance) > 50 else ""),
                    utterance=tc.utterance,
                    audio_url=audio_url,
                    description=tc.utterance
                ))
                test_case_ids.append(new_tc.id)
                
            new_suite = create_suite(TestSuiteCreate(
                name=suite.suite_name,
                description="Imported from Excel",
                test_case_ids=test_case_ids
            ))
            created_suites.append(new_suite)
            
        return {"success": True, "created_count": len(created_suites)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving data: {str(e)}")

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
        background_tasks.add_task(execute_suite_run, run_statuses, agent)
        return {"success": True, "run_statuses": run_statuses}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/runs", response_model=List[TestRunStatus])
async def list_runs():
    from server.engine.runner import get_test_runs
    return get_test_runs()

class TestRunVerificationUpdate(BaseModel):
    pass_lng: bool | None = None
    pass_asr: bool | None = None
    pass_capsule: bool | None = None
    pass_tts: bool | None = None
    reason: str | None = None

@router.put("/runs/{run_id}/verify", response_model=TestRunStatus)
async def verify_test_run(run_id: str, update: TestRunVerificationUpdate):
    from server.engine.runner import get_test_run
    run = get_test_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Test run not found")
        
    run.verified = True
    run.pass_lng = update.pass_lng
    run.pass_asr = update.pass_asr
    run.pass_capsule = update.pass_capsule
    run.pass_tts = update.pass_tts
    run.reason = update.reason
    
    return run

from server.models.device import DeviceInfo, DeviceRole
from server.ws.device_manager import manager

@router.get("/agents", response_model=List[DeviceInfo])
async def list_agents():
    # Return all devices that are PC Agents
    agents = []
    for device in manager.devices.values():
        if device.role == DeviceRole.PC_AGENT:
            agents.append(device)
    return agents
