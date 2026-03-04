from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

from app.models.user import User
from app.schemas.receipt import ReceiptParseRequest
from app.services.receipt_parser import parse_receipt_text


@pytest.fixture
def mock_user():
    return User(
        id=uuid4(),
        email="test@test.com",
        name="Test",
        hashed_password="hashed",
    )


class TestParseReceiptText:
    @pytest.mark.asyncio
    async def test_parse_receipt(self, mock_user):
        parsed_items = [
            {
                "name": "Organic Milk",
                "category": "dairy",
                "quantity": 1,
                "unit": "gallon",
                "estimated_nutrition": {
                    "calories": 150,
                    "protein_g": 8,
                    "carbs_g": 12,
                    "fat_g": 8,
                    "fiber_g": 0,
                    "sodium_mg": 120,
                },
            },
            {
                "name": "Eggs",
                "category": "protein",
                "quantity": 12,
                "unit": "count",
                "estimated_nutrition": {
                    "calories": 70,
                    "protein_g": 6,
                    "carbs_g": 0,
                    "fat_g": 5,
                    "fiber_g": 0,
                    "sodium_mg": 70,
                },
            },
        ]

        db = AsyncMock()
        db.flush = AsyncMock()
        db.add = AsyncMock()

        request = ReceiptParseRequest(raw_text="Organic Milk $4.99\nEggs $3.49")

        with patch("app.services.receipt_parser.ai_service") as mock_ai:
            mock_ai.complete_json = AsyncMock(return_value={"items": parsed_items})

            result = await parse_receipt_text(db, mock_user, request)
            assert len(result.items) == 2
            assert result.items[0]["name"] == "Organic Milk"
            assert result.pantry_items_created == 2

    @pytest.mark.asyncio
    async def test_parse_receipt_direct_list(self, mock_user):
        """When AI returns a list instead of dict with 'items' key."""
        parsed_items = [
            {"name": "Bread", "category": "grains", "quantity": 1},
        ]

        db = AsyncMock()
        db.flush = AsyncMock()
        db.add = AsyncMock()

        request = ReceiptParseRequest(raw_text="Bread $2.99")

        with patch("app.services.receipt_parser.ai_service") as mock_ai:
            mock_ai.complete_json = AsyncMock(return_value=parsed_items)

            result = await parse_receipt_text(db, mock_user, request)
            assert len(result.items) == 1
            assert result.pantry_items_created == 1
