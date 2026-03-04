import json
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.ai import AIConversation
from app.models.food_log import FoodLog
from app.models.health import BloodPressureLog, WeightLog
from app.models.user import User
from app.schemas.ai import ChatRequest, ChatResponse, InsightsResponse
from app.services.ai_service import TaskType, ai_service

COACH_SYSTEM = """You are Aaron's AI Health Coach, specializing in:
- DASH diet guidance for lowering blood pressure
- Heart-healthy eating to reduce cholesterol
- Sustainable weight loss strategies
- Grocery and meal planning optimization

You have access to the user's health data context provided below.
Be encouraging, specific, and evidence-based in your advice.
Keep responses concise but actionable."""

INSIGHTS_SYSTEM = """You are a health data analyst. Based on the user's recent health metrics,
food logs, and pantry data, generate 3-5 actionable insights.
Return JSON: {"insights": [{"title": "...", "description": "...",
"category": "nutrition|exercise|health|shopping",
"priority": "high|medium|low"}]}"""


async def _get_health_context(db: AsyncSession, user: User) -> str:
    """Build context string from user's recent health data."""
    parts = []

    # Recent BP
    bp_result = await db.execute(
        select(BloodPressureLog)
        .where(BloodPressureLog.user_id == user.id)
        .order_by(BloodPressureLog.measured_at.desc())  # type: ignore[attr-defined]
        .limit(5)
    )
    bp_logs = bp_result.scalars().all()
    if bp_logs:
        latest = bp_logs[0]
        parts.append(f"Latest BP: {latest.systolic}/{latest.diastolic}")

    # Recent Weight
    weight_result = await db.execute(
        select(WeightLog)
        .where(WeightLog.user_id == user.id)
        .order_by(WeightLog.measured_at.desc())  # type: ignore[attr-defined]
        .limit(5)
    )
    weight_logs = weight_result.scalars().all()
    if weight_logs:
        parts.append(f"Latest weight: {weight_logs[0].weight_lbs} lbs")

    # Recent food logs
    food_result = await db.execute(
        select(FoodLog)
        .where(FoodLog.user_id == user.id)
        .order_by(FoodLog.logged_at.desc())  # type: ignore[attr-defined]
        .limit(10)
    )
    food_logs = food_result.scalars().all()
    if food_logs:
        foods = [f.food_name for f in food_logs]
        parts.append(f"Recent foods: {', '.join(foods)}")

    if user.health_goals_json:
        parts.append(f"Health goals: {json.dumps(user.health_goals_json)}")

    return "\n".join(parts) if parts else "No health data recorded yet."


async def chat(db: AsyncSession, user: User, data: ChatRequest) -> ChatResponse:
    # Load or create conversation
    conversation = None
    if data.conversation_id:
        result = await db.execute(
            select(AIConversation).where(
                AIConversation.id == UUID(data.conversation_id),
                AIConversation.user_id == user.id,
            )
        )
        conversation = result.scalar_one_or_none()

    if not conversation:
        conversation = AIConversation(
            user_id=user.id,
            messages_json=[],
        )
        db.add(conversation)
        await db.flush()

    # Build messages
    health_context = await _get_health_context(db, user)
    system_msg = f"{COACH_SYSTEM}\n\nUser health context:\n{health_context}"

    messages = [{"role": "system", "content": system_msg}]
    if conversation.messages_json:
        messages.extend(conversation.messages_json[-10:])  # Keep last 10 messages
    messages.append({"role": "user", "content": data.message})

    reply = await ai_service.complete(
        db, str(user.id), TaskType.COACH_CHAT, messages, use_cache=False
    )

    # Save conversation
    if not conversation.messages_json:
        conversation.messages_json = []
    conversation.messages_json.append({"role": "user", "content": data.message})
    conversation.messages_json.append({"role": "assistant", "content": reply})
    await db.flush()

    return ChatResponse(reply=reply, conversation_id=str(conversation.id))


async def generate_insights(db: AsyncSession, user: User) -> InsightsResponse:
    health_context = await _get_health_context(db, user)

    messages = [
        {"role": "system", "content": INSIGHTS_SYSTEM},
        {"role": "user", "content": f"Generate insights based on:\n{health_context}"},
    ]

    result = await ai_service.complete_json(db, str(user.id), TaskType.INSIGHTS, messages)

    return InsightsResponse(insights=result.get("insights", []))
