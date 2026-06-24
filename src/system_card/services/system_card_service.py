"""Builds the system card from the agent and tool registries and computes its hash."""

import hashlib

from system_card.registry.agent_registry import AgentRegistry
from system_card.registry.tool_registry import ToolRegistry
from system_card.schemas.agent_manifest import AgentManifestEntry
from system_card.schemas.system_card import SystemCard
from system_card.services.agent_service import effective_instruction


def build_system_card(agent_registry: AgentRegistry, tool_registry: ToolRegistry) -> SystemCard:
    """Builds the system card from every registered agent, tools resolved per agent.

    Args:
        agent_registry: The populated agent registry.
        tool_registry: The populated tool registry, used to resolve each
            agent's tool_names into manifest entries.

    Returns:
        A SystemCard capturing every agent's current behavior surface,
        agents and their tools both sorted by name.
    """
    agents = []

    for spec in sorted(agent_registry.list_agents(), key=lambda spec: spec.name):
        tools = sorted(
            (tool_registry.get(name).manifest() for name in spec.tool_names),
            key=lambda tool: tool.name,
        )
        agents.append(
            AgentManifestEntry(
                name=spec.name,
                description=spec.description,
                instruction=effective_instruction(spec),
                tools=tools,
                model=spec.model,
            )
        )

    return SystemCard(agents=agents)


def hash_system_card(card: SystemCard) -> str:
    """Computes a stable hash of the system card.

    Args:
        card: The system card to hash.

    Returns:
        A hex-encoded SHA-256 hash of the card's canonical JSON form.
    """
    canonical = card.model_dump_json()

    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
