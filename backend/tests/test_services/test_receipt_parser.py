from sqlmodel import select

from app.models.pantry import PantryItem
from app.models.receipt import PurchaseReceipt
from app.schemas.receipt import ReceiptParseRequest
from app.services.receipt_parser import SYSTEM_PROMPT, parse_receipt_text

MILK = {
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
}
EGGS = {"name": "Eggs", "category": "protein", "quantity": 12, "unit": "count"}


async def _pantry(db_session, user_id):
    result = await db_session.execute(
        select(PantryItem).where(PantryItem.user_id == user_id).order_by(PantryItem.name)
    )
    return result.scalars().all()


class TestParseReceiptText:
    async def test_items_wrapped_in_object(self, db_session, test_user, openrouter):
        openrouter.reply({"items": [MILK, EGGS]})
        raw = "Organic Milk $4.99\nEggs $3.49"

        result = await parse_receipt_text(db_session, test_user, ReceiptParseRequest(raw_text=raw))

        assert result.items == [MILK, EGGS]
        assert result.pantry_items_created == 2
        assert openrouter.last_messages == [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": raw},
        ]

        eggs, milk = await _pantry(db_session, test_user.id)
        assert (milk.name, milk.category, milk.quantity, milk.unit) == (
            "Organic Milk",
            "dairy",
            1,
            "gallon",
        )
        assert milk.nutrition_json == MILK["estimated_nutrition"]
        assert (eggs.quantity, eggs.unit, eggs.nutrition_json) == (12, "count", None)

        (receipt,) = (
            (
                await db_session.execute(
                    select(PurchaseReceipt).where(PurchaseReceipt.user_id == test_user.id)
                )
            )
            .scalars()
            .all()
        )
        assert receipt.raw_text == raw
        assert receipt.items_json == [MILK, EGGS]
        assert receipt.parsed_at is not None

    async def test_direct_list_with_defaults(self, db_session, test_user, openrouter):
        """When the model returns a bare list, and items omit optional fields."""
        openrouter.reply([{"name": "Bread", "category": "grains"}, {}])

        result = await parse_receipt_text(
            db_session, test_user, ReceiptParseRequest(raw_text="Bread $2.99")
        )

        assert result.pantry_items_created == 2
        bread, unknown = await _pantry(db_session, test_user.id)
        assert (bread.name, bread.category, bread.quantity) == ("Bread", "grains", 1)
        assert (unknown.name, unknown.category) == ("Unknown", None)

    async def test_api_failure_creates_no_items(self, db_session, test_user, openrouter):
        openrouter.fail(500, times=3)

        result = await parse_receipt_text(
            db_session, test_user, ReceiptParseRequest(raw_text="Bread $2.99")
        )

        assert result.items == []
        assert result.pantry_items_created == 0
        assert await _pantry(db_session, test_user.id) == []
