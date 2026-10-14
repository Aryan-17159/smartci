import pytest

from src.inventory import Inventory


def test_add_stock():
    inventory = Inventory()
    inventory.add_stock("pen", 10)
    assert inventory.stock["pen"] == 10


def test_add_stock_accumulates():
    inventory = Inventory()
    inventory.add_stock("pen", 10)
    inventory.add_stock("pen", 5)
    assert inventory.stock["pen"] == 15


def test_remove_stock():
    inventory = Inventory()
    inventory.add_stock("pen", 10)
    inventory.remove_stock("pen", 4)
    assert inventory.stock["pen"] == 6


def test_remove_all_stock():
    inventory = Inventory()
    inventory.add_stock("pen", 3)
    inventory.remove_stock("pen", 3)
    assert inventory.stock["pen"] == 0


def test_removing_too_much_raises_and_preserves_stock():
    inventory = Inventory()
    inventory.add_stock("pen", 2)
    with pytest.raises(ValueError, match="not enough stock"):
        inventory.remove_stock("pen", 3)
    assert inventory.stock["pen"] == 2


def test_removing_missing_item_raises():
    inventory = Inventory()
    with pytest.raises(ValueError, match="not enough stock"):
        inventory.remove_stock("missing", 1)
    assert inventory.stock == {}


def test_different_products_have_separate_stock():
    inventory = Inventory()
    inventory.add_stock("pen", 10)
    inventory.add_stock("book", 4)
    inventory.remove_stock("pen", 2)
    assert inventory.stock == {"pen": 8, "book": 4}


def test_inventories_have_independent_stock():
    first = Inventory()
    second = Inventory()
    first.add_stock("pen", 10)
    assert second.stock == {}
