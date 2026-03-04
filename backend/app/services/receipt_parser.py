from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.pantry import PantryItem
from app.models.receipt import PurchaseReceipt
from app.models.user import User
from app.schemas.receipt import ReceiptParseRequest, ReceiptParseResponse
from app.services.ai_service import TaskType, ai_service

SYSTEM_PROMPT = """You are a grocery receipt parser. Extract items from the receipt text.
Return a JSON array of objects with these fields:
- name: item name (string)
- category: one of "produce", "dairy", "meat", "grains", "snacks",
  "beverages", "frozen", "canned", "condiments", "other" (string)
- quantity: number of items (number, default 1)
- unit: unit of measurement if applicable (string or null)
- estimated_price: price if visible (number or null)
- estimated_nutrition: estimated per-serving nutrition (object or null) with fields:
  calories (number), protein_g (number), carbs_g (number), fat_g (number),
  fiber_g (number), sodium_mg (number)

Only return the JSON array, no other text."""


async def parse_receipt_text(
    db: AsyncSession, user: User, data: ReceiptParseRequest
) -> ReceiptParseResponse:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": data.raw_text},
    ]

    items = await ai_service.complete_json(db, str(user.id), TaskType.RECEIPT_PARSE, messages)

    if not isinstance(items, list):
        items = items.get("items", [])

    # Save receipt
    receipt = PurchaseReceipt(
        user_id=user.id,
        raw_text=data.raw_text,
        parsed_at=datetime.utcnow(),
        source=data.source,
        items_json=items,
    )
    db.add(receipt)

    # Create pantry items
    created = 0
    for item_data in items:
        pantry_item = PantryItem(
            user_id=user.id,
            name=item_data.get("name", "Unknown"),
            category=item_data.get("category"),
            quantity=item_data.get("quantity", 1),
            unit=item_data.get("unit"),
            nutrition_json=item_data.get("estimated_nutrition"),
        )
        db.add(pantry_item)
        created += 1

    await db.flush()
    return ReceiptParseResponse(items=items, pantry_items_created=created)
