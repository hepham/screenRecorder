from pydantic import BaseModel
from typing import List, Optional
import uuid

class TestSuiteCreate(BaseModel):
    name: str
    description: Optional[str] = None
    test_case_ids: List[str]

class TestSuite(TestSuiteCreate):
    id: str

# In-memory storage for test suites
test_suites_db = {}
# Queue for pending suites
pending_suites_queue = []

def get_all_suites() -> List[TestSuite]:
    return list(test_suites_db.values())

def create_suite(data: TestSuiteCreate) -> TestSuite:
    suite_id = str(uuid.uuid4())
    suite = TestSuite(id=suite_id, **data.model_dump())
    test_suites_db[suite_id] = suite
    return suite

def get_suite(suite_id: str) -> Optional[TestSuite]:
    return test_suites_db.get(suite_id)

def delete_suite(suite_id: str) -> bool:
    if suite_id in test_suites_db:
        del test_suites_db[suite_id]
        return True
    return False

def enqueue_suite(suite_id: str, executed_by: str = "Auto"):
    if suite_id in test_suites_db:
        pending_suites_queue.append({"suite_id": suite_id, "executed_by": executed_by})
        return True
    return False

def dequeue_suite():
    if pending_suites_queue:
        return pending_suites_queue.pop(0)
    return None
