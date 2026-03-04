from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class FoodLogCreate(BaseModel):
    logged_at: datetime | None = None
    meal_type: str
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


class FoodLogRead(BaseModel):
    id: UUID
    logged_at: datetime
    meal_type: str
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


class DailySummary(BaseModel):
    date: str
    total_calories: float
    total_protein_g: float
    total_carbs_g: float
    total_fat_g: float
    total_fiber_g: float
    total_sodium_mg: float
    total_potassium_mg: float
    total_cholesterol_mg: float
    meal_count: int
