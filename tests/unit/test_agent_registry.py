"""Unit tests for the agent registry."""

import pytest

from system_card.registry.agent_registry import AgentRegistry
from system_card.registry.exceptions import AgentNotFoundError, DuplicateAgentError
from system_card.schemas.agent_spec import AgentSpec
from system_card.schemas.model_config import ModelConfig, ModelProvider


def _spec(name: str = "system_card_agent") -> AgentSpec:
    model = ModelConfig(
        provider=ModelProvider.OLLAMA,
        model_name="gemma4:latest",
        model_digest="abc123",
        temperature=0.7,
        top_p=1.0,
        top_k=64,
        seed=None,
        presence_penalty=None,
        frequency_penalty=None,
        stop_sequences=None,
        max_output_tokens=None,
    )
    return AgentSpec(
        name=name,
        description="A test agent.",
        instruction="Use the available tools to answer the user's request.",
        model=model,
        tool_names=("calculator", "dad_joke"),
    )


def test_register_and_get_returns_the_same_spec() -> None:
    registry = AgentRegistry()
    spec = _spec()

    registry.register(spec)

    assert registry.get("system_card_agent") is spec


def test_register_duplicate_name_raises() -> None:
    registry = AgentRegistry()
    registry.register(_spec())

    with pytest.raises(DuplicateAgentError):
        registry.register(_spec())


def test_get_unregistered_name_raises() -> None:
    registry = AgentRegistry()

    with pytest.raises(AgentNotFoundError):
        registry.get("nonexistent")


def test_list_agents_returns_every_registered_spec() -> None:
    registry = AgentRegistry()
    registry.register(_spec(name="agent_one"))
    registry.register(_spec(name="agent_two"))

    names = {spec.name for spec in registry.list_agents()}

    assert names == {"agent_one", "agent_two"}
