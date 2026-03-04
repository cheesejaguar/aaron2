from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, Relationship

from app.models.base import UUIDBase

if TYPE_CHECKING:
    from app.models.user import User


class ShoppingList(UUIDBase, table=True):
    __tablename__ = "shopping_lists"

    user_id: UUID = Field(foreign_key="users.id", index=True)
    name: str
    status: str = "active"  # active, completed, archived

    items: list["ShoppingListItem"] = Relationship(back_populates="shopping_list")
    user: "User" = Relationship(back_populates="shopping_lists")


class ShoppingListItem(UUIDBase, table=True):
    __tablename__ = "shopping_list_items"

    shopping_list_id: UUID = Field(foreign_key="shopping_lists.id", index=True)
    name: str
    quantity: float | None = None
    unit: str | None = None
    category: str | None = None
    is_checked: bool = False
    is_ai_suggested: bool = False
    health_priority_score: float | None = None
    pantry_item_ref: UUID | None = None  # soft reference

    shopping_list: "ShoppingList" = Relationship(back_populates="items")
