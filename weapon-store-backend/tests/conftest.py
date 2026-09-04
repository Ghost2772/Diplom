import asyncio

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

import app.models  # noqa: F401
from app.core.database import Base, get_db
from app.main import app


@pytest.fixture
def api_client(tmp_path):
    database_url = f"sqlite+aiosqlite:///{tmp_path / 'test.db'}"
    engine = create_async_engine(database_url)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async def create_schema() -> None:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

    async def override_get_db():
        async with session_factory() as session:
            yield session

    asyncio.run(create_schema())
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client, session_factory

    app.dependency_overrides.clear()
    asyncio.run(engine.dispose())
