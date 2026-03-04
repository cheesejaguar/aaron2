from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from app.models.user import User
from app.schemas.ai import ChatRequest
from app.services.coach_service import chat, generate_insights


@pytest.fixture
def mock_user():
    user = User(
        id=uuid4(),
        email="test@test.com",
        name="Test User",
        hashed_password="hashed",
    )
    user.health_goals_json = None
    return user


def _mock_empty_db():
    """Create a mock DB where scalars().all() returns [] and scalar_one_or_none() returns None."""
    db = AsyncMock()

    def make_empty_result():
        result = MagicMock()
        scalars = MagicMock()
        scalars.all.return_value = []
        result.scalars.return_value = scalars
        result.scalar_one_or_none.return_value = None
        return result

    db.execute = AsyncMock(side_effect=lambda *a, **kw: make_empty_result())
    db.flush = AsyncMock()
    # Use MagicMock for db.add since it's not awaited
    db.add = MagicMock()
    return db


class TestChat:
    @pytest.mark.asyncio
    async def test_chat_new_conversation(self, mock_user):
        db = _mock_empty_db()
        request = ChatRequest(message="How can I lower my blood pressure?")

        with patch("app.services.coach_service.ai_service") as mock_ai:
            mock_ai.complete = AsyncMock(
                return_value="Reduce sodium intake and exercise regularly."
            )
            result = await chat(db, mock_user, request)

            assert result.reply == "Reduce sodium intake and exercise regularly."
            assert result.conversation_id is not None

    @pytest.mark.asyncio
    async def test_chat_with_conversation_id(self, mock_user):
        db = _mock_empty_db()
        conv_id = str(uuid4())
        request = ChatRequest(message="Thanks!", conversation_id=conv_id)

        with patch("app.services.coach_service.ai_service") as mock_ai:
            mock_ai.complete = AsyncMock(return_value="You're welcome!")
            result = await chat(db, mock_user, request)

            assert result.reply == "You're welcome!"


class TestGenerateInsights:
    @pytest.mark.asyncio
    async def test_generate_insights_empty_data(self, mock_user):
        db = _mock_empty_db()

        with patch("app.services.coach_service.ai_service") as mock_ai:
            mock_ai.complete_json = AsyncMock(
                return_value={
                    "insights": [
                        {
                            "title": "Start tracking",
                            "description": "Begin logging",
                            "category": "general",
                            "priority": "high",
                        }
                    ]
                }
            )
            result = await generate_insights(db, mock_user)

            assert len(result.insights) == 1
            assert result.insights[0]["title"] == "Start tracking"
