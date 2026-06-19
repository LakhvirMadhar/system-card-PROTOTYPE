"""Smoke tests — verifies the package imports without errors."""

import system_card


def test_package_importable() -> None:
    assert system_card is not None
