"""Types for the calculator tool, kept separate so importing them never pulls in the tool itself."""

from typing import Literal

Operator = Literal["+", "-", "*", "/"]


class DivisionByZeroError(Exception):
    """Raised when a calculator call divides by zero."""
