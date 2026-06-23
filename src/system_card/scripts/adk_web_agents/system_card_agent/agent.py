"""Exposes root_agent for `adk web`, built from the same registry adk web_agents elsewhere use.

`adk web` discovers agents by importing a module-level `root_agent` from an
`agent.py` inside a directory it's pointed at. This wires that single
required name onto the project's own AgentSpec/registry construction, so
`adk web` runs the exact same agent as every other script, not a separate
hardcoded copy.
"""

from system_card.adapters.ollama_digest import verify_model_digest
from system_card.agents import system_card_agent
from system_card.core.config import Settings
from system_card.registry.agent_registry import AgentRegistry
from system_card.registry.default_agents import register_default_agents
from system_card.registry.default_tools import register_default_tools
from system_card.registry.tool_registry import ToolRegistry
from system_card.schemas.model_config import ModelConfig, ModelProvider
from system_card.services.agent_service import build_agent_from_spec

_settings = Settings()

_tool_registry = ToolRegistry()
register_default_tools(_tool_registry)

_model = ModelConfig(
    provider=ModelProvider.OLLAMA,
    model_name=system_card_agent.PINNED_MODEL_TAG,
    model_digest=verify_model_digest(
        system_card_agent.PINNED_MODEL_TAG,
        _settings.ollama_api_base,
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

_agent_registry = AgentRegistry()
register_default_agents(_agent_registry, _model)

root_agent = build_agent_from_spec(
    _agent_registry.get(system_card_agent.NAME), _tool_registry, _settings.ollama_api_base
)
