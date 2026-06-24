"""Registry-specific exceptions."""


class ToolNotFoundError(Exception):
    """Raised when a requested tool has no registered entry."""


class DuplicateToolError(Exception):
    """Raised when a tool name is registered more than once."""


class AgentNotFoundError(Exception):
    """Raised when a requested agent has no registered spec."""


class DuplicateAgentError(Exception):
    """Raised when an agent name is registered more than once."""


class GuardrailNotFoundError(Exception):
    """Raised when a requested guardrail has no registered spec."""


class DuplicateGuardrailError(Exception):
    """Raised when a guardrail name is registered more than once."""
