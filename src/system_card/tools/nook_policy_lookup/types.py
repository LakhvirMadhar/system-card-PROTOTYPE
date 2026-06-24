"""Types for the nook_policy_lookup tool."""

from typing import Literal

PolicyTopic = Literal["returns", "shipping", "warranty"]


class PolicyNotFoundError(Exception):
    """Raised when no policy text exists for the given topic."""
