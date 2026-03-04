from datetime import date
from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship

from app.models.base import UUIDBase

if TYPE_CHECKING:
    from app.models.recipe import Recipe
    from app.models.user import User


class MealPlan(UUIDBase, table=True):
    __tablename__ = "meal_plans"

    user_id: UUID = Field(foreign_key="users.id", index=True)
    week_start_date: date

    entries: list["MealPlanEntry"] = Relationship(back_populates="meal_plan")
    user: "User" = Relationship(back_populates="meal_plans")


class MealPlanEntry(UUIDBase, table=True):
    __tablename__ = "meal_plan_entries"

    meal_plan_id: UUID = Field(foreign_key="meal_plans.id", index=True)
    recipe_id: UUID | None = Field(default=None, foreign_key="recipes.id")
    day_of_week: int  # 0=Monday, 6=Sunday
    meal_type: str  # breakfast, lunch, dinner, snack
    custom_meal_json: dict[str, Any] | None = Field(default=None, sa_column=Column(JSONB))

    meal_plan: "MealPlan" = Relationship(back_populates="entries")
    recipe: "Recipe" = Relationship(back_populates="meal_plan_entries")
