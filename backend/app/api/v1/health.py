from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.api.deps import get_current_user, get_db
from app.models.health import BloodPressureLog, CholesterolLog, WeightLog
from app.models.user import User
from app.schemas.health import (
    BPLogCreate,
    BPLogRead,
    CholesterolLogCreate,
    CholesterolLogRead,
    DashboardResponse,
    WeightLogCreate,
    WeightLogRead,
)
from app.services.health_service import get_dashboard

router = APIRouter(prefix="/health", tags=["health"])


# Blood Pressure
@router.get("/blood-pressure", response_model=list[BPLogRead])
async def list_bp_logs(
    limit: int = Query(30, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List blood pressure logs, most recent first."""
    result = await db.execute(
        select(BloodPressureLog)
        .where(BloodPressureLog.user_id == current_user.id)
        .order_by(BloodPressureLog.measured_at.desc())  # type: ignore[attr-defined]
        .limit(limit)
    )
    return result.scalars().all()


@router.post("/blood-pressure", response_model=BPLogRead, status_code=201)
async def create_bp_log(
    data: BPLogCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Record a new blood pressure reading."""
    log = BloodPressureLog(**data.model_dump(), user_id=current_user.id)
    db.add(log)
    await db.flush()
    await db.refresh(log)
    return log


# Weight
@router.get("/weight", response_model=list[WeightLogRead])
async def list_weight_logs(
    limit: int = Query(30, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List weight logs, most recent first."""
    result = await db.execute(
        select(WeightLog)
        .where(WeightLog.user_id == current_user.id)
        .order_by(WeightLog.measured_at.desc())  # type: ignore[attr-defined]
        .limit(limit)
    )
    return result.scalars().all()


@router.post("/weight", response_model=WeightLogRead, status_code=201)
async def create_weight_log(
    data: WeightLogCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Record a new weight measurement."""
    log = WeightLog(**data.model_dump(), user_id=current_user.id)
    db.add(log)
    await db.flush()
    await db.refresh(log)
    return log


# Cholesterol
@router.get("/cholesterol", response_model=list[CholesterolLogRead])
async def list_cholesterol_logs(
    limit: int = Query(30, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List cholesterol logs, most recent first."""
    result = await db.execute(
        select(CholesterolLog)
        .where(CholesterolLog.user_id == current_user.id)
        .order_by(CholesterolLog.measured_at.desc())  # type: ignore[attr-defined]
        .limit(limit)
    )
    return result.scalars().all()


@router.post("/cholesterol", response_model=CholesterolLogRead, status_code=201)
async def create_cholesterol_log(
    data: CholesterolLogCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Record a new cholesterol panel result."""
    log = CholesterolLog(**data.model_dump(), user_id=current_user.id)
    db.add(log)
    await db.flush()
    await db.refresh(log)
    return log


# Dashboard
@router.get("/dashboard", response_model=DashboardResponse)
async def dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get aggregated health dashboard with latest metrics and trends."""
    return await get_dashboard(db, current_user.id)
