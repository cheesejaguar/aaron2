from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.pantry import PantryItem
from app.models.recipe import Recipe
from app.models.shopping import ShoppingList
from app.models.user import User


@pytest.fixture
async def recipe(db_session: AsyncSession, test_user: User) -> Recipe:
    r = Recipe(
        id=uuid4(),
        user_id=test_user.id,
        title="Grilled Salmon",
        description="Simple healthy salmon",
        ingredients_json=[{"name": "salmon", "amount": "6 oz"}],
        steps_json=["Season salmon", "Grill 4 min each side"],
        health_tags=["heart-healthy", "high-protein"],
        is_ai_generated=False,
    )
    db_session.add(r)
    await db_session.flush()
    await db_session.refresh(r)
    return r


class TestListRecipes:
    @pytest.mark.asyncio
    async def test_list_empty(self, client: AsyncClient):
        resp = await client.get("/api/v1/recipes/")
        assert resp.status_code == 200
        assert resp.json() == []

    @pytest.mark.asyncio
    async def test_list_with_recipes(self, client: AsyncClient, recipe: Recipe):
        resp = await client.get("/api/v1/recipes/")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["title"] == "Grilled Salmon"

    @pytest.mark.asyncio
    async def test_user_isolation(
        self, client: AsyncClient, db_session: AsyncSession, second_user: User
    ):
        db_session.add(
            Recipe(
                id=uuid4(),
                user_id=second_user.id,
                title="Secret Recipe",
                is_ai_generated=False,
            )
        )
        await db_session.flush()

        resp = await client.get("/api/v1/recipes/")
        assert len(resp.json()) == 0


