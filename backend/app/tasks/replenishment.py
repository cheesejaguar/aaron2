import asyncio
from datetime import datetime, timedelta

from sqlalchemy import func
from sqlmodel import select

from app.api.deps import DEFAULT_USER_EMAIL
from app.core.database import async_session_factory
from app.models.food_log import FoodLog
from app.models.pantry import PantryItem
from app.models.shopping import ShoppingList, ShoppingListItem
from app.models.user import User
from app.services.shopping_service import _compute_health_priority
from app.tasks import celery_app


async def _calculate_consumption_rate(db, user_id, pantry_item) -> dict:
    """Calculate daily consumption rate from FoodLog over the past 14 days."""
    cutoff = datetime.utcnow() - timedelta(days=14)
    result = await db.execute(
        select(func.count()).where(
            FoodLog.user_id == user_id,
            FoodLog.food_name == pantry_item.name,
            FoodLog.logged_at >= cutoff,
        )
    )
    count = result.scalar() or 0
    daily_rate = count / 14.0
    days_until_depletion = pantry_item.quantity / daily_rate if daily_rate > 0 else float("inf")
    return {"daily_rate": daily_rate, "days_until_depletion": days_until_depletion}


async def _auto_replenish():
    async with async_session_factory() as db:
        result = await db.execute(
            select(User).where(User.email == DEFAULT_USER_EMAIL)
        )
        user = result.scalar_one_or_none()
        if not user:
            return

        # Find pantry items with thresholds
        pantry_result = await db.execute(
            select(PantryItem).where(
                PantryItem.user_id == user.id,
                PantryItem.low_stock_threshold.isnot(None),  # type: ignore[union-attr]
            )
        )
        items_to_replenish = []
        for item in pantry_result.scalars().all():
            if not item.low_stock_threshold:
                continue
            # Check consumption rate
            rate = await _calculate_consumption_rate(db, user.id, item)
            # Replenish if depleting within 5 days OR below threshold
            if rate["days_until_depletion"] <= 5 or item.quantity <= item.low_stock_threshold:
                items_to_replenish.append(item)

        if not items_to_replenish:
            return

        # Find or create active shopping list
        list_result = await db.execute(
            select(ShoppingList).where(
                ShoppingList.user_id == user.id,
                ShoppingList.status == "active",
            )
        )
        shopping_list = list_result.scalar_one_or_none()

        if not shopping_list:
            shopping_list = ShoppingList(
                user_id=user.id,
                name="Auto-Replenishment",
                status="active",
            )
            db.add(shopping_list)
            await db.flush()

        for pantry_item in items_to_replenish:
            item = ShoppingListItem(
                shopping_list_id=shopping_list.id,
                name=pantry_item.name,
                quantity=1,
                unit=pantry_item.unit,
                category=pantry_item.category,
                is_ai_suggested=True,
                pantry_item_ref=pantry_item.id,
                health_priority_score=_compute_health_priority(
                    pantry_item.name, pantry_item.category
                ),
            )
            db.add(item)

        await db.commit()


@celery_app.task(name="app.tasks.replenishment.auto_replenish")
def auto_replenish():
    asyncio.run(_auto_replenish())
