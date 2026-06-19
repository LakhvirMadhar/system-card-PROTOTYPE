"""Unit tests for the toy tools."""

import pytest

from system_card.tools.calculator import DivisionByZeroError, Operator, calculator
from system_card.tools.coin_flip import coin_flip
from system_card.tools.dad_joke import dad_joke
from system_card.tools.shakespearify import shakespearify
from system_card.tools.word_count import word_count


@pytest.mark.parametrize(
    ("a", "b", "operator", "expected"),
    [
        (2, 3, "+", 5),
        (2, 3, "-", -1),
        (2, 3, "*", 6),
        (6, 3, "/", 2),
    ],
)
def test_calculator_applies_operator(
    a: float, b: float, operator: Operator, expected: float
) -> None:
    assert calculator(a, b, operator) == expected


def test_calculator_raises_on_division_by_zero() -> None:
    with pytest.raises(DivisionByZeroError):
        calculator(1, 0, "/")


def test_dad_joke_returns_nonempty_string() -> None:
    assert isinstance(dad_joke(), str)
    assert dad_joke() != ""


def test_coin_flip_returns_heads_or_tails() -> None:
    assert coin_flip() in ("heads", "tails")


def test_shakespearify_replaces_known_words() -> None:
    assert shakespearify("Hello friend, you are welcome") == "Hail fellow, thou art welcome"


def test_shakespearify_leaves_unknown_words_untouched() -> None:
    assert shakespearify("the quick fox") == "the quick fox"


def test_word_count_counts_whitespace_separated_words() -> None:
    assert word_count("the quick brown fox") == 4


def test_word_count_returns_zero_for_empty_string() -> None:
    assert word_count("") == 0