class TestCreateRecipe:
    @pytest.mark.asyncio
    async def test_create_minimal(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/recipes/",
            json={"title": "Toast"},
        )
        assert resp.status_code == 201
        assert resp.json()["title"] == "Toast"
        assert resp.json()["is_ai_generated"] is False

    @pytest.mark.asyncio
    async def test_create_full(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/recipes/",
            json={
                "title": "DASH Chicken Stir-Fry",
                "description": "Low-sodium stir fry",
                "ingredients_json": [
                    {"name": "chicken breast", "amount": "1 lb"},
                    {"name": "broccoli", "amount": "2 cups"},
                ],
                "steps_json": ["Cut chicken", "Stir-fry 8 min"],
                "health_tags": ["low-sodium", "high-protein"],
                "is_ai_generated": False,
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert len(data["ingredients_json"]) == 2
        assert "low-sodium" in data["health_tags"]


class TestGetRecipe:
    @pytest.mark.asyncio
    async def test_get_existing(self, client: AsyncClient, recipe: Recipe):
        resp = await client.get(f"/api/v1/recipes/{recipe.id}")
        assert resp.status_code == 200
        assert resp.json()["title"] == "Grilled Salmon"

    @pytest.mark.asyncio
    async def test_get_not_found(self, client: AsyncClient):
        resp = await client.get(f"/api/v1/recipes/{uuid4()}")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_get_other_user_recipe(
        self, client: AsyncClient, db_session: AsyncSession, second_user: User
    ):
        other_recipe = Recipe(
            id=uuid4(),
            user_id=second_user.id,
            title="Private",
            is_ai_generated=False,
        )
        db_session.add(other_recipe)
        await db_session.flush()

        resp = await client.get(f"/api/v1/recipes/{other_recipe.id}")
        assert resp.status_code == 404


class TestGenerateRecipe:
    @pytest.mark.asyncio
    async def test_generate_recipe(self, client: AsyncClient, test_user: User):
        mock_recipe = Recipe(
            id=uuid4(),
            user_id=test_user.id,
            title="AI Healthy Bowl",
            is_ai_generated=True,
        )
        with patch(
            "app.api.v1.recipes.generate_recipe",
            new_callable=AsyncMock,
            return_value=mock_recipe,
        ):
            resp = await client.post(
                "/api/v1/recipes/generate",
                json={"health_focus": "heart-healthy", "cuisine": "Mediterranean"},
            )
            assert resp.status_code == 201
            assert resp.json()["is_ai_generated"] is True


class TestImportRecipe:
    @pytest.mark.asyncio
    async def test_import_url(self, client: AsyncClient, test_user: User):
        mock_recipe = Recipe(
            id=uuid4(),
            user_id=test_user.id,
            title="Imported Recipe",
            source_url="https://example.com/recipe",
            is_ai_generated=False,
        )
        with patch(
            "app.api.v1.recipes.import_recipe_from_url",
            new_callable=AsyncMock,
            return_value=mock_recipe,
        ):
            resp = await client.post(
                "/api/v1/recipes/import-url",
                json={"url": "https://example.com/recipe"},
            )
            assert resp.status_code == 201
            assert resp.json()["source_url"] == "https://example.com/recipe"


class TestAddToShoppingList:
    @pytest.mark.asyncio
    async def test_add_missing_ingredients(
        self, client: AsyncClient, db_session: AsyncSession, test_user: User
    ):
        recipe = Recipe(
            id=uuid4(),
            user_id=test_user.id,
            title="Test Recipe",
            ingredients_json=[
                {"name": "Chicken", "quantity": 1, "unit": "lb"},
                {"name": "Rice", "quantity": 2, "unit": "cups"},
                {"name": "Broccoli", "quantity": 1, "unit": "head"},
            ],
            is_ai_generated=False,
        )
        # Add only "chicken" to pantry (should NOT appear in shopping list)
        pantry = PantryItem(id=uuid4(), user_id=test_user.id, name="Chicken", quantity=2.0)
        db_session.add(recipe)
        db_session.add(pantry)
        await db_session.flush()

        resp = await client.post(f"/api/v1/recipes/{recipe.id}/add-to-shopping-list")
        assert resp.status_code == 200
        assert "2 ingredients" in resp.json()["message"]

    @pytest.mark.asyncio
    async def test_all_ingredients_in_pantry(
        self, client: AsyncClient, db_session: AsyncSession, test_user: User
    ):
        recipe = Recipe(
            id=uuid4(),
            user_id=test_user.id,
            title="Simple Recipe",
            ingredients_json=[{"name": "Eggs"}],
            is_ai_generated=False,
        )
        pantry = PantryItem(id=uuid4(), user_id=test_user.id, name="Eggs", quantity=12.0)
        db_session.add(recipe)
        db_session.add(pantry)
        await db_session.flush()

        resp = await client.post(f"/api/v1/recipes/{recipe.id}/add-to-shopping-list")
        assert resp.status_code == 200
        assert "already in pantry" in resp.json()["message"]

    @pytest.mark.asyncio
    async def test_creates_shopping_list_if_none(
        self, client: AsyncClient, db_session: AsyncSession, test_user: User
    ):
        recipe = Recipe(
            id=uuid4(),
            user_id=test_user.id,
            title="New List Recipe",
            ingredients_json=[{"name": "Tofu", "quantity": 1}],
            is_ai_generated=False,
        )
        db_session.add(recipe)
        await db_session.flush()

        resp = await client.post(f"/api/v1/recipes/{recipe.id}/add-to-shopping-list")
        assert resp.status_code == 200
        assert "1 ingredients" in resp.json()["message"]

    @pytest.mark.asyncio
    async def test_uses_existing_active_list(
        self, client: AsyncClient, db_session: AsyncSession, test_user: User
    ):
        shopping_list = ShoppingList(
            id=uuid4(), user_id=test_user.id, name="My List", status="active"
        )
        recipe = Recipe(
            id=uuid4(),
            user_id=test_user.id,
            title="Existing List Recipe",
            ingredients_json=[{"name": "Avocado"}],
            is_ai_generated=False,
        )
        db_session.add(shopping_list)
        db_session.add(recipe)
        await db_session.flush()

        resp = await client.post(f"/api/v1/recipes/{recipe.id}/add-to-shopping-list")
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_recipe_not_found(self, client: AsyncClient):
        resp = await client.post(f"/api/v1/recipes/{uuid4()}/add-to-shopping-list")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_other_user_recipe(
        self, client: AsyncClient, db_session: AsyncSession, second_user: User
    ):
        recipe = Recipe(
            id=uuid4(),
            user_id=second_user.id,
            title="Private Recipe",
            ingredients_json=[{"name": "Secret"}],
            is_ai_generated=False,
        )
        db_session.add(recipe)
        await db_session.flush()

        resp = await client.post(f"/api/v1/recipes/{recipe.id}/add-to-shopping-list")
        assert resp.status_code == 404
