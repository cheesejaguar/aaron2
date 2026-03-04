from sqlalchemy.ext.asyncio import AsyncSession

from app.models.recipe import Recipe
from app.models.user import User
from app.schemas.recipe import RecipeGenerateRequest
from app.services.ai_service import TaskType, ai_service

GENERATE_SYSTEM = """You are a health-focused recipe creator \
specializing in DASH diet and heart-healthy meals.
Create recipes that help lower blood pressure, reduce cholesterol, \
and support weight loss.
Return JSON with these fields:
- title: recipe name (string)
- description: brief description (string)
- ingredients: array of {name, quantity, unit}
- steps: array of step strings
- nutrition_per_serving: {calories, protein_g, carbs_g, fat_g,
  fiber_g, sodium_mg, potassium_mg, cholesterol_mg}
- health_tags: array like "low-sodium", "high-fiber", "dash-diet"
Only return JSON."""

IMPORT_SYSTEM = """Extract recipe information from the provided webpage content.
Return JSON with these fields:
- title: recipe name (string)
- description: brief description (string)
- ingredients: array of {name, quantity, unit}
- steps: array of step strings
- nutrition_per_serving: {calories, protein_g, carbs_g, fat_g,
  fiber_g, sodium_mg} (estimate if not provided)
- health_tags: array of applicable tags
Only return JSON."""


async def generate_recipe(db: AsyncSession, user: User, data: RecipeGenerateRequest) -> Recipe:
    prompt_parts = ["Generate a healthy recipe"]
    if data.dietary_preferences:
        prompt_parts.append(f"Dietary preferences: {', '.join(data.dietary_preferences)}")
    if data.available_ingredients:
        prompt_parts.append(f"Use these ingredients: {', '.join(data.available_ingredients)}")
    if data.health_focus:
        prompt_parts.append(f"Health focus: {data.health_focus}")
    if data.cuisine:
        prompt_parts.append(f"Cuisine: {data.cuisine}")

    messages = [
        {"role": "system", "content": GENERATE_SYSTEM},
        {"role": "user", "content": ". ".join(prompt_parts)},
    ]

    result = await ai_service.complete_json(
        db, str(user.id), TaskType.RECIPE_GENERATE, messages, use_cache=False
    )

    recipe = Recipe(
        user_id=user.id,
        title=result.get("title", "AI Recipe"),
        description=result.get("description"),
        ingredients_json=result.get("ingredients"),
        steps_json=result.get("steps"),
        nutrition_per_serving_json=result.get("nutrition_per_serving"),
        health_tags=result.get("health_tags"),
        is_ai_generated=True,
    )
    db.add(recipe)
    await db.flush()
    await db.refresh(recipe)
    return recipe


async def import_recipe_from_url(db: AsyncSession, user: User, url: str) -> Recipe:
    import httpx

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, follow_redirects=True, timeout=15)
        page_content = resp.text[:8000]  # Limit content size

    messages = [
        {"role": "system", "content": IMPORT_SYSTEM},
        {"role": "user", "content": f"URL: {url}\n\nPage content:\n{page_content}"},
    ]

    result = await ai_service.complete_json(db, str(user.id), TaskType.RECIPE_IMPORT, messages)

    recipe = Recipe(
        user_id=user.id,
        title=result.get("title", "Imported Recipe"),
        description=result.get("description"),
        ingredients_json=result.get("ingredients"),
        steps_json=result.get("steps"),
        nutrition_per_serving_json=result.get("nutrition_per_serving"),
        health_tags=result.get("health_tags"),
        source_url=url,
        is_ai_generated=False,
    )
    db.add(recipe)
    await db.flush()
    await db.refresh(recipe)
    return recipe
