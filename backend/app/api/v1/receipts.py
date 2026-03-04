from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.receipt import ReceiptParseRequest, ReceiptParseResponse
from app.services.receipt_parser import parse_receipt_text

router = APIRouter(prefix="/receipts", tags=["receipts"])


@router.post("/parse", response_model=ReceiptParseResponse)
async def parse_receipt(
    data: ReceiptParseRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Parse grocery receipt text and create pantry items."""
    return await parse_receipt_text(db, current_user, data)
