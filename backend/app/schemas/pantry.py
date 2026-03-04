from datetime import date
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class PantryItemCreate(BaseModel):
    name: str
    category: str | None = None
    quantity: float = 1.0
    unit: str | None = None
    nutrition_json: dict[str, Any] | None = None
    purchase_date: date | None = None
    estimated_expiry: date | None = None
    low_stock_threshold: float | None = None


class PantryItemUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    quantity: float | None = None
    unit: str | None = None
    nutrition_json: dict[str, Any] | None = None
    purchase_date: date | None = None
    estimated_expiry: date | None = None
    low_stock_threshold: float | None = None


class PantryItemRead(BaseModel):
    id: UUID
    name: str
    category: str | None = None
    quantity: float
    unit: str | None = None
    nutrition_json: dict[str, Any] | None = None
    purchase_date: date | None = None
    estimated_expiry: date | None = None
    low_stock_threshold: float | None = None


class PantryConsumeRequest(BaseModel):
    quantity: float
    meal_type: str = "snack"
