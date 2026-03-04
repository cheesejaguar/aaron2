from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.shopping import ShoppingList, ShoppingListItem
from app.models.user import User


@pytest.fixture
async def shopping_list(db_session: AsyncSession, test_user: User) -> ShoppingList:
    sl = ShoppingList(id=uuid4(), user_id=test_user.id, name="Weekly Groceries", status="active")
    db_session.add(sl)
    await db_session.flush()

    items = [
        ShoppingListItem(id=uuid4(), shopping_list_id=sl.id, name="Milk", is_checked=False),
        ShoppingListItem(id=uuid4(), shopping_list_id=sl.id, name="Eggs", is_checked=True),
    ]
    for item in items:
        db_session.add(item)
    await db_session.flush()
    await db_session.refresh(sl)
    return sl


class TestListShoppingLists:
    @pytest.mark.asyncio
    async def test_list_empty(self, client: AsyncClient):
        resp = await client.get("/api/v1/shopping-lists/")
        assert resp.status_code == 200
        assert resp.json() == []

    @pytest.mark.asyncio
    async def test_list_with_data(self, client: AsyncClient, shopping_list):
        resp = await client.get("/api/v1/shopping-lists/")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["name"] == "Weekly Groceries"
        assert len(data[0]["items"]) == 2

    @pytest.mark.asyncio
    async def test_user_isolation(
        self, client: AsyncClient, db_session: AsyncSession, second_user: User
    ):
        other = ShoppingList(id=uuid4(), user_id=second_user.id, name="Other List", status="active")
        db_session.add(other)
        await db_session.flush()

        resp = await client.get("/api/v1/shopping-lists/")
        assert len(resp.json()) == 0


class TestCreateShoppingList:
    @pytest.mark.asyncio
    async def test_create_empty_list(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/shopping-lists/",
            json={"name": "New List"},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "New List"
        assert data["status"] == "active"
        assert data["items"] == []

    @pytest.mark.asyncio
    async def test_create_with_items(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/shopping-lists/",
            json={
                "name": "Dinner Party",
                "items": [
                    {"name": "Wine", "quantity": 2.0, "unit": "bottles"},
                    {"name": "Cheese", "category": "dairy"},
                ],
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert len(data["items"]) == 2
        names = {i["name"] for i in data["items"]}
        assert "Wine" in names
        assert "Cheese" in names


class TestAmazonCartUrl:
    @pytest.mark.asyncio
    async def test_get_url(self, client: AsyncClient, shopping_list):
        resp = await client.get(f"/api/v1/shopping-lists/{shopping_list.id}/amazon-cart-url")
        assert resp.status_code == 200
        url = resp.json()["url"]
        assert "amazon.com" in url
        assert "Milk" in url  # unchecked item

    @pytest.mark.asyncio
    async def test_not_found(self, client: AsyncClient):
        resp = await client.get(f"/api/v1/shopping-lists/{uuid4()}/amazon-cart-url")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_other_user_list(
        self, client: AsyncClient, db_session: AsyncSession, second_user: User
    ):
        other = ShoppingList(id=uuid4(), user_id=second_user.id, name="Other", status="active")
        db_session.add(other)
        await db_session.flush()

        resp = await client.get(f"/api/v1/shopping-lists/{other.id}/amazon-cart-url")
        assert resp.status_code == 404


class TestReplenish:
    @pytest.mark.asyncio
    async def test_replenish_not_found(self, client: AsyncClient):
        resp = await client.post(f"/api/v1/shopping-lists/{uuid4()}/replenish")
        assert resp.status_code == 404
