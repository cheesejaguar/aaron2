import pytest
from pydantic import ValidationError

from app.schemas.pantry import PantryConsumeRequest, PantryItemCreate, PantryItemUpdate


class TestPantryItemCreate:
    def test_minimal_create(self):
        item = PantryItemCreate(name="Apples")
        assert item.name == "Apples"
        assert item.quantity == 1.0
        assert item.category is None

    def test_full_create(self):
        item = PantryItemCreate(
            name="Milk",
            category="dairy",
            quantity=2.0,
            unit="gallons",
            purchase_date="2024-01-15",
            estimated_expiry="2024-01-29",
            low_stock_threshold=0.5,
        )
        assert item.unit == "gallons"
        assert item.low_stock_threshold == 0.5

    def test_missing_name_rejected(self):
        with pytest.raises(ValidationError):
            PantryItemCreate()  # type: ignore[call-arg]


class TestPantryItemUpdate:
    def test_partial_update(self):
        update = PantryItemUpdate(quantity=5.0)
        data = update.model_dump(exclude_unset=True)
        assert data == {"quantity": 5.0}

    def test_empty_update_allowed(self):
        update = PantryItemUpdate()
        assert update.model_dump(exclude_unset=True) == {}


class TestPantryConsumeRequest:
    def test_consume_request(self):
        req = PantryConsumeRequest(quantity=2.5)
        assert req.quantity == 2.5

    def test_missing_quantity_rejected(self):
        with pytest.raises(ValidationError):
            PantryConsumeRequest()  # type: ignore[call-arg]
