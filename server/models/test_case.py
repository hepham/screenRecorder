from pydantic import BaseModel
from typing import Optional
import uuid

class TestCaseCreate(BaseModel):
    name: str
    utterance: str
    audio_url: str
    description: Optional[str] = None

class TestCase(TestCaseCreate):
    id: str

# In-memory storage for test cases
test_cases_db = {}

def get_all_tests():
    return list(test_cases_db.values())

def create_test(data: TestCaseCreate) -> TestCase:
    test_id = str(uuid.uuid4())
    test_case = TestCase(id=test_id, **data.model_dump())
    test_cases_db[test_id] = test_case
    return test_case

def get_test(test_id: str) -> Optional[TestCase]:
    return test_cases_db.get(test_id)

def delete_test(test_id: str) -> bool:
    if test_id in test_cases_db:
        del test_cases_db[test_id]
        return True
    return False
