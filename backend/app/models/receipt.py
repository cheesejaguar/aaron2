from datetime import datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship

from app.models.base import UUIDBase

if TYPE_CHECKING:
    from app.models.user import User


class PurchaseReceipt(UUIDBase, table=True):
    __tablename__ = "purchase_receipts"

    user_id: UUID = Field(foreign_key="users.id", index=True)
    raw_text: str
    parsed_at: datetime | None = None
    source: str | None = None
    items_json: list[dict[str, Any]] | None = Field(default=None, sa_column=Column(JSONB))

    user: "User" = Relationship(back_populates="purchase_receipts")
