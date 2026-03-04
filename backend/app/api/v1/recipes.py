from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.api.deps import get_current_user, get_db
from app.models.pantry import PantryItem
from app.models.recipe import Recipe
from app.models.shopping import ShoppingList, ShoppingListItem
from app.models.user import User
from app.schemas.common import MessageResponse
from app.schemas.recipe import RecipeCreate, RecipeGenerateRequest, RecipeImportRequest, RecipeRead
from app.services.recipe_service import generate_recipe, import_recipe_from_url

router = APIRouter(prefix="/recipes", tags=["recipes"])


@router.get("/", response_model=list[RecipeRead])
async def list_recipes(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all recipes for the current user."""
    result = await db.execute(select(Recipe).where(Recipe.user_id == current_user.id))
    return result.scalars().all()


@router.post("/", response_model=RecipeRead, status_code=201)
async def create_recipe(
    data: RecipeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new recipe manually."""
    recipe = Recipe(**data.model_dump(), user_id=current_user.id)
    db.add(recipe)
    await db.flush()
    await db.refresh(recipe)
    return recipe


@router.get("/{recipe_id}", response_model=RecipeRead)
async def get_recipe(
    recipe_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific recipe by ID."""
    from uuid import UUID

    result = await db.execute(
        select(Recipe).where(Recipe.id == UUID(recipe_id), Recipe.user_id == current_user.id)
    )
    recipe = result.scalar_one_or_none()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe


@router.post("/generate", response_model=RecipeRead, status_code=201)
async def generate_recipe_endpoint(
    data: RecipeGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate a DASH-diet recipe using AI."""
    return await generate_recipe(db, current_user, data)


@router.post("/import-url", response_model=RecipeRead, status_code=201)
async def import_recipe_endpoint(
    data: RecipeImportRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Import a recipe from a URL using AI extraction."""
    return await import_recipe_from_url(db, current_user, data.url)


@router.post("/{recipe_id}/add-to-shopping-list", response_model=MessageResponse)
async def add_recipe_to_shopping_list(
    recipe_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add missing recipe ingredients to the active shopping list."""
    result = await db.execute(
        select(Recipe).where(Recipe.id == recipe_id, Recipe.user_id == current_user.id)
    )
    recipe = result.scalar_one_or_none()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    # Get pantry item names for comparison
    pantry_result = await db.execute(
        select(PantryItem.name).where(PantryItem.user_id == current_user.id)
    )
    pantry_names = {name.lower() for name in pantry_result.scalars().all()}

    # Find missing ingredients
    ingredients = recipe.ingredients_json or []
    missing = [ing for ing in ingredients if ing.get("name", "").lower() not in pantry_names]

    if not missing:
        return MessageResponse(message="All ingredients already in pantry")

    # Find or create active shopping list
    list_result = await db.execute(
        select(ShoppingList).where(
            ShoppingList.user_id == current_user.id,
            ShoppingList.status == "active",
        )
    )
    shopping_list = list_result.scalar_one_or_none()

    if not shopping_list:
        shopping_list = ShoppingList(
            user_id=current_user.id,
            name="Recipe Ingredients",
            status="active",
        )
        db.add(shopping_list)
        await db.flush()

    # Add missing ingredients
    for ing in missing:
        item = ShoppingListItem(
            shopping_list_id=shopping_list.id,
            name=ing.get("name", "Unknown"),
            quantity=ing.get("quantity"),
            unit=ing.get("unit"),
            is_ai_suggested=True,
        )
        db.add(item)

    await db.flush()
    return MessageResponse(message=f"Added {len(missing)} ingredients to shopping list")
