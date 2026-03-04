import uuid
from datetime import datetime

from sqlalchemy import text
from sqlmodel import Field, SQLModel


class UUIDBase(SQLModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(
        default=None,
        sa_column_kwargs={"server_default": text("now()")},
    )
