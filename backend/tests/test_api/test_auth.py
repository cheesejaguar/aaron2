import pytest
from httpx import AsyncClient


class TestGetMe:
    @pytest.mark.asyncio
    async def test_get_me(self, client: AsyncClient, test_user):
        resp = await client.get("/api/v1/auth/me")
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == test_user.email
        assert data["name"] == test_user.name
        assert "hashed_password" not in data


class TestUpdateSettings:
    @pytest.mark.asyncio
    async def test_update_name(self, client: AsyncClient, test_user):
        resp = await client.patch(
            "/api/v1/auth/settings",
            json={"name": "Updated Name"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Updated Name"
        assert data["email"] == test_user.email

    @pytest.mark.asyncio
    async def test_update_health_goals(self, client: AsyncClient):
        goals = {"target_calories": 2000, "diet_type": "DASH"}
        resp = await client.patch(
            "/api/v1/auth/settings",
            json={"health_goals_json": goals},
        )
        assert resp.status_code == 200
        assert resp.json()["health_goals_json"] == goals

    @pytest.mark.asyncio
    async def test_update_both(self, client: AsyncClient):
        resp = await client.patch(
            "/api/v1/auth/settings",
            json={"name": "New Name", "health_goals_json": {"goal": "lose_weight"}},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "New Name"
        assert data["health_goals_json"]["goal"] == "lose_weight"

    @pytest.mark.asyncio
    async def test_update_empty_body(self, client: AsyncClient, test_user):
        resp = await client.patch("/api/v1/auth/settings", json={})
        assert resp.status_code == 200
        assert resp.json()["name"] == test_user.name
