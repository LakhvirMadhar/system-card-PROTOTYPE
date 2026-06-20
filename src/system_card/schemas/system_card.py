"""Typed shape of the full system card — the application's versioned behavior surface."""

from pydantic import BaseModel

from system_card.schemas.agent_manifest import AgentManifestEntry


class SystemCard(BaseModel):
    """The application's complete LLM-facing behavior surface at a point in time.

    Attributes:
        agents: Every registered agent's resolved manifest entry, sorted by
            name for deterministic hashing. Each agent carries its own
            tools and model, so changes are attributable to a specific
            agent rather than the system as one undifferentiated whole.
    """

    agents: list[AgentManifestEntry]
