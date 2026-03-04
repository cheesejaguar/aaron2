from uuid import uuid4

from app.models.shopping import ShoppingList, ShoppingListItem
from app.services.shopping_service import _compute_health_priority, build_amazon_cart_url


class TestBuildAmazonCartUrl:
    def _make_list(self, items: list[dict]) -> ShoppingList:
        sl = ShoppingList(id=uuid4(), user_id=uuid4(), name="Test", status="active")
        sl.items = [
            ShoppingListItem(
                id=uuid4(),
                shopping_list_id=sl.id,
                name=i["name"],
                is_checked=i.get("checked", False),
            )
            for i in items
        ]
        return sl

    def test_empty_list(self):
        sl = self._make_list([])
        assert build_amazon_cart_url(sl) == ""

    def test_all_checked_returns_empty(self):
        sl = self._make_list(
            [
                {"name": "Milk", "checked": True},
                {"name": "Eggs", "checked": True},
            ]
        )
        assert build_amazon_cart_url(sl) == ""

    def test_unchecked_items_in_url(self):
        sl = self._make_list(
            [
                {"name": "Milk", "checked": False},
                {"name": "Eggs", "checked": True},
                {"name": "Bread", "checked": False},
            ]
        )
        url = build_amazon_cart_url(sl)
        assert "amazon.com" in url
        assert "amazonfresh" in url
        assert "Milk" in url
        assert "Bread" in url

    def test_max_10_items(self):
        items = [{"name": f"Item{i}"} for i in range(15)]
        sl = self._make_list(items)
        url = build_amazon_cart_url(sl)
        # Only first 10 should appear
        assert "Item9" in url
        assert "Item10" not in url


class TestComputeHealthPriority:
    def test_produce_highest(self):
        assert _compute_health_priority("Kale", "produce") == 1.0

    def test_grains(self):
        assert _compute_health_priority("Rice", "grains") == 0.8

    def test_dairy(self):
        assert _compute_health_priority("Milk", "dairy") == 0.7

    def test_snacks_lowest(self):
        assert _compute_health_priority("Chips", "snacks") == 0.2

    def test_unknown_category(self):
        assert _compute_health_priority("Mystery", "unknown_category") == 0.5

    def test_none_category(self):
        assert _compute_health_priority("Something", None) == 0.5
