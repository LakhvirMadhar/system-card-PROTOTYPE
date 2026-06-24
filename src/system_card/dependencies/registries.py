"""Composition root: wires every registry together so scripts don't each repeat the setup."""

from dataclasses import dataclass

from system_card.adapters.ollama_digest import verify_model_digest
from system_card.agents import system_card_agent
from system_card.core.config import Settings
from system_card.registry.agent_registry import AgentRegistry
from system_card.registry.default_agents import register_default_agents
from system_card.registry.default_guardrails import register_default_guardrails
from system_card.registry.default_tools import register_default_tools
from system_card.registry.guardrail_registry import GuardrailRegistry
from system_card.registry.tool_registry import ToolRegistry
from system_card.schemas.model_config import ModelConfig, ModelProvider


@dataclass(frozen=True)
class Registries:
    """Every populated registry the project's scripts need.

    Attributes:
        tools: Every default tool, registered.
        guardrails: Every default guardrail, registered.
        agents: Every default agent, registered against the given model.
    """

    tools: ToolRegistry
    guardrails: GuardrailRegistry
    agents: AgentRegistry


def build_pinned_model(settings: Settings) -> ModelConfig:
    """Builds the pinned model config, verifying the digest against a live Ollama server.

    Args:
        settings: Used to reach the local Ollama server for verification.

    Returns:
        The pinned ModelConfig, with its digest confirmed live.

    Raises:
        OllamaDigestLookupError: If no local model matches the pinned tag.
        ModelDigestMismatchError: If the tag's live digest no longer matches.
    """
    return ModelConfig(
        provider=ModelProvider.OLLAMA,
        model_name=system_card_agent.PINNED_MODEL_TAG,
        model_digest=verify_model_digest(
            system_card_agent.PINNED_MODEL_TAG,
            settings.ollama_api_base,
            system_card_agent.PINNED_MODEL_DIGEST,
        ),
        temperature=0.7,
        top_p=1.0,
        top_k=64,
        seed=None,
        presence_penalty=None,
        frequency_penalty=None,
        stop_sequences=None,
        max_output_tokens=None,
    )


def build_pinned_model_from_source() -> ModelConfig:
    """Builds the pinned model config from source only, with no live Ollama call.

    Used by record_card_version.py, which runs in CI where there's no local
    Ollama server to verify against — the card hash has to reflect what's
    pinned in source, not a runtime check that's unavailable there.

    Returns:
        The pinned ModelConfig, using the digest declared in source as-is.
    """
    return ModelConfig(
        provider=ModelProvider.OLLAMA,
        model_name=system_card_agent.PINNED_MODEL_TAG,
        model_digest=system_card_agent.PINNED_MODEL_DIGEST,
        temperature=0.7,
        top_p=1.0,
        top_k=64,
        seed=None,
        presence_penalty=None,
        frequency_penalty=None,
        stop_sequences=None,
        max_output_tokens=None,
    )


def build_registries(model: ModelConfig) -> Registries:
    """Builds and populates every registry with the project's defaults.

    Args:
        model: The model every default agent runs with.

    Returns:
        Every populated registry, ready to pass into build_system_card() or
        to resolve a specific agent's tools/guardrails for running it.
    """
    tool_registry = ToolRegistry()
    register_default_tools(tool_registry)

    guardrail_registry = GuardrailRegistry()
    register_default_guardrails(guardrail_registry)

    agent_registry = AgentRegistry()
    register_default_agents(agent_registry, model)

    return Registries(tools=tool_registry, guardrails=guardrail_registry, agents=agent_registry)
