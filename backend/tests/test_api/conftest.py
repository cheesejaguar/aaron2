import os
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool
from sqlmodel import SQLModel

from app.api.deps import get_current_user, get_db
from app.main import app
from app.models import *  # noqa: F401, F403
from app.models.user import User

_TEST_DB_URL_ASYNC = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://aaron2:aaron2_dev_password@localhost:5432/aaron2",
)
_TEST_DB_URL_SYNC = _TEST_DB_URL_ASYNC.replace("+asyncpg", "")

test_engine = create_async_engine(_TEST_DB_URL_ASYNC, echo=False, poolclass=NullPool)


@pytest.fixture(scope="session", autouse=True)
def _create_tables():
    """Use synchronous engine for DDL to avoid event-loop conflicts."""
    sync_engine = create_engine(_TEST_DB_URL_SYNC, echo=False)
    SQLModel.metadata.drop_all(sync_engine)
    SQLModel.metadata.create_all(sync_engine)
    sync_engine.dispose()
    yield
    sync_engine = create_engine(_TEST_DB_URL_SYNC, echo=False)
    SQLModel.metadata.drop_all(sync_engine)
    sync_engine.dispose()


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    conn = await test_engine.connect()
    trans = await conn.begin()
    session = AsyncSession(bind=conn, join_transaction_mode="create_savepoint")
    yield session
    await session.close()
    await trans.rollback()
    await conn.close()


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    user = User(
        id=uuid4(),
        email=f"test-{uuid4().hex[:8]}@test.com",
        name="Test User",
        hashed_password="not-used",
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def second_user(db_session: AsyncSession) -> User:
    user = User(
        id=uuid4(),
        email=f"other-{uuid4().hex[:8]}@test.com",
        name="Other User",
        hashed_password="not-used",
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user


@pytest.fixture
def mock_redis():
    mock = AsyncMock()
    mock.ping = AsyncMock(return_value=True)
    mock.get = AsyncMock(return_value=None)
    mock.set = AsyncMock(return_value=True)
    mock.incr = AsyncMock(return_value=1)
    mock.expire = AsyncMock(return_value=True)
    mock.aclose = AsyncMock()
    return mock


@pytest_asyncio.fixture
async def client(
    db_session: AsyncSession, test_user: User, mock_redis
) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        yield db_session

    async def override_get_current_user():
        return test_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    with (
        patch("app.core.redis.get_redis", return_value=mock_redis),
        patch("app.core.redis._redis_client", mock_redis),
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as ac:
            yield ac

    app.dependency_overrides.clear()


