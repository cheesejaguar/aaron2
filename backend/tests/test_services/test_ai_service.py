import pytest
from sqlmodel import select

from app.models.ai import AIUsageLog
from app.services.ai_service import (
    CACHE_TTL,
    FALLBACK_MESSAGES,
    RATE_LIMIT_MAX,
    RATE_LIMIT_WINDOW,
    TASK_MODEL_MAP,
    TaskType,
    ai_service,
)

MESSAGES = [{"role": "user", "content": "hi"}]


async def _usage_logs(db_session, user_id):
    result = await db_session.execute(select(AIUsageLog).where(AIUsageLog.user_id == user_id))
    return result.scalars().all()


class TestCacheKey:
    def test_deterministic(self):
        key1 = ai_service._cache_key("task", [{"role": "user", "content": "hi"}])
        key2 = ai_service._cache_key("task", [{"role": "user", "content": "hi"}])
        assert key1 == key2
        assert key1.startswith("ai_cache:")

    def test_different_tasks(self):
        key1 = ai_service._cache_key("task1", MESSAGES)
        key2 = ai_service._cache_key("task2", MESSAGES)
        assert key1 != key2

    def test_different_messages(self):
        key1 = ai_service._cache_key("task", [{"role": "user", "content": "a"}])
        key2 = ai_service._cache_key("task", [{"role": "user", "content": "b"}])
        assert key1 != key2


class TestRateLimit:
    async def test_first_request_counts_and_sets_window(self, redis):
        await ai_service._check_rate_limit("user-1")
        assert await redis.get("ai_rate:user-1") == "1"
        ttl = await redis.ttl("ai_rate:user-1")
        assert 0 < ttl <= RATE_LIMIT_WINDOW

    async def test_allows_up_to_limit(self, redis):
        for _ in range(RATE_LIMIT_MAX):
            await ai_service._check_rate_limit("user-1")
        assert await redis.get("ai_rate:user-1") == str(RATE_LIMIT_MAX)

    async def test_over_limit_raises(self, redis):
        for _ in range(RATE_LIMIT_MAX):
            await ai_service._check_rate_limit("user-1")
        with pytest.raises(ValueError, match="Rate limit exceeded"):
            await ai_service._check_rate_limit("user-1")

    async def test_limits_are_per_user(self, redis):
        await redis.set("ai_rate:user-1", RATE_LIMIT_MAX)
        await ai_service._check_rate_limit("user-2")  # unaffected by user-1's count
        with pytest.raises(ValueError):
            await ai_service._check_rate_limit("user-1")


class TestComplete:
    async def test_cache_hit_skips_api(self, db_session, test_user, redis, openrouter):
        await redis.set(ai_service._cache_key(TaskType.COACH_CHAT.value, MESSAGES), "cached")

        result = await ai_service.complete(
            db_session, str(test_user.id), TaskType.COACH_CHAT, MESSAGES
        )

        assert result == "cached"
        assert openrouter.requests == []
        assert await _usage_logs(db_session, test_user.id) == []

    async def test_cache_miss_calls_api_caches_and_logs_usage(
        self, db_session, test_user, redis, openrouter
    ):
        openrouter.reply('{"result": "test"}', prompt_tokens=11, completion_tokens=22)

        result = await ai_service.complete(
            db_session, str(test_user.id), TaskType.NUTRITION_LOOKUP, MESSAGES
        )
        await db_session.flush()

        assert result == '{"result": "test"}'

        # Request sent to OpenRouter uses the task's model and the given messages
        assert len(openrouter.requests) == 1
        req = openrouter.requests[0]
        assert req["url"] == "https://openrouter.ai/api/v1/chat/completions"
        assert req["json"]["model"] == TASK_MODEL_MAP[TaskType.NUTRITION_LOOKUP].value
        assert req["json"]["messages"] == MESSAGES
        assert req["headers"]["x-title"] == "Aaron 2.0"

        # Response cached with a TTL
        key = ai_service._cache_key(TaskType.NUTRITION_LOOKUP.value, MESSAGES)
        assert await redis.get(key) == '{"result": "test"}'
        assert 0 < await redis.ttl(key) <= CACHE_TTL

        # Usage recorded from the API response
        (log,) = await _usage_logs(db_session, test_user.id)
        assert log.model == TASK_MODEL_MAP[TaskType.NUTRITION_LOOKUP].value
        assert log.prompt_tokens == 11
        assert log.completion_tokens == 22
        assert log.task_type == "nutrition_lookup"

    async def test_second_call_served_from_cache(self, db_session, test_user, openrouter):
        openrouter.reply("first")
        uid = str(test_user.id)
        assert await ai_service.complete(db_session, uid, TaskType.INSIGHTS, MESSAGES) == "first"
        assert await ai_service.complete(db_session, uid, TaskType.INSIGHTS, MESSAGES) == "first"
        assert len(openrouter.requests) == 1

    async def test_no_cache_neither_reads_nor_writes(
        self, db_session, test_user, redis, openrouter
    ):
        key = ai_service._cache_key(TaskType.COACH_CHAT.value, MESSAGES)
        await redis.set(key, "stale")
        openrouter.reply("fresh")

        result = await ai_service.complete(
            db_session, str(test_user.id), TaskType.COACH_CHAT, MESSAGES, use_cache=False
        )

        assert result == "fresh"
        assert len(openrouter.requests) == 1
        assert await redis.get(key) == "stale"

    async def test_rate_limited_before_calling_api(self, db_session, test_user, redis, openrouter):
        await redis.set(f"ai_rate:{test_user.id}", RATE_LIMIT_MAX)
        with pytest.raises(ValueError, match="Rate limit exceeded"):
            await ai_service.complete(db_session, str(test_user.id), TaskType.COACH_CHAT, MESSAGES)
        assert openrouter.requests == []


