from datetime import datetime

from app.models.food_log import FoodLog
from app.services.nutrition_service import get_daily_summary


def _log(user_id, logged_at, **nutrients):
    return FoodLog(
        user_id=user_id, meal_type="lunch", food_name="Food", logged_at=logged_at, **nutrients
    )


class TestGetDailySummary:
    async def test_empty_day(self, db_session, test_user):
        summary = await get_daily_summary(db_session, test_user.id, "2025-06-15")
        assert summary.date == "2025-06-15"
        assert summary.total_calories == 0
        assert summary.total_sodium_mg == 0
        assert summary.meal_count == 0

    async def test_sums_all_nutrients(self, db_session, test_user):
        noon = datetime(2025, 6, 15, 12, 0)
        db_session.add_all(
            [
                _log(
                    test_user.id,
                    noon,
                    calories=300,
                    protein_g=20.0,
                    carbs_g=30.0,
                    fat_g=10.0,
                    fiber_g=5.0,
                    sodium_mg=100.0,
                    potassium_mg=200.0,
                    cholesterol_mg=50.0,
                ),
                _log(
                    test_user.id,
                    noon,
                    calories=500,
                    protein_g=40.0,
                    carbs_g=20.0,
                    fat_g=15.0,
                    fiber_g=3.0,
                    sodium_mg=200.0,
                    potassium_mg=300.0,
                    cholesterol_mg=80.0,
                ),
            ]
        )
        await db_session.flush()

        summary = await get_daily_summary(db_session, test_user.id, "2025-06-15")

        assert summary.total_calories == 800
        assert summary.total_protein_g == 60.0
        assert summary.total_carbs_g == 50.0
        assert summary.total_fat_g == 25.0
        assert summary.total_fiber_g == 8.0
        assert summary.total_sodium_mg == 300.0
        assert summary.total_potassium_mg == 500.0
        assert summary.total_cholesterol_mg == 130.0
        assert summary.meal_count == 2

    async def test_missing_values_count_as_zero(self, db_session, test_user):
        db_session.add(_log(test_user.id, datetime(2025, 6, 15, 8, 0)))
        db_session.add(_log(test_user.id, datetime(2025, 6, 15, 9, 0), calories=120))
        await db_session.flush()

        summary = await get_daily_summary(db_session, test_user.id, "2025-06-15")

        assert summary.total_calories == 120
        assert summary.total_protein_g == 0
        assert summary.meal_count == 2

    async def test_only_includes_that_day(self, db_session, test_user):
        db_session.add_all(
            [
                _log(test_user.id, datetime(2025, 6, 14, 23, 59), calories=1),
                _log(test_user.id, datetime(2025, 6, 15, 0, 0), calories=10),
                _log(test_user.id, datetime(2025, 6, 15, 23, 59), calories=100),
                _log(test_user.id, datetime(2025, 6, 16, 0, 0), calories=1000),
            ]
        )
        await db_session.flush()

        summary = await get_daily_summary(db_session, test_user.id, "2025-06-15")

        assert summary.total_calories == 110
        assert summary.meal_count == 2

    async def test_only_includes_that_user(self, db_session, test_user, second_user):
        noon = datetime(2025, 6, 15, 12, 0)
        db_session.add(_log(test_user.id, noon, calories=200))
        db_session.add(_log(second_user.id, noon, calories=900))
        await db_session.flush()

        summary = await get_daily_summary(db_session, test_user.id, "2025-06-15")

        assert summary.total_calories == 200
        assert summary.meal_count == 1
