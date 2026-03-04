import pytest
from pydantic import ValidationError

from app.schemas.food_log import DailySummary, FoodLogCreate


class TestFoodLogCreate:
    def test_minimal(self):
        log = FoodLogCreate(meal_type="lunch", food_name="Salad")
        assert log.food_name == "Salad"
        assert log.calories is None

    def test_full(self):
        log = FoodLogCreate(
            meal_type="dinner",
            food_name="Grilled Chicken",
            quantity=6,
            unit="oz",
            calories=280,
            protein_g=42,
            carbs_g=0,
            fat_g=12,
            fiber_g=0,
            sodium_mg=350,
            potassium_mg=400,
            cholesterol_mg=85,
        )
        assert log.calories == 280
        assert log.sodium_mg == 350

    def test_missing_required_rejected(self):
        with pytest.raises(ValidationError):
            FoodLogCreate(meal_type="lunch")  # type: ignore[call-arg]


class TestDailySummary:
    def test_summary_fields(self):
        s = DailySummary(
            date="2024-01-15",
            total_calories=1800,
            total_protein_g=90,
            total_carbs_g=200,
            total_fat_g=60,
            total_fiber_g=25,
            total_sodium_mg=1200,
            total_potassium_mg=3500,
            total_cholesterol_mg=200,
            meal_count=3,
        )
        assert s.total_calories == 1800
        assert s.meal_count == 3

    def test_zero_values(self):
        s = DailySummary(
            date="2024-01-15",
            total_calories=0,
            total_protein_g=0,
            total_carbs_g=0,
            total_fat_g=0,
            total_fiber_g=0,
            total_sodium_mg=0,
            total_potassium_mg=0,
            total_cholesterol_mg=0,
            meal_count=0,
        )
        assert s.meal_count == 0
