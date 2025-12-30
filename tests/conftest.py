import sys
from pathlib import Path
import os
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

# Add project root to Python path
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from backend import app
from db import init_db

@pytest.fixture(scope="session", autouse=True)
def test_db():
    os.environ["DB_PATH"] = "test.db"
    init_db()
    yield
    db_file = Path("test.db")
    if db_file.exists():
        db_file.unlink()

@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test"
    ) as ac:
        yield ac


