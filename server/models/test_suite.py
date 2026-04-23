import os
import aiosqlite
import json
from pydantic import BaseModel
from typing import List, Optional
import uuid

class TestSuiteCreate(BaseModel):
    name: str
    description: Optional[str] = None
    test_case_ids: List[str]

class TestSuite(TestSuiteCreate):
    id: str

DB_PATH = os.path.join("data", "app.db")

async def get_all_suites() -> List[TestSuite]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM test_suites") as cursor:
            rows = await cursor.fetchall()
            suites = []
            for row in rows:
                d = dict(row)
                d['test_case_ids'] = json.loads(d['test_case_ids'])
                suites.append(TestSuite(**d))
            return suites

async def check_suite_name_exists(name: str) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT 1 FROM test_suites WHERE name = ?", (name,)) as cursor:
            return await cursor.fetchone() is not None

async def create_suite(data: TestSuiteCreate) -> TestSuite:
    suite_id = str(uuid.uuid4())
    suite = TestSuite(id=suite_id, **data.model_dump())
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO test_suites (id, name, description, test_case_ids, queue) VALUES (?, ?, ?, ?, ?)",
            (suite.id, suite.name, suite.description, json.dumps(suite.test_case_ids), "[]")
        )
        await db.commit()
    return suite

async def get_suite(suite_id: str) -> Optional[TestSuite]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM test_suites WHERE id = ?", (suite_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                d = dict(row)
                d['test_case_ids'] = json.loads(d['test_case_ids'])
                return TestSuite(**d)
            return None

async def delete_suite(suite_id: str) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("DELETE FROM test_suites WHERE id = ?", (suite_id,))
        await db.commit()
        return cursor.rowcount > 0

async def enqueue_suite(suite_id: str, executed_by: str = "Auto"):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT queue FROM test_suites WHERE id = ?", (suite_id,)) as cursor:
            row = await cursor.fetchone()
            if not row:
                return False
            queue = json.loads(row['queue'])
            queue.append({"executed_by": executed_by})
            await db.execute("UPDATE test_suites SET queue = ? WHERE id = ?", (json.dumps(queue), suite_id))
            await db.commit()
            return True

async def dequeue_suite():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT id, queue FROM test_suites") as cursor:
            rows = await cursor.fetchall()
            for row in rows:
                queue = json.loads(row['queue'])
                if queue:
                    item = queue.pop(0)
                    await db.execute("UPDATE test_suites SET queue = ? WHERE id = ?", (json.dumps(queue), row['id']))
                    await db.commit()
                    return {"suite_id": row['id'], "executed_by": item['executed_by']}
            return None
