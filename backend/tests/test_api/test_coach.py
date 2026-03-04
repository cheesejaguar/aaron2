from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from httpx import AsyncClient

from app.schemas.ai import ChatResponse, InsightsResponse


class TestCoachChat:
    @pytest.mark.asyncio
    async def test_chat(self, client: AsyncClient):
        mock_response = ChatResponse(
            reply="Based on your blood pressure readings, I recommend reducing sodium intake.",
            conversation_id=str(uuid4()),
        )
        with patch(
            "app.api.v1.coach.chat",
            new_callable=AsyncMock,
            return_value=mock_response,
        ):
            resp = await client.post(
                "/api/v1/coach/chat",
                json={"message": "How can I lower my blood pressure?"},
            )
            assert resp.status_code == 200
            data = resp.json()
            assert "sodium" in data["reply"]
            assert "conversation_id" in data

    @pytest.mark.asyncio
    async def test_chat_with_conversation_id(self, client: AsyncClient):
        conv_id = str(uuid4())
        mock_response = ChatResponse(reply="Great progress!", conversation_id=conv_id)
        with patch(
            "app.api.v1.coach.chat",
            new_callable=AsyncMock,
            return_value=mock_response,
        ):
            resp = await client.post(
                "/api/v1/coach/chat",
                json={"message": "Thanks!", "conversation_id": conv_id},
            )
            assert resp.status_code == 200
            assert resp.json()["conversation_id"] == conv_id

    @pytest.mark.asyncio
    async def test_chat_missing_message(self, client: AsyncClient):
        resp = await client.post("/api/v1/coach/chat", json={})
        assert resp.status_code == 422



class TestInsights:
    @pytest.mark.asyncio
    async def test_get_insights(self, client: AsyncClient):
        mock_response = InsightsResponse(
            insights=[
                {"type": "bp", "message": "Your BP has been trending down"},
                {"type": "nutrition", "message": "Increase potassium intake"},
            ]
        )
        with patch(
            "app.api.v1.coach.generate_insights",
            new_callable=AsyncMock,
            return_value=mock_response,
        ):
            resp = await client.get("/api/v1/coach/insights")
            assert resp.status_code == 200
            data = resp.json()
            assert len(data["insights"]) == 2

