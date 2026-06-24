"""Typed shape describing a single agent's configuration."""

from pydantic import BaseModel

from system_card.schemas.model_config import ModelConfig


class AgentSpec(BaseModel):
    """Declares an agent's name, instruction, model, and equipped tools.

    Attributes:
        name: The agent's unique name.
        description: A short description of what the agent does. ADK injects
            this into the model-facing system instruction alongside the
            agent's name, so it's part of the card's behavior surface too.
        instruction: The system instruction guiding the agent's behavior.
        model: The model and generation hyperparameters this agent runs with.
        tool_names: Names of the tools (as registered in a ToolRegistry) this
            agent is equipped with.
        guardrail_names: Names of the guardrails (as registered in a
            GuardrailRegistry) checked against every incoming message before
            this agent's turn. Defaults to none.
    """

    name: str
    description: str
    instruction: str
    model: ModelConfig
    tool_names: tuple[str, ...]
    guardrail_names: tuple[str, ...] = ()
