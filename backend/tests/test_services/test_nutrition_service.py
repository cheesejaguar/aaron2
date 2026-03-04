from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.services.nutrition_service import get_daily_summary


def _mock_db_with_logs(logs):
    """Create mock DB that returns given logs for the food log query."""
    db = AsyncMock()
    result = MagicMock()  # MagicMock, not AsyncMock - scalars() is sync
    scalars = MagicMock()
    scalars.all.return_value = logs
    result.scalars.return_value = scalars
    db.execute = AsyncMock(return_value=result)
    return db


class TestGetDailySummary:
    @pytest.mark.asyncio
    async def test_empty_day(self):
        db = _mock_db_with_logs([])
        summary = await get_daily_summary(db, uuid4(), "2025-06-15")
        assert summary.total_calories == 0
        assert summary.meal_count == 0

    @pytest.mark.asyncio
    async def test_with_logs(self):
        log1 = MagicMock(
            calories=300,
            protein_g=20.0,
            carbs_g=30.0,
            fat_g=10.0,
            fiber_g=5.0,
            sodium_mg=100.0,
            potassium_mg=200.0,
            cholesterol_mg=50.0,
        )
        log2 = MagicMock(
            calories=500,
            protein_g=40.0,
            carbs_g=20.0,
            fat_g=15.0,
            fiber_g=3.0,
            sodium_mg=200.0,
            potassium_mg=300.0,
            cholesterol_mg=80.0,
        )

        db = _mock_db_with_logs([log1, log2])
        summary = await get_daily_summary(db, uuid4(), "2025-06-15")
        assert summary.total_calories == 800
        assert summary.total_protein_g == 60.0
        assert summary.total_carbs_g == 50.0
        assert summary.meal_count == 2

    @pytest.mark.asyncio
    async def test_handles_none_values(self):
        log = MagicMock(
            calories=None,
            protein_g=None,
            carbs_g=None,
            fat_g=None,
            fiber_g=None,
            sodium_mg=None,
            potassium_mg=None,
            cholesterol_mg=None,
        )

        db = _mock_db_with_logs([log])
        summary = await get_daily_summary(db, uuid4(), "2025-06-15")
        assert summary.total_calories == 0
        assert summary.meal_count == 1
