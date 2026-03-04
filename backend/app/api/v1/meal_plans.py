from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select

from app.api.deps import get_current_user, get_db
from app.models.meal_plan import MealPlan, MealPlanEntry
from app.models.user import User
from app.schemas.meal_plan import MealPlanCreate, MealPlanRead, MealPlanSuggestRequest
from app.services.meal_plan_service import suggest_meal_plan

router = APIRouter(prefix="/meal-plans", tags=["meal-plans"])


@router.get("/", response_model=list[MealPlanRead])
async def list_meal_plans(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all meal plans for the current user."""
    result = await db.execute(
        select(MealPlan)
        .where(MealPlan.user_id == current_user.id)
        .options(selectinload(MealPlan.entries))  # type: ignore[arg-type]
        .order_by(MealPlan.week_start_date.desc())  # type: ignore[attr-defined]
    )
    return result.scalars().all()


@router.post("/", response_model=MealPlanRead, status_code=201)
async def create_meal_plan(
    data: MealPlanCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new weekly meal plan with entries."""
    plan = MealPlan(
        user_id=current_user.id,
        week_start_date=data.week_start_date,
    )
    db.add(plan)
    await db.flush()

    for entry_data in data.entries:
        entry = MealPlanEntry(
            meal_plan_id=plan.id,
            **entry_data.model_dump(),
        )
        db.add(entry)

    await db.flush()
    result = await db.execute(
        select(MealPlan).where(MealPlan.id == plan.id).options(selectinload(MealPlan.entries))  # type: ignore[arg-type]
    )
    return result.scalar_one()


@router.post("/suggest", response_model=MealPlanRead, status_code=201)
async def suggest_meal_plan_endpoint(
    data: MealPlanSuggestRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get an AI-suggested DASH diet meal plan for the week."""
    return await suggest_meal_plan(db, current_user, data)
