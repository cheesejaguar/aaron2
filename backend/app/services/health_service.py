from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.health import BloodPressureLog, CholesterolLog, WeightLog
from app.schemas.health import DashboardResponse


def bp_status(systolic: int, diastolic: int) -> str:
    if systolic > 180 or diastolic > 120:
        return "crisis"
    if systolic >= 140 or diastolic >= 90:
        return "high_stage_2"
    if systolic >= 130 or diastolic >= 80:
        return "high_stage_1"
    if systolic >= 120:
        return "elevated"
    return "normal"


async def get_dashboard(db: AsyncSession, user_id: UUID) -> DashboardResponse:
    # Latest BP
    bp_result = await db.execute(
        select(BloodPressureLog)
        .where(BloodPressureLog.user_id == user_id)
        .order_by(BloodPressureLog.measured_at.desc())  # type: ignore[attr-defined]
        .limit(30)
    )
    bp_logs = bp_result.scalars().all()
    latest_bp = bp_logs[0] if bp_logs else None

    # Latest Weight
    weight_result = await db.execute(
        select(WeightLog)
        .where(WeightLog.user_id == user_id)
        .order_by(WeightLog.measured_at.desc())  # type: ignore[attr-defined]
        .limit(30)
    )
    weight_logs = weight_result.scalars().all()
    latest_weight = weight_logs[0] if weight_logs else None

    # Latest Cholesterol
    chol_result = await db.execute(
        select(CholesterolLog)
        .where(CholesterolLog.user_id == user_id)
        .order_by(CholesterolLog.measured_at.desc())  # type: ignore[attr-defined]
        .limit(1)
    )
    latest_cholesterol = chol_result.scalar_one_or_none()

    status = None
    if latest_bp:
        status = bp_status(latest_bp.systolic, latest_bp.diastolic)

    return DashboardResponse(
        latest_bp=latest_bp,
        latest_weight=latest_weight,
        latest_cholesterol=latest_cholesterol,
        bp_status=status,
        weight_trend=list(weight_logs),
        bp_trend=list(bp_logs),
    )
