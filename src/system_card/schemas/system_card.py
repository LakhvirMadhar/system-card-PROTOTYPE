"""Typed shape of the full system card — the application's versioned behavior surface."""

from pydantic import BaseModel

from system_card.schemas.model_config import ModelConfig
from system_card.schemas.tool_manifest import ToolManifestEntry


class SystemCard(BaseModel):
    """The application's complete LLM-facing behavior surface at a point in time.

    Attributes:
        tools: Every registered tool's manifest entry, sorted by name for
            deterministic hashing.
        model: The LLM and generation hyperparameters actually configured
            on the agent. System prompt fields will be added here once
            that surface is captured too.
    """

    tools: list[ToolManifestEntry]
    model: ModelConfig
