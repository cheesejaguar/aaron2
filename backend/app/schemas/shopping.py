from uuid import UUID

from pydantic import BaseModel


class ShoppingListItemCreate(BaseModel):
    name: str
    quantity: float | None = None
    unit: str | None = None
    category: str | None = None


class ShoppingListItemRead(BaseModel):
    id: UUID
    name: str
    quantity: float | None = None
    unit: str | None = None
    category: str | None = None
    is_checked: bool
    is_ai_suggested: bool
    health_priority_score: float | None = None


class ShoppingListCreate(BaseModel):
    name: str
    items: list[ShoppingListItemCreate] = []


class ShoppingListRead(BaseModel):
    id: UUID
    name: str
    status: str
    items: list[ShoppingListItemRead] = []
