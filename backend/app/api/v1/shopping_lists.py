from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select

from app.api.deps import get_current_user, get_db
from app.models.shopping import ShoppingList, ShoppingListItem
from app.models.user import User
from app.schemas.shopping import ShoppingListCreate, ShoppingListRead
from app.services.shopping_service import build_amazon_cart_url, replenish_from_pantry

router = APIRouter(prefix="/shopping-lists", tags=["shopping-lists"])


@router.get("/", response_model=list[ShoppingListRead])
async def list_shopping_lists(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all shopping lists for the current user."""
    result = await db.execute(
        select(ShoppingList)
        .where(ShoppingList.user_id == current_user.id)
        .options(selectinload(ShoppingList.items))  # type: ignore[arg-type]
        .order_by(ShoppingList.created_at.desc())  # type: ignore[attr-defined]
    )
    return result.scalars().all()


@router.post("/", response_model=ShoppingListRead, status_code=201)
async def create_shopping_list(
    data: ShoppingListCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new shopping list with items."""
    shopping_list = ShoppingList(
        user_id=current_user.id,
        name=data.name,
    )
    db.add(shopping_list)
    await db.flush()

    for item_data in data.items:
        item = ShoppingListItem(
            shopping_list_id=shopping_list.id,
            **item_data.model_dump(),
        )
        db.add(item)

    await db.flush()
    result = await db.execute(
        select(ShoppingList)
        .where(ShoppingList.id == shopping_list.id)
        .options(selectinload(ShoppingList.items))  # type: ignore[arg-type]
    )
    return result.scalar_one()


@router.post("/{list_id}/replenish", response_model=ShoppingListRead)
async def replenish_shopping_list(
    list_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Auto-add low-stock pantry items to this shopping list."""
    result = await db.execute(
        select(ShoppingList).where(
            ShoppingList.id == list_id, ShoppingList.user_id == current_user.id
        )
    )
    shopping_list = result.scalar_one_or_none()
    if not shopping_list:
        raise HTTPException(status_code=404, detail="Shopping list not found")

    return await replenish_from_pantry(db, current_user, shopping_list)


@router.get("/{list_id}/amazon-cart-url")
async def get_amazon_cart_url(
    list_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get an Amazon Fresh search URL for unchecked items."""
    result = await db.execute(
        select(ShoppingList)
        .where(ShoppingList.id == list_id, ShoppingList.user_id == current_user.id)
        .options(selectinload(ShoppingList.items))  # type: ignore[arg-type]
    )
    shopping_list = result.scalar_one_or_none()
    if not shopping_list:
        raise HTTPException(status_code=404, detail="Shopping list not found")

    url = build_amazon_cart_url(shopping_list)
    return {"url": url}
