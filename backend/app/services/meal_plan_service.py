import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select

from app.models.meal_plan import MealPlan, MealPlanEntry
from app.models.pantry import PantryItem
from app.models.user import User
from app.schemas.meal_plan import MealPlanSuggestRequest
from app.services.ai_service import TaskType, ai_service

SYSTEM_PROMPT = """You are a DASH diet meal planning expert. Create a 7-day meal plan that:
- Emphasizes fruits, vegetables, whole grains, lean proteins
- Limits sodium to <2300mg/day (ideally <1500mg)
- Is rich in potassium, calcium, magnesium, and fiber
- Supports weight loss and blood pressure reduction
- Includes 3 meals + 1 snack per day

Return JSON with this structure:
{
  "entries": [
    {"day_of_week": 0, "meal_type": "breakfast",
     "meal": {"name": "...", "description": "...",
     "estimated_calories": 300, "estimated_sodium_mg": 200}},
    ...
  ]
}
day_of_week: 0=Monday through 6=Sunday
meal_type: "breakfast", "lunch", "dinner", "snack"
"""


async def suggest_meal_plan(db: AsyncSession, user: User, data: MealPlanSuggestRequest) -> MealPlan:
    # Get current pantry for context
    result = await db.execute(select(PantryItem).where(PantryItem.user_id == user.id))
    pantry_items = result.scalars().all()
    pantry_names = [item.name for item in pantry_items]

    prompt_parts = ["Create a 7-day DASH diet meal plan."]
    if pantry_names:
        prompt_parts.append(f"Available pantry items: {', '.join(pantry_names[:20])}")
    if data.dietary_preferences:
        prompt_parts.append(f"Dietary preferences: {', '.join(data.dietary_preferences)}")
    if data.health_focus:
        prompt_parts.append(f"Health focus: {data.health_focus}")
    if user.health_goals_json:
        prompt_parts.append(f"Health goals: {json.dumps(user.health_goals_json)}")

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": " ".join(prompt_parts)},
    ]

    ai_result = await ai_service.complete_json(
        db, str(user.id), TaskType.MEAL_PLAN_SUGGEST, messages, use_cache=False
    )

    plan = MealPlan(user_id=user.id, week_start_date=data.week_start_date)
    db.add(plan)
    await db.flush()

    for entry_data in ai_result.get("entries", []):
        entry = MealPlanEntry(
            meal_plan_id=plan.id,
            day_of_week=entry_data.get("day_of_week", 0),
            meal_type=entry_data.get("meal_type", "lunch"),
            custom_meal_json=entry_data.get("meal"),
        )
        db.add(entry)

    await db.flush()
    result = await db.execute(
        select(MealPlan).where(MealPlan.id == plan.id).options(selectinload(MealPlan.entries))  # type: ignore[arg-type]
    )
    return result.scalar_one()  # type: ignore[return-value]
