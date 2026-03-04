from typing import Any

from pydantic import BaseModel


class ReceiptParseRequest(BaseModel):
    raw_text: str
    source: str | None = None


class ReceiptParseResponse(BaseModel):
    items: list[dict[str, Any]]
    pantry_items_created: int
