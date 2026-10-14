"""Discount and tax calculations from Lab 1."""


def apply_discount(price, percent):
    """Return the discounted price, rounded to two decimal places."""
    if not 0 <= percent <= 100:
        raise ValueError("percent must be between 0 and 100")
    return round(price * (1 - percent / 100), 2)


def add_tax(price, rate=0.18):
    """Return the price including tax (18% by default)."""
    return round(price * (1 + rate), 2)
