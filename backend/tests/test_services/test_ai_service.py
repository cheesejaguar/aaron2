from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.ai_service import FALLBACK_MESSAGES, AIService, TaskType


@pytest.fixture
def mock_redis():
    redis = AsyncMock()
    redis.incr = AsyncMock(return_value=1)
    redis.expire = AsyncMock()
    redis.get = AsyncMock(return_value=None)
    redis.set = AsyncMock()
    return redis


@pytest.fixture
def mock_openai_response():
    choice = MagicMock()
    choice.message.content = '{"result": "test"}'
    usage = MagicMock()
    usage.prompt_tokens = 10
    usage.completion_tokens = 20
    response = MagicMock()
    response.choices = [choice]
    response.usage = usage
    return response


@pytest.fixture
def ai_service():
    return AIService()


class TestCacheKey:
    def test_deterministic(self, ai_service):
        key1 = ai_service._cache_key("task", [{"role": "user", "content": "hi"}])
        key2 = ai_service._cache_key("task", [{"role": "user", "content": "hi"}])
        assert key1 == key2

    def test_different_inputs(self, ai_service):
        key1 = ai_service._cache_key("task1", [{"role": "user", "content": "hi"}])
        key2 = ai_service._cache_key("task2", [{"role": "user", "content": "hi"}])
        assert key1 != key2


class TestRateLimit:
    @pytest.mark.asyncio
    async def test_under_limit(self, ai_service, mock_redis):
        with patch("app.services.ai_service.get_redis", return_value=mock_redis):
            await ai_service._check_rate_limit("user-1")  # Should not raise

    @pytest.mark.asyncio
    async def test_over_limit(self, ai_service, mock_redis):
        mock_redis.incr = AsyncMock(return_value=11)
        with patch("app.services.ai_service.get_redis", return_value=mock_redis):
            with pytest.raises(ValueError, match="Rate limit exceeded"):
                await ai_service._check_rate_limit("user-1")

    @pytest.mark.asyncio
    async def test_first_request_sets_expire(self, ai_service, mock_redis):
        mock_redis.incr = AsyncMock(return_value=1)
        with patch("app.services.ai_service.get_redis", return_value=mock_redis):
            await ai_service._check_rate_limit("user-1")
            mock_redis.expire.assert_called_once()


class TestComplete:
    @pytest.mark.asyncio
    async def test_complete_with_cache_hit(self, ai_service, mock_redis):
        mock_redis.get = AsyncMock(return_value="cached result")
        db = AsyncMock()

        with patch("app.services.ai_service.get_redis", return_value=mock_redis):
            result = await ai_service.complete(
                db,
                "user-1",
                TaskType.COACH_CHAT,
                [{"role": "user", "content": "hi"}],
            )
            assert result == "cached result"

    @pytest.mark.asyncio
    async def test_complete_cache_miss(self, ai_service, mock_redis, mock_openai_response):
        db = AsyncMock()
        ai_service.client.chat.completions.create = AsyncMock(return_value=mock_openai_response)

        with patch("app.services.ai_service.get_redis", return_value=mock_redis):
            result = await ai_service.complete(
                db,
                "user-1",
                TaskType.COACH_CHAT,
                [{"role": "user", "content": "hi"}],
            )
            assert result == '{"result": "test"}'
            mock_redis.set.assert_called_once()
            db.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_complete_no_cache(self, ai_service, mock_redis, mock_openai_response):
        db = AsyncMock()
        ai_service.client.chat.completions.create = AsyncMock(return_value=mock_openai_response)

        with patch("app.services.ai_service.get_redis", return_value=mock_redis):
            result = await ai_service.complete(
                db,
                "user-1",
                TaskType.COACH_CHAT,
                [{"role": "user", "content": "hi"}],
                use_cache=False,
            )
            assert result == '{"result": "test"}'
            mock_redis.get.assert_not_called()


class TestCompleteJson:
    @pytest.mark.asyncio
    async def test_valid_json(self, ai_service, mock_redis, mock_openai_response):
        db = AsyncMock()
        ai_service.client.chat.completions.create = AsyncMock(return_value=mock_openai_response)

        with patch("app.services.ai_service.get_redis", return_value=mock_redis):
            result = await ai_service.complete_json(
                db,
                "user-1",
                TaskType.RECIPE_GENERATE,
                [{"role": "user", "content": "hi"}],
            )
            assert result == {"result": "test"}

    @pytest.mark.asyncio
    async def test_json_in_code_block(self, ai_service, mock_redis):
        choice = MagicMock()
        choice.message.content = 'Here is the result:\n```json\n{"key": "value"}\n```'
        usage = MagicMock()
        usage.prompt_tokens = 5
        usage.completion_tokens = 10
        response = MagicMock()
        response.choices = [choice]
        response.usage = usage

        db = AsyncMock()
        ai_service.client.chat.completions.create = AsyncMock(return_value=response)

        with patch("app.services.ai_service.get_redis", return_value=mock_redis):
            result = await ai_service.complete_json(
                db,
                "user-1",
                TaskType.RECIPE_GENERATE,
                [{"role": "user", "content": "hi"}],
            )
            assert result == {"key": "value"}

    @pytest.mark.asyncio
    async def test_invalid_json_returns_error_dict(self, ai_service, mock_redis):
        choice = MagicMock()
        choice.message.content = "not json at all"
        usage = MagicMock()
        usage.prompt_tokens = 5
        usage.completion_tokens = 10
        response = MagicMock()
        response.choices = [choice]
        response.usage = usage

        db = AsyncMock()
        ai_service.client.chat.completions.create = AsyncMock(return_value=response)

        with patch("app.services.ai_service.get_redis", return_value=mock_redis):
            result = await ai_service.complete_json(
                db,
                "user-1",
                TaskType.RECIPE_GENERATE,
                [{"role": "user", "content": "hi"}],
            )
            assert "error" in result
            assert result["error"] == "not json at all"


class TestCompleteFallback:
    @pytest.mark.asyncio
    async def test_returns_fallback_on_exception(self, ai_service, mock_redis):
        db = AsyncMock()
        ai_service.client.chat.completions.create = AsyncMock(side_effect=Exception("API down"))

        with patch("app.services.ai_service.get_redis", return_value=mock_redis):
            result = await ai_service.complete(
                db,
                "user-1",
                TaskType.COACH_CHAT,
                [{"role": "user", "content": "hi"}],
            )
            assert result == FALLBACK_MESSAGES[TaskType.COACH_CHAT]

    @pytest.mark.asyncio
    async def test_fallback_for_recipe_generate(self, ai_service, mock_redis):
        db = AsyncMock()
        ai_service.client.chat.completions.create = AsyncMock(side_effect=Exception("timeout"))

        with patch("app.services.ai_service.get_redis", return_value=mock_redis):
            result = await ai_service.complete(
                db,
                "user-1",
                TaskType.RECIPE_GENERATE,
                [{"role": "user", "content": "generate"}],
            )
            assert "Unable to generate recipe" in result

    @pytest.mark.asyncio
    async def test_fallback_for_nutrition_lookup(self, ai_service, mock_redis):
        db = AsyncMock()
        ai_service.client.chat.completions.create = AsyncMock(side_effect=Exception("error"))

        with patch("app.services.ai_service.get_redis", return_value=mock_redis):
            result = await ai_service.complete(
                db,
                "user-1",
                TaskType.NUTRITION_LOOKUP,
                [{"role": "user", "content": "lookup"}],
            )
            assert "calories" in result
