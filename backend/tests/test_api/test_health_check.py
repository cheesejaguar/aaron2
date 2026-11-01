import fakeredis
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool

from tests.conftest import test_engine


@pytest.fixture
def app_db_engine(monkeypatch):
    """Point the app's engine (used directly by the health check) at the test database."""
    monkeypatch.setattr("app.core.database.engine", test_engine)


class TestHealthCheck:
    @pytest.mark.asyncio
    async def test_all_ok(self, client: AsyncClient, app_db_engine):
        resp = await client.get("/api/v1/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok", "database": "ok", "redis": "ok"}

    @pytest.mark.asyncio
    async def test_redis_down_is_degraded(self, client: AsyncClient, app_db_engine, monkeypatch):
        server = fakeredis.FakeServer()
        server.connected = False
        down = fakeredis.FakeAsyncRedis(server=server)
        monkeypatch.setattr("app.core.redis._redis_client", down)

        resp = await client.get("/api/v1/health")

        assert resp.status_code == 200
        assert resp.json() == {"status": "degraded", "database": "ok", "redis": "error"}

    @pytest.mark.asyncio
    async def test_database_down_is_degraded(self, client: AsyncClient, monkeypatch):
        unreachable = create_async_engine(
            "postgresql+asyncpg://nobody:nothing@127.0.0.1:1/none", poolclass=NullPool
        )
        monkeypatch.setattr("app.core.database.engine", unreachable)

        resp = await client.get("/api/v1/health")

        assert resp.status_code == 200
        assert resp.json() == {"status": "degraded", "database": "error", "redis": "ok"}
