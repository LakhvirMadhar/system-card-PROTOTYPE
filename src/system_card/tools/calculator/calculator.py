"""Basic arithmetic tool exposed to the agent."""

from system_card.tools.calculator.types import DivisionByZeroError, Operator


def calculator(a: float, b: float, operator: Operator) -> float:
    """Performs a single basic arithmetic operation on two numbers.

    Args:
        a: The first operand.
        b: The second operand.
        operator: One of "+", "-", "*", "/".

    Returns:
        The result of applying the operator to a and b.

    Raises:
        DivisionByZeroError: If operator is "/" and b is zero.
    """
    if operator == "+":
        return a + b
    if operator == "-":
        return a - b
    if operator == "*":
        return a * b

    if b == 0:
        raise DivisionByZeroError("Cannot divide by zero.")

    return a / b
