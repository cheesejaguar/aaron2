from datetime import datetime, timedelta

from app.models.food_log import FoodLog
from app.models.pantry import PantryItem
from app.tasks.replenishment import _calculate_consumption_rate


async def _add_logs(db_session, user_id, food_name, count, days_ago=1):
    when = datetime.utcnow() - timedelta(days=days_ago)
    db_session.add_all(
        [
            FoodLog(user_id=user_id, meal_type="snack", food_name=food_name, logged_at=when)
            for _ in range(count)
        ]
    )
    await db_session.flush()


class TestCalculateConsumptionRate:
    async def test_no_consumption(self, db_session, test_user):
        item = PantryItem(user_id=test_user.id, name="Milk", quantity=5.0)
        rate = await _calculate_consumption_rate(db_session, test_user.id, item)
        assert rate["daily_rate"] == 0.0
        assert rate["days_until_depletion"] == float("inf")

    async def test_with_consumption(self, db_session, test_user):
        await _add_logs(db_session, test_user.id, "Eggs", 14)  # 14 logs in 14 days = 1/day
        item = PantryItem(user_id=test_user.id, name="Eggs", quantity=5.0)

        rate = await _calculate_consumption_rate(db_session, test_user.id, item)

        assert rate["daily_rate"] == 1.0
        assert rate["days_until_depletion"] == 5.0

    async def test_high_consumption_rate(self, db_session, test_user):
        await _add_logs(db_session, test_user.id, "Water", 28)  # 2/day
        item = PantryItem(user_id=test_user.id, name="Water", quantity=4.0)

        rate = await _calculate_consumption_rate(db_session, test_user.id, item)

        assert rate["daily_rate"] == 2.0
        assert rate["days_until_depletion"] == 2.0

    async def test_only_counts_matching_recent_logs_for_user(
        self, db_session, test_user, second_user
    ):
        await _add_logs(db_session, test_user.id, "Eggs", 7)
        await _add_logs(db_session, test_user.id, "Eggs", 5, days_ago=20)  # outside window
        await _add_logs(db_session, test_user.id, "Bacon", 5)  # different food
        await _add_logs(db_session, second_user.id, "Eggs", 5)  # different user
        item = PantryItem(user_id=test_user.id, name="Eggs", quantity=3.0)

        rate = await _calculate_consumption_rate(db_session, test_user.id, item)

        assert rate["daily_rate"] == 0.5
        assert rate["days_until_depletion"] == 6.0
