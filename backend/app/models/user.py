from typing import TYPE_CHECKING, Any

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship

from app.models.base import UUIDBase

if TYPE_CHECKING:
    from app.models.ai import AIConversation, AIUsageLog
    from app.models.food_log import FoodLog
    from app.models.health import BloodPressureLog, CholesterolLog, WeightLog
    from app.models.meal_plan import MealPlan
    from app.models.pantry import PantryItem
    from app.models.receipt import PurchaseReceipt
    from app.models.recipe import Recipe
    from app.models.shopping import ShoppingList


class User(UUIDBase, table=True):
    __tablename__ = "users"

    email: str = Field(unique=True, index=True)
    name: str
    hashed_password: str
    health_goals_json: dict[str, Any] | None = Field(default=None, sa_column=Column(JSONB))

    # Relationships
    pantry_items: list["PantryItem"] = Relationship(back_populates="user")
    purchase_receipts: list["PurchaseReceipt"] = Relationship(back_populates="user")
    recipes: list["Recipe"] = Relationship(back_populates="user")
    meal_plans: list["MealPlan"] = Relationship(back_populates="user")
    shopping_lists: list["ShoppingList"] = Relationship(back_populates="user")
    food_logs: list["FoodLog"] = Relationship(back_populates="user")
    blood_pressure_logs: list["BloodPressureLog"] = Relationship(back_populates="user")
    weight_logs: list["WeightLog"] = Relationship(back_populates="user")
    cholesterol_logs: list["CholesterolLog"] = Relationship(back_populates="user")
    ai_conversations: list["AIConversation"] = Relationship(back_populates="user")
    ai_usage_logs: list["AIUsageLog"] = Relationship(back_populates="user")
