from typing import Any
from uuid import UUID

from pydantic import BaseModel


class RecipeCreate(BaseModel):
    title: str
    description: str | None = None
    ingredients_json: list[dict[str, Any]] | None = None
    steps_json: list[str] | None = None
    nutrition_per_serving_json: dict[str, Any] | None = None
    health_tags: list[str] | None = None
    source_url: str | None = None
    is_ai_generated: bool = False


class RecipeRead(BaseModel):
    id: UUID
    title: str
    description: str | None = None
    ingredients_json: list[dict[str, Any]] | None = None
    steps_json: list[str] | None = None
    nutrition_per_serving_json: dict[str, Any] | None = None
    health_tags: list[str] | None = None
    source_url: str | None = None
    is_ai_generated: bool


class RecipeGenerateRequest(BaseModel):
    dietary_preferences: list[str] | None = None
    available_ingredients: list[str] | None = None
    health_focus: str | None = None
    cuisine: str | None = None


class RecipeImportRequest(BaseModel):
    url: str
