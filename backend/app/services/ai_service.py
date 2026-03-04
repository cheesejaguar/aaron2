import hashlib
import json
import logging
from enum import StrEnum

from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.core.redis import get_redis
from app.models.ai import AIUsageLog

logger = logging.getLogger(__name__)

CACHE_TTL = 86400  # 24 hours
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX = 10  # requests per window


class AIModel(StrEnum):
    CLAUDE_HEAVY = "anthropic/claude-sonnet-4-6"
    MINIMAX = "minimax/minimax-m2.5"


class TaskType(StrEnum):
    RECEIPT_PARSE = "receipt_parse"
    RECIPE_GENERATE = "recipe_generate"
    RECIPE_IMPORT = "recipe_import"
    MEAL_PLAN_SUGGEST = "meal_plan_suggest"
    COACH_CHAT = "coach_chat"
    INSIGHTS = "insights"
    NUTRITION_LOOKUP = "nutrition_lookup"
    SHOPPING_LIST_DESCRIPTION = "shopping_list_description"


FALLBACK_MESSAGES: dict[TaskType, str] = {
    TaskType.RECEIPT_PARSE: "[]",
    TaskType.RECIPE_GENERATE: (
        '{"title": "Unable to generate recipe",'
        ' "ingredients_json": [],'
        ' "steps_json": ["Please try again later."]}'
    ),
    TaskType.RECIPE_IMPORT: (
        '{"title": "Import failed",'
        ' "ingredients_json": [],'
        ' "steps_json": ["Could not import. Try again."]}'
    ),
    TaskType.MEAL_PLAN_SUGGEST: '{"entries": []}',
    TaskType.COACH_CHAT: (
        "I'm sorry, I'm having trouble responding right now. Please try again in a moment."
    ),
    TaskType.INSIGHTS: '{"insights": []}',
    TaskType.NUTRITION_LOOKUP: ('{"calories": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0}'),
    TaskType.SHOPPING_LIST_DESCRIPTION: "",
}

TASK_MODEL_MAP: dict[TaskType, AIModel] = {
    TaskType.RECEIPT_PARSE: AIModel.CLAUDE_HEAVY,
    TaskType.RECIPE_GENERATE: AIModel.CLAUDE_HEAVY,
    TaskType.RECIPE_IMPORT: AIModel.MINIMAX,
    TaskType.MEAL_PLAN_SUGGEST: AIModel.CLAUDE_HEAVY,
    TaskType.COACH_CHAT: AIModel.CLAUDE_HEAVY,
    TaskType.INSIGHTS: AIModel.CLAUDE_HEAVY,
    TaskType.NUTRITION_LOOKUP: AIModel.MINIMAX,
    TaskType.SHOPPING_LIST_DESCRIPTION: AIModel.MINIMAX,
}


class AIService:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.openrouter_api_key,
            base_url="https://openrouter.ai/api/v1",
            default_headers={
                "X-Title": "Aaron 2.0",
                "HTTP-Referer": "http://localhost:3000",
            },
        )

    def _cache_key(self, task_type: str, messages: list[dict]) -> str:
        content = json.dumps({"task": task_type, "messages": messages}, sort_keys=True)
        return f"ai_cache:{hashlib.sha256(content.encode()).hexdigest()}"

    async def _check_rate_limit(self, user_id: str) -> None:
        redis = get_redis()
        key = f"ai_rate:{user_id}"
        count = await redis.incr(key)
        if count == 1:
            await redis.expire(key, RATE_LIMIT_WINDOW)
        if count > RATE_LIMIT_MAX:
            raise ValueError("Rate limit exceeded. Please wait before making more AI requests.")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    async def _completion(
        self,
        model: str,
        messages: list[dict],
        response_format: dict | None = None,
    ) -> dict:
        kwargs: dict = {
            "model": model,
            "messages": messages,
        }
        if response_format:
            kwargs["response_format"] = response_format

        response = await self.client.chat.completions.create(**kwargs)
        choice = response.choices[0]
        return {
            "content": choice.message.content,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
            },
        }

    async def _log_usage(
        self,
        db: AsyncSession,
        user_id: str,
        model: str,
        usage: dict,
        task_type: str,
    ) -> None:
        log = AIUsageLog(
            user_id=user_id,
            model=model,
            prompt_tokens=usage.get("prompt_tokens", 0),
            completion_tokens=usage.get("completion_tokens", 0),
            cost_usd=0.0,  # Could calculate based on model pricing
            task_type=task_type,
        )
        db.add(log)

    async def complete(
        self,
        db: AsyncSession,
        user_id: str,
        task_type: TaskType,
        messages: list[dict],
        use_cache: bool = True,
    ) -> str:
        await self._check_rate_limit(user_id)

        model = TASK_MODEL_MAP[task_type].value
        redis = get_redis()

        # Check cache
        if use_cache:
            cache_key = self._cache_key(task_type.value, messages)
            cached = await redis.get(cache_key)
            if cached:
                return cached

        # Call AI with fallback
        try:
            result = await self._completion(model, messages)
        except Exception:
            logger.exception("AI completion failed for task_type=%s", task_type)
            return FALLBACK_MESSAGES.get(task_type, "An error occurred. Please try again.")
        content = result["content"]

        # Cache result
        if use_cache:
            await redis.set(cache_key, content, ex=CACHE_TTL)

        # Log usage
        await self._log_usage(db, user_id, model, result["usage"], task_type.value)

        return content

    async def complete_json(
        self,
        db: AsyncSession,
        user_id: str,
        task_type: TaskType,
        messages: list[dict],
        use_cache: bool = True,
    ) -> dict:
        content = await self.complete(db, user_id, task_type, messages, use_cache=use_cache)
        # Try to parse JSON from the response
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
                return json.loads(json_str)
            if "```" in content:
                json_str = content.split("```")[1].split("```")[0].strip()
                return json.loads(json_str)
            return {"error": content}


ai_service = AIService()
