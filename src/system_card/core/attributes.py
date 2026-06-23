"""Custom OTel attribute names this project stamps onto spans, defined once."""

from enum import StrEnum


class AgentAttributes(StrEnum):
    """Names for the agent.* attribute namespace.

    Standard gen_ai.* attributes come from ADK automatically; these are the
    project-specific additions layered on top.
    """

    SYSTEM_CARD_HASH = "agent.system_card_hash"
