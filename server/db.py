import aiosqlite
import os

DB_PATH = os.path.join("data", "app.db")

async def get_db():
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    try:
        yield db
    finally:
        await db.close()

async def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS test_cases (
                id TEXT PRIMARY KEY,
                name TEXT,
                utterance TEXT,
                audio_url TEXT,
                description TEXT
            )
        ''')
        
        await db.execute('''
            CREATE TABLE IF NOT EXISTS test_suites (
                id TEXT PRIMARY KEY,
                name TEXT,
                description TEXT,
                test_case_ids TEXT,
                queue TEXT
            )
        ''')
        
        await db.execute('''
            CREATE TABLE IF NOT EXISTS test_runs (
                id TEXT PRIMARY KEY,
                test_id TEXT,
                suite_id TEXT,
                status TEXT,
                video_filename TEXT,
                executed_by TEXT,
                timestamp REAL,
                verified BOOLEAN,
                pass_lng BOOLEAN,
                pass_asr BOOLEAN,
                pass_capsule BOOLEAN,
                pass_tts BOOLEAN,
                pass_nlg BOOLEAN,
                reason TEXT,
                result_utterance TEXT,
                result_asr TEXT,
                result_capsule TEXT,
                result_tts TEXT,
                result_nlg TEXT
            )
        ''')
        await db.commit()
