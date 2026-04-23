import os
import aiosqlite
from pydantic import BaseModel
from typing import Optional, List
import uuid

class TestCaseCreate(BaseModel):
    name: str
    utterance: str
    audio_url: str
    description: Optional[str] = None

class TestCase(TestCaseCreate):
    id: str

DB_PATH = os.path.join("data", "app.db")

async def get_all_tests() -> List[TestCase]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM test_cases") as cursor:
            rows = await cursor.fetchall()
            return [TestCase(**dict(row)) for row in rows]

async def create_test(data: TestCaseCreate) -> TestCase:
    test_id = str(uuid.uuid4())
    test_case = TestCase(id=test_id, **data.model_dump())
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO test_cases (id, name, utterance, audio_url, description) VALUES (?, ?, ?, ?, ?)",
            (test_case.id, test_case.name, test_case.utterance, test_case.audio_url, test_case.description)
        )
        await db.commit()
    return test_case

async def get_test(test_id: str) -> Optional[TestCase]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM test_cases WHERE id = ?", (test_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return TestCase(**dict(row))
            return None

async def delete_test(test_id: str) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("DELETE FROM test_cases WHERE id = ?", (test_id,))
        await db.commit()
        return cursor.rowcount > 0
