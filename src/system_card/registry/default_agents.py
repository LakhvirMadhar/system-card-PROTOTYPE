"""Registers the project's default agents into an AgentRegistry."""

from system_card.agents import system_card_agent
from system_card.registry.agent_registry import AgentRegistry
from system_card.schemas.model_config import ModelConfig


def register_default_agents(registry: AgentRegistry, model: ModelConfig) -> None:
    """Registers every default agent, all running on the given model.

    Args:
        registry: The agent registry to populate.
        model: The model and generation hyperparameters to run agents with.
    """
    registry.register(system_card_agent.build_spec(model))
