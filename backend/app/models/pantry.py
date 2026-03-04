from datetime import date
from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship

from app.models.base import UUIDBase

if TYPE_CHECKING:
    from app.models.user import User


class PantryItem(UUIDBase, table=True):
    __tablename__ = "pantry_items"

    user_id: UUID = Field(foreign_key="users.id", index=True)
    name: str
    category: str | None = None
    quantity: float = 1.0
    unit: str | None = None
    nutrition_json: dict[str, Any] | None = Field(default=None, sa_column=Column(JSONB))
    purchase_date: date | None = None
    estimated_expiry: date | None = None
    low_stock_threshold: float | None = None

    user: "User" = Relationship(back_populates="pantry_items")
