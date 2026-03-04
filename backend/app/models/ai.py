from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship

from app.models.base import UUIDBase

if TYPE_CHECKING:
    from app.models.user import User


class AIConversation(UUIDBase, table=True):
    __tablename__ = "ai_conversations"

    user_id: UUID = Field(foreign_key="users.id", index=True)
    messages_json: list[dict[str, Any]] | None = Field(default=None, sa_column=Column(JSONB))

    user: "User" = Relationship(back_populates="ai_conversations")


class AIUsageLog(UUIDBase, table=True):
    __tablename__ = "ai_usage_logs"

    user_id: UUID = Field(foreign_key="users.id", index=True)
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cost_usd: float = 0.0
    task_type: str

    user: "User" = Relationship(back_populates="ai_usage_logs")
