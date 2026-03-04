from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import text
from sqlmodel import Field, Relationship

from app.models.base import UUIDBase

if TYPE_CHECKING:
    from app.models.user import User


class BloodPressureLog(UUIDBase, table=True):
    __tablename__ = "blood_pressure_logs"

    user_id: UUID = Field(foreign_key="users.id", index=True)
    systolic: int
    diastolic: int
    pulse: int | None = None
    notes: str | None = None
    measured_at: datetime = Field(
        default=None,
        sa_column_kwargs={"server_default": text("now()")},
    )

    user: "User" = Relationship(back_populates="blood_pressure_logs")


class WeightLog(UUIDBase, table=True):
    __tablename__ = "weight_logs"

    user_id: UUID = Field(foreign_key="users.id", index=True)
    weight_lbs: float
    notes: str | None = None
    measured_at: datetime = Field(
        default=None,
        sa_column_kwargs={"server_default": text("now()")},
    )

    user: "User" = Relationship(back_populates="weight_logs")


class CholesterolLog(UUIDBase, table=True):
    __tablename__ = "cholesterol_logs"

    user_id: UUID = Field(foreign_key="users.id", index=True)
    total_mg_dl: float
    ldl: float | None = None
    hdl: float | None = None
    triglycerides: float | None = None
    notes: str | None = None
    measured_at: datetime = Field(
        default=None,
        sa_column_kwargs={"server_default": text("now()")},
    )

    user: "User" = Relationship(back_populates="cholesterol_logs")
