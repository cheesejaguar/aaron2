from datetime import date
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.meal_plan import MealPlan, MealPlanEntry
from app.models.pantry import PantryItem
from app.models.user import User


class TestListMealPlans:
    @pytest.mark.asyncio
    async def test_list_empty(self, client: AsyncClient):
        resp = await client.get("/api/v1/meal-plans/")
        assert resp.status_code == 200
        assert resp.json() == []

    @pytest.mark.asyncio
    async def test_list_with_plans(
        self, client: AsyncClient, db_session: AsyncSession, test_user: User
    ):
        plan = MealPlan(
            id=uuid4(),
            user_id=test_user.id,
            week_start_date=date(2025, 6, 16),
        )
        db_session.add(plan)
        await db_session.flush()

        entry = MealPlanEntry(
            id=uuid4(),
            meal_plan_id=plan.id,
            day_of_week=0,
            meal_type="breakfast",
            custom_meal_json={"name": "Oatmeal"},
        )
        db_session.add(entry)
        await db_session.flush()

        resp = await client.get("/api/v1/meal-plans/")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["week_start_date"] == "2025-06-16"
        assert len(data[0]["entries"]) == 1

    @pytest.mark.asyncio
    async def test_user_isolation(
        self, client: AsyncClient, db_session: AsyncSession, second_user: User
    ):
        plan = MealPlan(
            id=uuid4(),
            user_id=second_user.id,
            week_start_date=date(2025, 6, 16),
        )
        db_session.add(plan)
        await db_session.flush()

        resp = await client.get("/api/v1/meal-plans/")
        assert len(resp.json()) == 0


class TestCreateMealPlan:
    @pytest.mark.asyncio
    async def test_create_empty(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/meal-plans/",
            json={"week_start_date": "2025-06-16", "entries": []},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["week_start_date"] == "2025-06-16"
        assert data["entries"] == []

    @pytest.mark.asyncio
    async def test_create_with_entries(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/meal-plans/",
            json={
                "week_start_date": "2025-06-16",
                "entries": [
                    {
                        "day_of_week": 0,
                        "meal_type": "breakfast",
                        "custom_meal_json": {"name": "Oatmeal with berries"},
                    },
                    {
                        "day_of_week": 0,
                        "meal_type": "lunch",
                        "custom_meal_json": {"name": "Grilled chicken salad"},
                    },
                ],
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert len(data["entries"]) == 2

    @pytest.mark.asyncio
    async def test_create_missing_date(self, client: AsyncClient):
        resp = await client.post("/api/v1/meal-plans/", json={"entries": []})
        assert resp.status_code == 422


class TestSuggestMealPlan:
    @pytest.mark.asyncio
    async def test_suggest(
        self, client: AsyncClient, db_session: AsyncSession, test_user: User, openrouter
    ):
        db_session.add(PantryItem(user_id=test_user.id, name="Oats", quantity=1.0))
        await db_session.flush()
        oatmeal = {"name": "Oatmeal", "estimated_calories": 300, "estimated_sodium_mg": 5}
        salad = {"name": "Salad", "estimated_calories": 400, "estimated_sodium_mg": 300}
        openrouter.reply(
            {
                "entries": [
                    {"day_of_week": 0, "meal_type": "breakfast", "meal": oatmeal},
                    {"day_of_week": 2, "meal_type": "lunch", "meal": salad},
                ]
            }
        )

        resp = await client.post(
            "/api/v1/meal-plans/suggest",
            json={"week_start_date": "2025-06-16", "health_focus": "heart-healthy"},
        )

        assert resp.status_code == 201
        data = resp.json()
        assert data["week_start_date"] == "2025-06-16"
        entries = sorted(data["entries"], key=lambda e: e["day_of_week"])
        assert [(e["day_of_week"], e["meal_type"], e["custom_meal_json"]) for e in entries] == [
            (0, "breakfast", oatmeal),
            (2, "lunch", salad),
        ]
        prompt = openrouter.last_messages[1]["content"]
        assert "Available pantry items: Oats" in prompt
        assert "Health focus: heart-healthy" in prompt

    @pytest.mark.asyncio
    async def test_suggest_ai_unavailable_creates_empty_plan(self, client: AsyncClient, openrouter):
        openrouter.fail(500, times=3)

        resp = await client.post(
            "/api/v1/meal-plans/suggest",
            json={"week_start_date": "2025-06-16"},
        )

        assert resp.status_code == 201
        assert resp.json()["entries"] == []
