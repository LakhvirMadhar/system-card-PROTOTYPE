"""Exposes root_agent for `adk web`, built from the same registry adk_web_agents elsewhere use.

`adk web` discovers agents by importing a module-level `root_agent` from an
`agent.py` inside a directory it's pointed at. This wires that single
required name onto the project's own AgentSpec/registry construction, so
`adk web` runs the exact same agent definition every other script does --
including its guardrails, wired in as a real before_model_callback on the
LlmAgent itself, so adk web's own runner sees the same guardrail behavior
as everything else, not a side-channel only one caller knows about.
"""

from system_card.agents import nook_support_agent
from system_card.core.config import Settings
from system_card.dependencies.registries import build_pinned_model, build_registries
from system_card.services.agent_service import build_agent_from_spec

_settings = Settings()
_model = build_pinned_model(_settings)
_registries = build_registries(_model)

_spec = _registries.agents.get(nook_support_agent.NAME)
_guardrails = [_registries.guardrails.get(name) for name in _spec.guardrail_names]

root_agent = build_agent_from_spec(_spec, _registries.tools, _settings.ollama_api_base, _guardrails)
