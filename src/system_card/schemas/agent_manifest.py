"""Typed shape of one agent's resolved behavior surface in the system card."""

from pydantic import BaseModel

from system_card.schemas.model_config import ModelConfig
from system_card.schemas.tool_manifest import ToolManifestEntry


class AgentManifestEntry(BaseModel):
    """One agent's full behavior surface, with its tools resolved to manifests.

    This is the extension point for future per-agent surfaces (memory,
    planner config, etc.) — each one becomes a new field here when it's
    actually built, not before.

    Attributes:
        name: The agent's name.
        instruction: The system instruction guiding the agent's behavior.
        tools: This agent's equipped tools, resolved to their manifest
            entries and sorted by name for deterministic hashing.
        model: The model and generation hyperparameters this agent runs with.
    """

    name: str
    instruction: str
    tools: list[ToolManifestEntry]
    model: ModelConfig
