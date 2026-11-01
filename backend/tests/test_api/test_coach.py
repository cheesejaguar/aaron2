from uuid import UUID

import pytest
from httpx import AsyncClient

from app.models.ai import AIConversation


class TestCoachChat:
    @pytest.mark.asyncio
    async def test_chat(self, client: AsyncClient, db_session, test_user, openrouter):
        openrouter.reply(
            "Based on your blood pressure readings, I recommend reducing sodium intake."
        )

        resp = await client.post(
            "/api/v1/coach/chat",
            json={"message": "How can I lower my blood pressure?"},
        )

        assert resp.status_code == 200
        data = resp.json()
        assert data["reply"] == (
            "Based on your blood pressure readings, I recommend reducing sodium intake."
        )
        assert openrouter.last_messages[-1] == {
            "role": "user",
            "content": "How can I lower my blood pressure?",
        }
        conv = await db_session.get(AIConversation, UUID(data["conversation_id"]))
        assert conv.user_id == test_user.id

    @pytest.mark.asyncio
    async def test_chat_with_conversation_id(self, client: AsyncClient, openrouter):
        openrouter.reply("Hello!").reply("Great progress!")
        first = await client.post("/api/v1/coach/chat", json={"message": "Hi"})
        conv_id = first.json()["conversation_id"]

        resp = await client.post(
            "/api/v1/coach/chat",
            json={"message": "Thanks!", "conversation_id": conv_id},
        )

        assert resp.status_code == 200
        assert resp.json() == {"reply": "Great progress!", "conversation_id": conv_id}
        assert [m["content"] for m in openrouter.last_messages[1:]] == [
            "Hi",
            "Hello!",
            "Thanks!",
        ]

    @pytest.mark.asyncio
    async def test_chat_missing_message(self, client: AsyncClient):
        resp = await client.post("/api/v1/coach/chat", json={})
        assert resp.status_code == 422


class TestInsights:
    @pytest.mark.asyncio
    async def test_get_insights(self, client: AsyncClient, openrouter):
        insights = [
            {"type": "bp", "message": "Your BP has been trending down"},
            {"type": "nutrition", "message": "Increase potassium intake"},
        ]
        openrouter.reply({"insights": insights})

        resp = await client.get("/api/v1/coach/insights")

        assert resp.status_code == 200
        assert resp.json() == {"insights": insights}
