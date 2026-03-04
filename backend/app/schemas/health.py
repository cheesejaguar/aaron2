from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BPLogCreate(BaseModel):
    systolic: int
    diastolic: int
    pulse: int | None = None
    notes: str | None = None


class BPLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    systolic: int
    diastolic: int
    pulse: int | None = None
    notes: str | None = None
    measured_at: datetime


class WeightLogCreate(BaseModel):
    weight_lbs: float
    notes: str | None = None


class WeightLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    weight_lbs: float
    notes: str | None = None
    measured_at: datetime


class CholesterolLogCreate(BaseModel):
    total_mg_dl: float
    ldl: float | None = None
    hdl: float | None = None
    triglycerides: float | None = None
    notes: str | None = None


class CholesterolLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    total_mg_dl: float
    ldl: float | None = None
    hdl: float | None = None
    triglycerides: float | None = None
    notes: str | None = None
    measured_at: datetime


class DashboardResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    latest_bp: BPLogRead | None = None
    latest_weight: WeightLogRead | None = None
    latest_cholesterol: CholesterolLogRead | None = None
    bp_status: str | None = None
    weight_trend: list[WeightLogRead] = []
    bp_trend: list[BPLogRead] = []
