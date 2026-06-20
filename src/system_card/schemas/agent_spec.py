"""Typed shape describing a single agent's configuration."""

from pydantic import BaseModel

from system_card.schemas.model_config import ModelConfig


class AgentSpec(BaseModel):
    """Declares an agent's name, instruction, model, and equipped tools.

    Attributes:
        name: The agent's unique name.
        instruction: The system instruction guiding the agent's behavior.
        model: The model and generation hyperparameters this agent runs with.
        tool_names: Names of the tools (as registered in a ToolRegistry) this
            agent is equipped with.
    """

    name: str
    instruction: str
    model: ModelConfig
    tool_names: tuple[str, ...]
