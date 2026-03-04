from datetime import date
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class MealPlanEntryCreate(BaseModel):
    day_of_week: int
    meal_type: str
    recipe_id: UUID | None = None
    custom_meal_json: dict[str, Any] | None = None


class MealPlanEntryRead(BaseModel):
    id: UUID
    day_of_week: int
    meal_type: str
    recipe_id: UUID | None = None
    custom_meal_json: dict[str, Any] | None = None


class MealPlanCreate(BaseModel):
    week_start_date: date
    entries: list[MealPlanEntryCreate] = []


class MealPlanRead(BaseModel):
    id: UUID
    week_start_date: date
    entries: list[MealPlanEntryRead] = []


class MealPlanSuggestRequest(BaseModel):
    week_start_date: date
    dietary_preferences: list[str] | None = None
    health_focus: str | None = None
