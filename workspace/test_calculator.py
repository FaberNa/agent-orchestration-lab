import pytest

from calculator import divide


def test_divide_returns_quotient():
    assert divide(10, 2) == 5


def test_divide_handles_negative_numbers():
    assert divide(-9, 3) == -3


def test_divide_handles_zero_numerator():
    assert divide(0, 5) == 0


def test_divide_rejects_zero_divisor():
    with pytest.raises(ValueError):
        divide(10, 0)