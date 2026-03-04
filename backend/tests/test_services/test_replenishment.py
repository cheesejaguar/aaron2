from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from app.tasks.replenishment import _calculate_consumption_rate


class TestCalculateConsumptionRate:
    @pytest.mark.asyncio
    async def test_no_consumption(self):
        from unittest.mock import AsyncMock

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar.return_value = 0
        mock_db.execute.return_value = mock_result

        pantry_item = MagicMock()
        pantry_item.name = "Milk"
        pantry_item.quantity = 5.0

        rate = await _calculate_consumption_rate(mock_db, uuid4(), pantry_item)
        assert rate["daily_rate"] == 0.0
        assert rate["days_until_depletion"] == float("inf")

    @pytest.mark.asyncio
    async def test_with_consumption(self):
        from unittest.mock import AsyncMock

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar.return_value = 14  # 14 logs in 14 days = 1/day
        mock_db.execute.return_value = mock_result

        pantry_item = MagicMock()
        pantry_item.name = "Eggs"
        pantry_item.quantity = 5.0

        rate = await _calculate_consumption_rate(mock_db, uuid4(), pantry_item)
        assert rate["daily_rate"] == 1.0
        assert rate["days_until_depletion"] == 5.0

    @pytest.mark.asyncio
    async def test_high_consumption_rate(self):
        from unittest.mock import AsyncMock

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar.return_value = 28  # 28 logs in 14 days = 2/day
        mock_db.execute.return_value = mock_result

        pantry_item = MagicMock()
        pantry_item.name = "Water"
        pantry_item.quantity = 4.0

        rate = await _calculate_consumption_rate(mock_db, uuid4(), pantry_item)
        assert rate["daily_rate"] == 2.0
        assert rate["days_until_depletion"] == 2.0
