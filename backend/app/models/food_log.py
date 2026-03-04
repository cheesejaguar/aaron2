from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, Relationship

from app.models.base import UUIDBase

if TYPE_CHECKING:
    from app.models.user import User


class FoodLog(UUIDBase, table=True):
    __tablename__ = "food_logs"

    user_id: UUID = Field(foreign_key="users.id", index=True)
    logged_at: datetime
    meal_type: str  # breakfast, lunch, dinner, snack
    food_name: str
    quantity: float | None = None
    unit: str | None = None
    calories: float | None = None
    protein_g: float | None = None
    carbs_g: float | None = None
    fat_g: float | None = None
    fiber_g: float | None = None
    sodium_mg: float | None = None
    potassium_mg: float | None = None
    cholesterol_mg: float | None = None

    user: "User" = Relationship(back_populates="food_logs")
