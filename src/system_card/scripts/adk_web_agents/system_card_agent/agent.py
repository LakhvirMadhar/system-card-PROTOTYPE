"""Exposes root_agent for `adk web`, built from the same registry adk web_agents elsewhere use.

`adk web` discovers agents by importing a module-level `root_agent` from an
`agent.py` inside a directory it's pointed at. This wires that single
required name onto the project's own AgentSpec/registry construction, so
`adk web` runs the exact same agent as every other script, not a separate
hardcoded copy.
"""

from system_card.agents import system_card_agent
from system_card.core.config import Settings
from system_card.dependencies.registries import build_pinned_model, build_registries
from system_card.services.agent_service import build_agent_from_spec

_settings = Settings()
_model = build_pinned_model(_settings)
_registries = build_registries(_model)

root_agent = build_agent_from_spec(
    _registries.agents.get(system_card_agent.NAME), _registries.tools, _settings.ollama_api_base
)
