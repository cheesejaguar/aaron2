from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import ARRAY, Column, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship

from app.models.base import UUIDBase

if TYPE_CHECKING:
    from app.models.meal_plan import MealPlanEntry
    from app.models.user import User


class Recipe(UUIDBase, table=True):
    __tablename__ = "recipes"

    user_id: UUID = Field(foreign_key="users.id", index=True)
    title: str
    description: str | None = None
    ingredients_json: list[dict[str, Any]] | None = Field(default=None, sa_column=Column(JSONB))
    steps_json: list[str] | None = Field(default=None, sa_column=Column(JSONB))
    nutrition_per_serving_json: dict[str, Any] | None = Field(default=None, sa_column=Column(JSONB))
    health_tags: list[str] | None = Field(default=None, sa_column=Column(ARRAY(String)))
    source_url: str | None = None
    is_ai_generated: bool = False

    user: "User" = Relationship(back_populates="recipes")
    meal_plan_entries: list["MealPlanEntry"] = Relationship(back_populates="recipe")
