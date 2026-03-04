from datetime import datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.schemas.health import (
    BPLogCreate,
    BPLogRead,
    CholesterolLogCreate,
    DashboardResponse,
    WeightLogCreate,
    WeightLogRead,
)


class TestBPLogCreate:
    def test_valid_bp_log(self):
        bp = BPLogCreate(systolic=120, diastolic=80)
        assert bp.systolic == 120
        assert bp.pulse is None

    def test_with_optional_fields(self):
        bp = BPLogCreate(systolic=140, diastolic=90, pulse=72, notes="After exercise")
        assert bp.pulse == 72
        assert bp.notes == "After exercise"

    def test_missing_required_rejected(self):
        with pytest.raises(ValidationError):
            BPLogCreate(systolic=120)  # type: ignore[call-arg]


class TestWeightLogCreate:
    def test_valid_weight(self):
        w = WeightLogCreate(weight_lbs=185.5)
        assert w.weight_lbs == 185.5

    def test_with_notes(self):
        w = WeightLogCreate(weight_lbs=180.0, notes="Morning weight")
        assert w.notes == "Morning weight"


class TestCholesterolLogCreate:
    def test_full_panel(self):
        c = CholesterolLogCreate(total_mg_dl=200, ldl=120, hdl=55, triglycerides=150)
        assert c.total_mg_dl == 200
        assert c.ldl == 120

    def test_total_only(self):
        c = CholesterolLogCreate(total_mg_dl=195)
        assert c.ldl is None


class TestBPLogRead:
    def test_serialization(self):
        bp = BPLogRead(
            id=uuid4(),
            systolic=120,
            diastolic=80,
            measured_at=datetime(2024, 1, 15, 8, 0),
        )
        assert bp.systolic == 120


class TestDashboardResponse:
    def test_empty_dashboard(self):
        d = DashboardResponse()
        assert d.latest_bp is None
        assert d.weight_trend == []

    def test_dashboard_with_data(self):
        bp = BPLogRead(
            id=uuid4(),
            systolic=125,
            diastolic=82,
            measured_at=datetime(2024, 1, 15),
        )
        w = WeightLogRead(
            id=uuid4(),
            weight_lbs=185.0,
            measured_at=datetime(2024, 1, 15),
        )
        d = DashboardResponse(
            latest_bp=bp,
            latest_weight=w,
            bp_status="elevated",
            bp_trend=[bp],
            weight_trend=[w],
        )
        assert d.bp_status == "elevated"
        assert len(d.bp_trend) == 1
