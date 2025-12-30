import os
import pytest
from httpx import AsyncClient
from backend import app
from db import init_db

@pytest.fixture(scope="session", autouse=True)
def test_db():
    os.environ["DB_PATH"] = "test.db"
    init_db()
    yield
    os.remove("test.db")


@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
