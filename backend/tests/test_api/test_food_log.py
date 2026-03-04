from datetime import datetime
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.food_log import FoodLog
from app.models.user import User


class TestCreateFoodLog:
    @pytest.mark.asyncio
    async def test_create_minimal(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/food-log/",
            json={"meal_type": "lunch", "food_name": "Salad"},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["food_name"] == "Salad"
        assert data["meal_type"] == "lunch"

    @pytest.mark.asyncio
    async def test_create_full(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/food-log/",
            json={
                "meal_type": "dinner",
                "food_name": "Grilled Salmon",
                "quantity": 6.0,
                "unit": "oz",
                "calories": 350,
                "protein_g": 40.0,
                "fat_g": 18.0,
                "carbs_g": 0.0,
                "fiber_g": 0.0,
                "sodium_mg": 75.0,
                "potassium_mg": 550.0,
                "cholesterol_mg": 85.0,
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["calories"] == 350
        assert data["protein_g"] == 40.0

    @pytest.mark.asyncio
    async def test_create_missing_required(self, client: AsyncClient):
        resp = await client.post("/api/v1/food-log/", json={"meal_type": "lunch"})
        assert resp.status_code == 422


class TestListFoodLogs:
    @pytest.mark.asyncio
    async def test_list_empty(self, client: AsyncClient):
        resp = await client.get("/api/v1/food-log/")
        assert resp.status_code == 200
        assert resp.json() == []

    @pytest.mark.asyncio
    async def test_list_all(self, client: AsyncClient):
        await client.post(
            "/api/v1/food-log/",
            json={"meal_type": "breakfast", "food_name": "Eggs"},
        )
        await client.post(
            "/api/v1/food-log/",
            json={"meal_type": "lunch", "food_name": "Soup"},
        )

        resp = await client.get("/api/v1/food-log/")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    @pytest.mark.asyncio
    async def test_list_filter_by_date(
        self, client: AsyncClient, db_session: AsyncSession, test_user: User
    ):
        target_date = datetime(
            2025,
            6,
            15,
            12,
            0,
        )
        other_date = datetime(
            2025,
            6,
            16,
            12,
            0,
        )

        db_session.add(
            FoodLog(
                id=uuid4(),
                user_id=test_user.id,
                meal_type="lunch",
                food_name="Salad",
                logged_at=target_date,
            )
        )
        db_session.add(
            FoodLog(
                id=uuid4(),
                user_id=test_user.id,
                meal_type="dinner",
                food_name="Pizza",
                logged_at=other_date,
            )
        )
        await db_session.flush()

        resp = await client.get("/api/v1/food-log/", params={"date": "2025-06-15"})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["food_name"] == "Salad"

    @pytest.mark.asyncio
    async def test_list_filter_end_of_month(
        self, client: AsyncClient, db_session: AsyncSession, test_user: User
    ):
        """Regression test: date filtering must work on day 31."""
        jan31 = datetime(
            2025,
            1,
            31,
            10,
            0,
        )
        db_session.add(
            FoodLog(
                id=uuid4(),
                user_id=test_user.id,
                meal_type="lunch",
                food_name="Toast",
                logged_at=jan31,
            )
        )
        await db_session.flush()

        resp = await client.get("/api/v1/food-log/", params={"date": "2025-01-31"})
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    @pytest.mark.asyncio
    async def test_user_isolation(
        self, client: AsyncClient, db_session: AsyncSession, second_user: User
    ):
        db_session.add(
            FoodLog(
                id=uuid4(),
                user_id=second_user.id,
                meal_type="lunch",
                food_name="Hidden",
                logged_at=datetime.utcnow(),
            )
        )
        await db_session.flush()

        resp = await client.get("/api/v1/food-log/")
        assert len(resp.json()) == 0


class TestDailySummary:
    @pytest.mark.asyncio
    async def test_summary_empty_day(self, client: AsyncClient):
        resp = await client.get("/api/v1/food-log/daily-summary", params={"date": "2025-06-15"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_calories"] == 0
        assert data["meal_count"] == 0

    @pytest.mark.asyncio
    async def test_summary_with_data(
        self, client: AsyncClient, db_session: AsyncSession, test_user: User
    ):
        target = datetime(
            2025,
            6,
            15,
            12,
            0,
        )
        db_session.add(
            FoodLog(
                id=uuid4(),
                user_id=test_user.id,
                meal_type="lunch",
                food_name="Salad",
                calories=300,
                protein_g=20.0,
                carbs_g=30.0,
                fat_g=10.0,
                logged_at=target,
            )
        )
        db_session.add(
            FoodLog(
                id=uuid4(),
                user_id=test_user.id,
                meal_type="dinner",
                food_name="Chicken",
                calories=500,
                protein_g=45.0,
                carbs_g=10.0,
                fat_g=20.0,
                logged_at=target,
            )
        )
        await db_session.flush()

        resp = await client.get("/api/v1/food-log/daily-summary", params={"date": "2025-06-15"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_calories"] == 800
        assert data["total_protein_g"] == 65.0
        assert data["meal_count"] == 2
