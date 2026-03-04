from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.food_log import FoodLog
from app.models.pantry import PantryItem
from app.models.user import User


@pytest.fixture
async def pantry_item(db_session: AsyncSession, test_user: User) -> PantryItem:
    item = PantryItem(
        id=uuid4(),
        user_id=test_user.id,
        name="Milk",
        category="dairy",
        quantity=2.0,
        unit="gallons",
    )
    db_session.add(item)
    await db_session.flush()
    await db_session.refresh(item)
    return item


class TestListPantry:
    @pytest.mark.asyncio
    async def test_list_empty(self, client: AsyncClient):
        resp = await client.get("/api/v1/pantry/")
        assert resp.status_code == 200
        assert resp.json() == []

    @pytest.mark.asyncio
    async def test_list_with_items(self, client: AsyncClient, pantry_item: PantryItem):
        resp = await client.get("/api/v1/pantry/")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["name"] == "Milk"

    @pytest.mark.asyncio
    async def test_list_user_isolation(
        self, client: AsyncClient, db_session: AsyncSession, second_user: User
    ):
        """Ensure users only see their own pantry items."""
        other_item = PantryItem(id=uuid4(), user_id=second_user.id, name="Other Milk", quantity=1.0)
        db_session.add(other_item)
        await db_session.flush()

        resp = await client.get("/api/v1/pantry/")
        assert resp.status_code == 200
        assert len(resp.json()) == 0



class TestCreatePantryItem:
    @pytest.mark.asyncio
    async def test_create_minimal(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/pantry/",
            json={"name": "Eggs", "quantity": 12.0},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Eggs"
        assert data["quantity"] == 12.0
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_full(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/pantry/",
            json={
                "name": "Chicken Breast",
                "category": "protein",
                "quantity": 3.0,
                "unit": "lbs",
                "low_stock_threshold": 1.0,
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["category"] == "protein"
        assert data["unit"] == "lbs"

    @pytest.mark.asyncio
    async def test_create_missing_name(self, client: AsyncClient):
        resp = await client.post("/api/v1/pantry/", json={"quantity": 1.0})
        assert resp.status_code == 422


class TestUpdatePantryItem:
    @pytest.mark.asyncio
    async def test_update_success(self, client: AsyncClient, pantry_item: PantryItem):
        resp = await client.put(
            f"/api/v1/pantry/{pantry_item.id}",
            json={"name": "Oat Milk", "quantity": 3.0},
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "Oat Milk"
        assert resp.json()["quantity"] == 3.0

    @pytest.mark.asyncio
    async def test_update_partial(self, client: AsyncClient, pantry_item: PantryItem):
        resp = await client.put(
            f"/api/v1/pantry/{pantry_item.id}",
            json={"quantity": 5.0},
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "Milk"  # unchanged
        assert resp.json()["quantity"] == 5.0

    @pytest.mark.asyncio
    async def test_update_not_found(self, client: AsyncClient):
        resp = await client.put(
            f"/api/v1/pantry/{uuid4()}",
            json={"name": "Ghost"},
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_update_other_user_item(
        self, client: AsyncClient, db_session: AsyncSession, second_user: User
    ):
        other = PantryItem(id=uuid4(), user_id=second_user.id, name="Other", quantity=1.0)
        db_session.add(other)
        await db_session.flush()

        resp = await client.put(f"/api/v1/pantry/{other.id}", json={"name": "Hacked"})
        assert resp.status_code == 404


class TestDeletePantryItem:
    @pytest.mark.asyncio
    async def test_delete_success(self, client: AsyncClient, pantry_item: PantryItem):
        resp = await client.delete(f"/api/v1/pantry/{pantry_item.id}")
        assert resp.status_code == 200

        # Verify it's gone
        resp = await client.get("/api/v1/pantry/")
        assert len(resp.json()) == 0

    @pytest.mark.asyncio
    async def test_delete_not_found(self, client: AsyncClient):
        resp = await client.delete(f"/api/v1/pantry/{uuid4()}")
        assert resp.status_code == 404


class TestConsumePantryItem:
    @pytest.mark.asyncio
    async def test_consume_success(self, client: AsyncClient, pantry_item: PantryItem):
        resp = await client.post(
            f"/api/v1/pantry/{pantry_item.id}/consume",
            json={"quantity": 1.0},
        )
        assert resp.status_code == 200
        assert resp.json()["quantity"] == 1.0

    @pytest.mark.asyncio
    async def test_consume_to_zero(self, client: AsyncClient, pantry_item: PantryItem):
        resp = await client.post(
            f"/api/v1/pantry/{pantry_item.id}/consume",
            json={"quantity": 100.0},
        )
        assert resp.status_code == 200
        assert resp.json()["quantity"] == 0.0

    @pytest.mark.asyncio
    async def test_consume_creates_food_log(
        self, client: AsyncClient, db_session: AsyncSession, test_user: User
    ):
        item = PantryItem(
            id=uuid4(),
            user_id=test_user.id,
            name="Banana",
            quantity=5.0,
            unit="pieces",
            nutrition_json={"calories": 105, "protein_g": 1.3, "carbs_g": 27, "fat_g": 0.4},
        )
        db_session.add(item)
        await db_session.flush()

        resp = await client.post(
            f"/api/v1/pantry/{item.id}/consume",
            json={"quantity": 2.0, "meal_type": "breakfast"},
        )
        assert resp.status_code == 200

        result = await db_session.execute(
            select(FoodLog).where(FoodLog.user_id == test_user.id, FoodLog.food_name == "Banana")
        )
        log = result.scalar_one()
        assert log.meal_type == "breakfast"
        assert log.quantity == 2.0
        assert log.unit == "pieces"
        assert log.calories is not None
        assert log.calories > 0

    @pytest.mark.asyncio
    async def test_consume_default_meal_type(
        self, client: AsyncClient, db_session: AsyncSession, test_user: User
    ):
        item = PantryItem(
            id=uuid4(),
            user_id=test_user.id,
            name="Apple",
            quantity=3.0,
        )
        db_session.add(item)
        await db_session.flush()

        resp = await client.post(
            f"/api/v1/pantry/{item.id}/consume",
            json={"quantity": 1.0},
        )
        assert resp.status_code == 200

        result = await db_session.execute(
            select(FoodLog).where(FoodLog.user_id == test_user.id, FoodLog.food_name == "Apple")
        )
        log = result.scalar_one()
        assert log.meal_type == "snack"

    @pytest.mark.asyncio
    async def test_consume_without_nutrition(
        self, client: AsyncClient, db_session: AsyncSession, test_user: User
    ):
        item = PantryItem(
            id=uuid4(),
            user_id=test_user.id,
            name="Mystery Food",
            quantity=10.0,
        )
        db_session.add(item)
        await db_session.flush()

        resp = await client.post(
            f"/api/v1/pantry/{item.id}/consume",
            json={"quantity": 1.0},
        )
        assert resp.status_code == 200

        result = await db_session.execute(
            select(FoodLog).where(
                FoodLog.user_id == test_user.id, FoodLog.food_name == "Mystery Food"
            )
        )
        log = result.scalar_one()
        assert log.calories is None

    @pytest.mark.asyncio
    async def test_consume_not_found(self, client: AsyncClient):
        resp = await client.post(
            f"/api/v1/pantry/{uuid4()}/consume",
            json={"quantity": 1.0},
        )
        assert resp.status_code == 404
