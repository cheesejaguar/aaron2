from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.api.deps import get_current_user, get_db
from app.models.food_log import FoodLog
from app.models.pantry import PantryItem
from app.models.user import User
from app.schemas.common import MessageResponse
from app.schemas.pantry import (
    PantryConsumeRequest,
    PantryItemCreate,
    PantryItemRead,
    PantryItemUpdate,
)

router = APIRouter(prefix="/pantry", tags=["pantry"])


@router.get("/", response_model=list[PantryItemRead])
async def list_pantry(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all pantry items for the current user."""
    result = await db.execute(select(PantryItem).where(PantryItem.user_id == current_user.id))
    return result.scalars().all()


@router.post("/", response_model=PantryItemRead, status_code=201)
async def create_pantry_item(
    data: PantryItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a new item to the pantry."""
    item = PantryItem(**data.model_dump(), user_id=current_user.id)
    db.add(item)
    await db.flush()
    await db.refresh(item)
    return item


@router.put("/{item_id}", response_model=PantryItemRead)
async def update_pantry_item(
    item_id: UUID,
    data: PantryItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an existing pantry item's details."""
    result = await db.execute(
        select(PantryItem).where(PantryItem.id == item_id, PantryItem.user_id == current_user.id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Pantry item not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(item, key, value)

    await db.flush()
    await db.refresh(item)
    return item


@router.delete("/{item_id}", response_model=MessageResponse)
async def delete_pantry_item(
    item_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a pantry item."""
    result = await db.execute(
        select(PantryItem).where(PantryItem.id == item_id, PantryItem.user_id == current_user.id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Pantry item not found")

    await db.delete(item)
    return MessageResponse(message="Item deleted")


@router.post("/{item_id}/consume", response_model=PantryItemRead)
async def consume_pantry_item(
    item_id: UUID,
    data: PantryConsumeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Consume a quantity of a pantry item and log it to food log."""
    result = await db.execute(
        select(PantryItem).where(PantryItem.id == item_id, PantryItem.user_id == current_user.id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Pantry item not found")

    item.quantity = max(0, item.quantity - data.quantity)

    # Create a FoodLog entry from the consumed pantry item
    nutrition = item.nutrition_json or {}
    ratio = data.quantity / max(item.quantity + data.quantity, 1)
    food_log = FoodLog(
        user_id=current_user.id,
        logged_at=datetime.utcnow(),
        meal_type=data.meal_type,
        food_name=item.name,
        quantity=data.quantity,
        unit=item.unit,
        calories=nutrition.get("calories", 0) * ratio if nutrition else None,
        protein_g=nutrition.get("protein_g", 0) * ratio if nutrition else None,
        carbs_g=nutrition.get("carbs_g", 0) * ratio if nutrition else None,
        fat_g=nutrition.get("fat_g", 0) * ratio if nutrition else None,
        fiber_g=nutrition.get("fiber_g", 0) * ratio if nutrition else None,
        sodium_mg=nutrition.get("sodium_mg", 0) * ratio if nutrition else None,
    )
    db.add(food_log)

    await db.flush()
    await db.refresh(item)
    return item