class TestCompleteJson:
    async def test_valid_json(self, db_session, test_user, openrouter):
        openrouter.reply('{"result": "test"}')
        result = await ai_service.complete_json(
            db_session, str(test_user.id), TaskType.RECIPE_GENERATE, MESSAGES
        )
        assert result == {"result": "test"}

    async def test_json_in_json_code_block(self, db_session, test_user, openrouter):
        openrouter.reply('Here is the result:\n```json\n{"key": "value"}\n```')
        result = await ai_service.complete_json(
            db_session, str(test_user.id), TaskType.RECIPE_GENERATE, MESSAGES
        )
        assert result == {"key": "value"}

    async def test_json_in_plain_code_block(self, db_session, test_user, openrouter):
        openrouter.reply('```\n{"key": 1}\n```')
        result = await ai_service.complete_json(
            db_session, str(test_user.id), TaskType.RECIPE_GENERATE, MESSAGES
        )
        assert result == {"key": 1}

    async def test_invalid_json_returns_error_dict(self, db_session, test_user, openrouter):
        openrouter.reply("not json at all")
        result = await ai_service.complete_json(
            db_session, str(test_user.id), TaskType.RECIPE_GENERATE, MESSAGES
        )
        assert result == {"error": "not json at all"}


class TestCompleteFallback:
    async def test_retries_then_returns_fallback(self, db_session, test_user, redis, openrouter):
        openrouter.fail(500, times=3)

        result = await ai_service.complete(
            db_session, str(test_user.id), TaskType.COACH_CHAT, MESSAGES
        )

        assert result == FALLBACK_MESSAGES[TaskType.COACH_CHAT]
        assert len(openrouter.requests) == 3  # tenacity stop_after_attempt(3)
        # Fallbacks are neither cached nor logged as usage
        key = ai_service._cache_key(TaskType.COACH_CHAT.value, MESSAGES)
        assert await redis.get(key) is None
        assert await _usage_logs(db_session, test_user.id) == []

    async def test_recovers_after_transient_failure(self, db_session, test_user, openrouter):
        openrouter.fail(500, times=2).reply("ok now")
        result = await ai_service.complete(
            db_session, str(test_user.id), TaskType.COACH_CHAT, MESSAGES
        )
        assert result == "ok now"
        assert len(openrouter.requests) == 3

    async def test_fallback_for_recipe_generate_is_valid_json(
        self, db_session, test_user, openrouter
    ):
        openrouter.fail(500, times=3)
        result = await ai_service.complete_json(
            db_session, str(test_user.id), TaskType.RECIPE_GENERATE, MESSAGES
        )
        assert result["title"] == "Unable to generate recipe"
        assert result["ingredients_json"] == []

    async def test_fallback_for_nutrition_lookup_is_zeroed(self, db_session, test_user, openrouter):
        openrouter.fail(500, times=3)
        result = await ai_service.complete_json(
            db_session, str(test_user.id), TaskType.NUTRITION_LOOKUP, MESSAGES
        )
        assert result == {"calories": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0}
