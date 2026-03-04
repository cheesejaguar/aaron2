from datetime import datetime
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.health import BloodPressureLog, CholesterolLog, WeightLog
from app.models.user import User


class TestBloodPressure:
    @pytest.mark.asyncio
    async def test_create_bp_log(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/health/blood-pressure",
            json={"systolic": 120, "diastolic": 80},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["systolic"] == 120
        assert data["diastolic"] == 80
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_bp_log_with_optional_fields(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/health/blood-pressure",
            json={"systolic": 130, "diastolic": 85, "pulse": 72, "notes": "After coffee"},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["pulse"] == 72
        assert data["notes"] == "After coffee"

    @pytest.mark.asyncio
    async def test_list_bp_logs_empty(self, client: AsyncClient):
        resp = await client.get("/api/v1/health/blood-pressure")
        assert resp.status_code == 200
        assert resp.json() == []

    @pytest.mark.asyncio
    async def test_list_bp_logs_ordered(
        self, client: AsyncClient, db_session: AsyncSession, test_user: User
    ):
        for sys_val in [120, 130, 140]:
            log = BloodPressureLog(
                id=uuid4(),
                user_id=test_user.id,
                systolic=sys_val,
                diastolic=80,
                measured_at=datetime.utcnow(),
            )
            db_session.add(log)
        await db_session.flush()

        resp = await client.get("/api/v1/health/blood-pressure")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 3
        # Most recent first
        assert data[0]["systolic"] >= data[-1]["systolic"]

    @pytest.mark.asyncio
    async def test_list_bp_with_limit(
        self, client: AsyncClient, db_session: AsyncSession, test_user: User
    ):
        for i in range(5):
            db_session.add(
                BloodPressureLog(
                    id=uuid4(),
                    user_id=test_user.id,
                    systolic=120 + i,
                    diastolic=80,
                    measured_at=datetime.utcnow(),
                )
            )
        await db_session.flush()

        resp = await client.get("/api/v1/health/blood-pressure", params={"limit": 2})
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    @pytest.mark.asyncio
    async def test_bp_user_isolation(
        self, client: AsyncClient, db_session: AsyncSession, second_user: User
    ):
        db_session.add(
            BloodPressureLog(
                id=uuid4(),
                user_id=second_user.id,
                systolic=150,
                diastolic=95,
                measured_at=datetime.utcnow(),
            )
        )
        await db_session.flush()

        resp = await client.get("/api/v1/health/blood-pressure")
        assert resp.status_code == 200
        assert len(resp.json()) == 0


class TestWeight:
    @pytest.mark.asyncio
    async def test_create_weight_log(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/health/weight",
            json={"weight_lbs": 185.5},
        )
        assert resp.status_code == 201
        assert resp.json()["weight_lbs"] == 185.5

    @pytest.mark.asyncio
    async def test_create_weight_with_notes(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/health/weight",
            json={"weight_lbs": 183.0, "notes": "Morning weigh-in"},
        )
        assert resp.status_code == 201
        assert resp.json()["notes"] == "Morning weigh-in"

    @pytest.mark.asyncio
    async def test_list_weight_logs(self, client: AsyncClient):
        # Create two logs
        await client.post("/api/v1/health/weight", json={"weight_lbs": 185.0})
        await client.post("/api/v1/health/weight", json={"weight_lbs": 184.0})

        resp = await client.get("/api/v1/health/weight")
        assert resp.status_code == 200
        assert len(resp.json()) == 2


class TestCholesterol:
    @pytest.mark.asyncio
    async def test_create_cholesterol_log(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/health/cholesterol",
            json={"total_mg_dl": 200, "ldl": 120, "hdl": 55, "triglycerides": 150},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["total_mg_dl"] == 200
        assert data["ldl"] == 120

    @pytest.mark.asyncio
    async def test_create_cholesterol_total_only(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/health/cholesterol",
            json={"total_mg_dl": 195},
        )
        assert resp.status_code == 201

    @pytest.mark.asyncio
    async def test_list_cholesterol(self, client: AsyncClient):
        await client.post("/api/v1/health/cholesterol", json={"total_mg_dl": 200})
        resp = await client.get("/api/v1/health/cholesterol")
        assert resp.status_code == 200
        assert len(resp.json()) == 1


class TestDashboard:
    @pytest.mark.asyncio
    async def test_dashboard_empty(self, client: AsyncClient):
        resp = await client.get("/api/v1/health/dashboard")
        assert resp.status_code == 200
        data = resp.json()
        assert data["latest_bp"] is None
        assert data["latest_weight"] is None
        assert data["latest_cholesterol"] is None
        assert data["bp_status"] is None

    @pytest.mark.asyncio
    async def test_dashboard_with_data(
        self, client: AsyncClient, db_session: AsyncSession, test_user: User
    ):
        db_session.add(
            BloodPressureLog(
                id=uuid4(),
                user_id=test_user.id,
                systolic=125,
                diastolic=78,
                measured_at=datetime.utcnow(),
            )
        )
        db_session.add(
            WeightLog(
                id=uuid4(),
                user_id=test_user.id,
                weight_lbs=185.0,
                measured_at=datetime.utcnow(),
            )
        )
        db_session.add(
            CholesterolLog(
                id=uuid4(),
                user_id=test_user.id,
                total_mg_dl=200,
                measured_at=datetime.utcnow(),
            )
        )
        await db_session.flush()

        resp = await client.get("/api/v1/health/dashboard")
        assert resp.status_code == 200
        data = resp.json()
        assert data["latest_bp"]["systolic"] == 125
        assert data["latest_weight"]["weight_lbs"] == 185.0
        assert data["latest_cholesterol"]["total_mg_dl"] == 200
        assert data["bp_status"] == "elevated"

