from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.coach import router as coach_router
from app.api.v1.food_log import router as food_log_router
from app.api.v1.health import router as health_router
from app.api.v1.meal_plans import router as meal_plans_router
from app.api.v1.pantry import router as pantry_router
from app.api.v1.receipts import router as receipts_router
from app.api.v1.recipes import router as recipes_router
from app.api.v1.shopping_lists import router as shopping_lists_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(pantry_router)
api_router.include_router(receipts_router)
api_router.include_router(recipes_router)
api_router.include_router(meal_plans_router)
api_router.include_router(shopping_lists_router)
api_router.include_router(food_log_router)
api_router.include_router(health_router)
api_router.include_router(coach_router)
