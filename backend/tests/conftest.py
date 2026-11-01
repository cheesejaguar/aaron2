"""Shared test fixtures.

Tests run against a real Postgres database (``TEST_DATABASE_URL``); each test runs
inside a transaction that is rolled back afterwards. Redis is replaced with an
in-memory ``fakeredis`` server. The only thing faked at the HTTP level is the
external OpenRouter API (see ``openrouter``).
"""

import importlib
import json
import os
from collections.abc import AsyncGenerator
from typing import Any
from uuid import uuid4

import fakeredis
import openai
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool
from sqlmodel import SQLModel
from tenacity import wait_none

from app.api.deps import DEFAULT_USER_EMAIL, get_db
from app.main import app
from app.models import *  # noqa: F401, F403
from app.models.user import User
from app.services.ai_service import AIService, ai_service

_TEST_DB_URL_ASYNC = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://aaron2:aaron2_dev_password@localhost:5432/aaron2",
)
# Name the sync driver explicitly: SQLAlchemy 2.1 defaults "postgresql://" to psycopg 3,
# but CI installs psycopg2.
_TEST_DB_URL_SYNC = _TEST_DB_URL_ASYNC.replace("+asyncpg", "+psycopg2")

test_engine = create_async_engine(_TEST_DB_URL_ASYNC, echo=False, poolclass=NullPool)


@pytest.fixture(scope="session")
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
async def db_session(_create_tables) -> AsyncGenerator[AsyncSession, None]:
    conn = await test_engine.connect()
    trans = await conn.begin()
    session = AsyncSession(bind=conn, join_transaction_mode="create_savepoint")
    yield session
    await session.close()
    await trans.rollback()
    await conn.close()


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    """The app's single default user, resolved by the real ``get_current_user``."""
    user = User(
        id=uuid4(),
        email=DEFAULT_USER_EMAIL,
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
def redis(monkeypatch):
    """An in-memory Redis installed as the app's shared client."""
    fake = fakeredis.FakeAsyncRedis(decode_responses=True)
    monkeypatch.setattr("app.core.redis._redis_client", fake)
    return fake


def chat_completion(content: str, prompt_tokens: int = 10, completion_tokens: int = 20) -> dict:
    """An OpenAI-compatible chat completion response body, as OpenRouter returns it."""
    return {
        "id": "gen-test",
        "object": "chat.completion",
        "created": 1700000000,
        "model": "test-model",
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
        },
    }


class FakeOpenRouter:
    """Stands in for the OpenRouter HTTP API behind the real OpenAI SDK client.

    Queue responses with ``reply``/``fail``; every request the SDK sends is recorded
    in ``requests`` (decoded JSON body plus URL and headers).
    """

    def __init__(self) -> None:
        self.requests: list[dict[str, Any]] = []
        self._responses: list[tuple[int, dict]] = []

    def reply(self, content: str | dict | list, **usage: int) -> "FakeOpenRouter":
        if not isinstance(content, str):
            content = json.dumps(content)
        self._responses.append((200, chat_completion(content, **usage)))
        return self

    def fail(self, status: int = 500, times: int = 1) -> "FakeOpenRouter":
        for _ in range(times):
            self._responses.append((status, {"error": {"message": "upstream error"}}))
        return self

    def handle(self, request):
        self.requests.append(
            {
                "url": str(request.url),
                "headers": dict(request.headers),
                "json": json.loads(request.content),
            }
        )
        if not self._responses:
            raise AssertionError("Unexpected OpenRouter request (no response queued)")
        status, body = self._responses.pop(0)
        return self._http.Response(status, json=body)

    @property
    def last_messages(self) -> list[dict]:
        return self.requests[-1]["json"]["messages"]


def _openai_http_module():
    """openai<3 is built on httpx, openai>=3 on httpx2; return the one the SDK uses."""
    base = openai.DefaultAsyncHttpxClient.__mro__[1]
    return importlib.import_module(base.__module__.split(".")[0])


@pytest.fixture
def openrouter(monkeypatch, redis) -> FakeOpenRouter:
    """Route the shared ``ai_service`` client to a FakeOpenRouter via a mock transport."""
    fake = FakeOpenRouter()
    http = _openai_http_module()
    fake._http = http  # type: ignore[attr-defined]
    client = ai_service.client.with_options(
        http_client=http.AsyncClient(transport=http.MockTransport(fake.handle)),
        max_retries=0,
    )
    monkeypatch.setattr(ai_service, "client", client)
    # Keep tenacity's retry count but skip its exponential back-off sleeps.
    monkeypatch.setattr(AIService._completion.retry, "wait", wait_none())  # type: ignore[attr-defined]
    return fake


@pytest_asyncio.fixture
async def client(
    db_session: AsyncSession, test_user: User, redis
) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
