import pytest

from src.cart import Cart


def test_total_with_discount():
    cart = Cart()
    cart.add("pen", 50, 2)
    assert cart.total(discount=10) == 106.2


def test_empty_cart():
    assert Cart().total() == 0


def test_default_quantity():
    cart = Cart()
    cart.add("notebook", 100)
    assert cart.total() == 118.0


def test_multiple_items_and_quantities():
    cart = Cart()
    cart.add("pen", 10, 3)
    cart.add("notebook", 50, 2)
    assert cart.total() == 153.4


def test_full_discount():
    cart = Cart()
    cart.add("book", 250)
    assert cart.total(discount=100) == 0.0


def test_invalid_discount_reaches_pricing_validation():
    cart = Cart()
    cart.add("book", 250)
    with pytest.raises(ValueError, match="percent must be between 0 and 100"):
        cart.total(discount=-1)


def test_carts_have_independent_items():
    first = Cart()
    second = Cart()
    first.add("pen", 10)
    assert second.total() == 0.0


def test_total_does_not_change_items():
    cart = Cart()
    cart.add("pen", 50, 2)
    assert cart.total(discount=10) == 106.2
    assert cart.total(discount=10) == 106.2
    assert cart.total() == 118.0
