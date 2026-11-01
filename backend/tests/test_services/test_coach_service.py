from datetime import datetime, timedelta
from uuid import UUID, uuid4

from app.models.ai import AIConversation
from app.models.food_log import FoodLog
from app.models.health import BloodPressureLog, WeightLog
from app.schemas.ai import ChatRequest
from app.services.coach_service import chat, generate_insights


class TestChat:
    async def test_new_conversation_without_data(self, db_session, test_user, openrouter):
        openrouter.reply("Reduce sodium intake and exercise regularly.")

        result = await chat(
            db_session, test_user, ChatRequest(message="How can I lower my blood pressure?")
        )

        assert result.reply == "Reduce sodium intake and exercise regularly."
        system, user = openrouter.last_messages
        assert system["role"] == "system"
        assert "No health data recorded yet." in system["content"]
        assert user == {"role": "user", "content": "How can I lower my blood pressure?"}

        conv = await db_session.get(AIConversation, UUID(result.conversation_id))
        assert conv is not None
        assert conv.user_id == test_user.id
        assert conv.messages_json == [
            {"role": "user", "content": "How can I lower my blood pressure?"},
            {"role": "assistant", "content": "Reduce sodium intake and exercise regularly."},
        ]

    async def test_health_context_in_system_prompt(self, db_session, test_user, openrouter):
        now = datetime.utcnow()
        test_user.health_goals_json = {"target_weight": 175}
        db_session.add_all(
            [
                BloodPressureLog(
                    user_id=test_user.id,
                    systolic=120,
                    diastolic=80,
                    measured_at=now - timedelta(days=1),
                ),
                BloodPressureLog(user_id=test_user.id, systolic=135, diastolic=88, measured_at=now),
                WeightLog(user_id=test_user.id, weight_lbs=190.5, measured_at=now),
                FoodLog(
                    user_id=test_user.id, meal_type="lunch", food_name="Oatmeal", logged_at=now
                ),
            ]
        )
        await db_session.flush()
        openrouter.reply("ok")

        await chat(db_session, test_user, ChatRequest(message="Hi"))

        system = openrouter.last_messages[0]["content"]
        assert "Latest BP: 135/88" in system  # most recent reading, not the older one
        assert "Latest weight: 190.5 lbs" in system
        assert "Recent foods: Oatmeal" in system
        assert 'Health goals: {"target_weight": 175}' in system

    async def test_continues_existing_conversation(self, db_session, test_user, openrouter):
        openrouter.reply("First answer").reply("Second answer")

        first = await chat(db_session, test_user, ChatRequest(message="First question"))
        second = await chat(
            db_session,
            test_user,
            ChatRequest(message="Second question", conversation_id=first.conversation_id),
        )

        assert second.conversation_id == first.conversation_id
        # The prior turn is replayed to the model
        assert openrouter.last_messages[1:] == [
            {"role": "user", "content": "First question"},
            {"role": "assistant", "content": "First answer"},
            {"role": "user", "content": "Second question"},
        ]

        # Both turns are persisted
        db_session.expire_all()
        conv = await db_session.get(AIConversation, UUID(first.conversation_id))
        assert [m["content"] for m in conv.messages_json] == [
            "First question",
            "First answer",
            "Second question",
            "Second answer",
        ]

    async def test_unknown_conversation_id_starts_new_one(self, db_session, test_user, openrouter):
        openrouter.reply("You're welcome!")
        unknown = str(uuid4())

        result = await chat(
            db_session, test_user, ChatRequest(message="Thanks!", conversation_id=unknown)
        )

        assert result.reply == "You're welcome!"
        assert result.conversation_id != unknown
        assert len(openrouter.last_messages) == 2  # system + user, no history

    async def test_cannot_continue_another_users_conversation(
        self, db_session, test_user, second_user, openrouter
    ):
        other = AIConversation(
            user_id=second_user.id,
            messages_json=[{"role": "user", "content": "private"}],
        )
        db_session.add(other)
        await db_session.flush()
        openrouter.reply("hello")

        result = await chat(
            db_session, test_user, ChatRequest(message="hi", conversation_id=str(other.id))
        )

        assert result.conversation_id != str(other.id)
        assert all(m["content"] != "private" for m in openrouter.last_messages)

    async def test_api_failure_returns_fallback_reply(self, db_session, test_user, openrouter):
        openrouter.fail(500, times=3)
        result = await chat(db_session, test_user, ChatRequest(message="Hi"))
        assert "having trouble responding" in result.reply


class TestGenerateInsights:
    async def test_returns_parsed_insights(self, db_session, test_user, openrouter):
        insight = {
            "title": "Start tracking",
            "description": "Begin logging",
            "category": "health",
            "priority": "high",
        }
        openrouter.reply({"insights": [insight]})

        result = await generate_insights(db_session, test_user)

        assert result.insights == [insight]
        user_msg = openrouter.last_messages[1]["content"]
        assert user_msg == "Generate insights based on:\nNo health data recorded yet."

    async def test_fallback_gives_empty_insights(self, db_session, test_user, openrouter):
        openrouter.fail(500, times=3)
        result = await generate_insights(db_session, test_user)
        assert result.insights == []

    async def test_insights_in_markdown_code_block(self, db_session, test_user, openrouter):
        openrouter.reply('```json\n{"insights": [{"title": "Eat more fiber"}]}\n```')
        result = await generate_insights(db_session, test_user)
        assert result.insights == [{"title": "Eat more fiber"}]

    async def test_recent_data_sent_to_model(self, db_session, test_user, openrouter):
        db_session.add(
            BloodPressureLog(
                user_id=test_user.id, systolic=142, diastolic=91, measured_at=datetime.utcnow()
            )
        )
        await db_session.flush()
        openrouter.reply({"insights": []})

        await generate_insights(db_session, test_user)

        assert "Latest BP: 142/91" in openrouter.last_messages[1]["content"]

    async def test_ignores_other_users_data(self, db_session, test_user, second_user, openrouter):
        db_session.add(
            BloodPressureLog(
                user_id=second_user.id, systolic=180, diastolic=110, measured_at=datetime.utcnow()
            )
        )
        await db_session.flush()
        openrouter.reply({"insights": []})

        await generate_insights(db_session, test_user)

        assert "180/110" not in openrouter.last_messages[1]["content"]
