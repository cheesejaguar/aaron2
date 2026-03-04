from datetime import date, datetime, timedelta
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.food_log import FoodLog
from app.schemas.food_log import DailySummary


async def get_daily_summary(db: AsyncSession, user_id: UUID, date_str: str) -> DailySummary:
    d = date.fromisoformat(date_str)
    start = datetime(d.year, d.month, d.day)
    end = start + timedelta(days=1)

    result = await db.execute(
        select(FoodLog).where(
            FoodLog.user_id == user_id,
            FoodLog.logged_at >= start,
            FoodLog.logged_at < end,
        )
    )
    logs = result.scalars().all()

    return DailySummary(
        date=date_str,
        total_calories=sum(log.calories or 0 for log in logs),
        total_protein_g=sum(log.protein_g or 0 for log in logs),
        total_carbs_g=sum(log.carbs_g or 0 for log in logs),
        total_fat_g=sum(log.fat_g or 0 for log in logs),
        total_fiber_g=sum(log.fiber_g or 0 for log in logs),
        total_sodium_mg=sum(log.sodium_mg or 0 for log in logs),
        total_potassium_mg=sum(log.potassium_mg or 0 for log in logs),
        total_cholesterol_mg=sum(log.cholesterol_mg or 0 for log in logs),
        meal_count=len(logs),
    )
