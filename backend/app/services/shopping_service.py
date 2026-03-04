from urllib.parse import quote_plus

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select

from app.models.pantry import PantryItem
from app.models.shopping import ShoppingList, ShoppingListItem
from app.models.user import User

CATEGORY_HEALTH_SCORES: dict[str | None, float] = {
    "produce": 1.0,
    "dairy": 0.7,
    "meat": 0.6,
    "grains": 0.8,
    "canned": 0.5,
    "frozen": 0.4,
    "beverages": 0.3,
    "snacks": 0.2,
    "condiments": 0.3,
    "other": 0.5,
    None: 0.5,
}


def _compute_health_priority(name: str, category: str | None) -> float:
    """Compute a 0.0-1.0 health priority score based on item category."""
    return CATEGORY_HEALTH_SCORES.get(category, 0.5)


def build_amazon_cart_url(shopping_list: ShoppingList) -> str:
    """Build an Amazon Fresh search URL for unchecked items."""
    unchecked = [item for item in shopping_list.items if not item.is_checked]
    if not unchecked:
        return ""
    search_terms = ", ".join(item.name for item in unchecked[:10])
    return f"https://www.amazon.com/s?k={quote_plus(search_terms)}&i=amazonfresh"


async def replenish_from_pantry(
    db: AsyncSession, user: User, shopping_list: ShoppingList
) -> ShoppingList:
    """Add items to shopping list based on low pantry stock."""
    result = await db.execute(
        select(PantryItem).where(
            PantryItem.user_id == user.id,
            PantryItem.low_stock_threshold.isnot(None),  # type: ignore[union-attr]
        )
    )
    low_stock_items = [
        item
        for item in result.scalars().all()
        if item.low_stock_threshold and item.quantity <= item.low_stock_threshold
    ]

    for pantry_item in low_stock_items:
        list_item = ShoppingListItem(
            shopping_list_id=shopping_list.id,
            name=pantry_item.name,
            quantity=1,
            unit=pantry_item.unit,
            category=pantry_item.category,
            is_ai_suggested=True,
            pantry_item_ref=pantry_item.id,
            health_priority_score=_compute_health_priority(pantry_item.name, pantry_item.category),
        )
        db.add(list_item)

    await db.flush()

    result = await db.execute(  # type: ignore[arg-type]
        select(ShoppingList)
        .where(ShoppingList.id == shopping_list.id)
        .options(selectinload(ShoppingList.items))  # type: ignore[arg-type]
    )
    return result.scalar_one()  # type: ignore[return-value]
