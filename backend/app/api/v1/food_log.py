from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.api.deps import get_current_user, get_db
from app.models.food_log import FoodLog
from app.models.user import User
from app.schemas.food_log import DailySummary, FoodLogCreate, FoodLogRead
from app.services.nutrition_service import get_daily_summary

router = APIRouter(prefix="/food-log", tags=["food-log"])


@router.get("/", response_model=list[FoodLogRead])
async def list_food_logs(
    date_filter: str | None = Query(None, alias="date", description="Filter by date YYYY-MM-DD"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List food log entries, optionally filtered by date."""
    query = select(FoodLog).where(FoodLog.user_id == current_user.id)
    if date_filter:
        d = date.fromisoformat(date_filter)
        day_start = datetime(d.year, d.month, d.day)
        day_end = day_start + timedelta(days=1)
        query = query.where(
            FoodLog.logged_at >= day_start,
            FoodLog.logged_at < day_end,
        )
    query = query.order_by(FoodLog.logged_at.desc())  # type: ignore[attr-defined]
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/", response_model=FoodLogRead, status_code=201)
async def create_food_log(
    data: FoodLogCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Log a food entry with optional nutrition data."""
    dump = data.model_dump(exclude_unset=True)
    dump.pop("logged_at", None)
    log = FoodLog(
        **dump,
        user_id=current_user.id,
        logged_at=data.logged_at or datetime.utcnow(),
    )
    db.add(log)
    await db.flush()
    await db.refresh(log)
    return log


@router.get("/daily-summary", response_model=DailySummary)
async def daily_summary(
    date_str: str = Query(..., alias="date", description="Date YYYY-MM-DD"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get nutrition totals for a specific date."""
    return await get_daily_summary(db, current_user.id, date_str)
