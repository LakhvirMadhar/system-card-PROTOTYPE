"""Exposes root_agent for `adk web`, built from the same registry adk_web_agents elsewhere use.

`adk web` discovers agents by importing a module-level `root_agent` from an
`agent.py` inside a directory it's pointed at. This wires that single
required name onto the project's own AgentSpec/registry construction, so
`adk web` runs the exact same agent definition every other script does --
including its guardrails, wired in as a real before_model_callback on the
LlmAgent itself, so adk web's own runner sees the same guardrail behavior
as everything else, not a side-channel only one caller knows about.
"""

from system_card.adapters.ollama_digest import verify_model_digest
from system_card.agents import nook_support_agent, system_card_agent
from system_card.core.config import Settings
from system_card.registry.agent_registry import AgentRegistry
from system_card.registry.default_agents import register_default_agents
from system_card.registry.default_guardrails import register_default_guardrails
from system_card.registry.default_tools import register_default_tools
from system_card.registry.guardrail_registry import GuardrailRegistry
from system_card.registry.tool_registry import ToolRegistry
from system_card.schemas.model_config import ModelConfig, ModelProvider
from system_card.services.agent_service import build_agent_from_spec

_settings = Settings()

_tool_registry = ToolRegistry()
register_default_tools(_tool_registry)

_guardrail_registry = GuardrailRegistry()
register_default_guardrails(_guardrail_registry)

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

_spec = _agent_registry.get(nook_support_agent.NAME)
_guardrails = [_guardrail_registry.get(name) for name in _spec.guardrail_names]

root_agent = build_agent_from_spec(_spec, _tool_registry, _settings.ollama_api_base, _guardrails)
