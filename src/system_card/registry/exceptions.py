"""Registry-specific exceptions."""


class ToolNotFoundError(Exception):
    """Raised when a requested tool has no registered entry."""


class DuplicateToolError(Exception):
    """Raised when a tool name is registered more than once."""
