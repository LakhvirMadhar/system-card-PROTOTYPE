"""Builds the system card from the tool registry and computes its hash."""

import hashlib

from system_card.registry.tool_registry import ToolRegistry
from system_card.schemas.model_config import ModelConfig
from system_card.schemas.system_card import SystemCard


def build_system_card(registry: ToolRegistry, model: ModelConfig) -> SystemCard:
    """Builds the system card from every tool currently registered plus the model surface.

    Args:
        registry: The populated tool registry.
        model: The model and generation hyperparameters actually configured on the agent.

    Returns:
        A SystemCard capturing the current tool and model surface, tools sorted by name.
    """
    tools = sorted(registry.list_tools(), key=lambda entry: entry.name)

    return SystemCard(tools=tools, model=model)


def hash_system_card(card: SystemCard) -> str:
    """Computes a stable hash of the system card.

    Args:
        card: The system card to hash.

    Returns:
        A hex-encoded SHA-256 hash of the card's canonical JSON form.
    """
    canonical = card.model_dump_json()

    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
