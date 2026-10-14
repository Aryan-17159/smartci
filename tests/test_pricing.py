import pytest

from src.pricing import add_tax, apply_discount


def test_discount_basic():
    assert apply_discount(100, 10) == 90.0


def test_discount_boundaries():
    assert apply_discount(100, 0) == 100.0
    assert apply_discount(100, 100) == 0.0


@pytest.mark.parametrize("percent", [-1, -0.01, 100.01, 101])
def test_discount_invalid(percent):
    with pytest.raises(ValueError, match="percent must be between 0 and 100"):
        apply_discount(100, percent)


def test_discount_rounds_to_two_places():
    assert apply_discount(99.99, 15) == 84.99


def test_discount_zero_price():
    assert apply_discount(0, 50) == 0.0


def test_tax_default():
    assert add_tax(100) == 118.0


def test_tax_custom_rate():
    assert add_tax(100, rate=0.05) == 105.0


def test_tax_zero_rate():
    assert add_tax(75.5, rate=0) == 75.5


def test_tax_rounds_to_two_places():
    assert add_tax(19.99) == 23.59
