"""Typed shape of one agent's resolved behavior surface in the system card."""

from pydantic import BaseModel

from system_card.schemas.guardrail_spec import GuardrailSpec
from system_card.schemas.model_config import ModelConfig
from system_card.schemas.tool_manifest import ToolManifestEntry


class AgentManifestEntry(BaseModel):
    """One agent's full behavior surface, with its tools resolved to manifests.

    This is the extension point for future per-agent surfaces (memory,
    planner config, etc.) — each one becomes a new field here when it's
    actually built, not before.

    Attributes:
        name: The agent's name.
        description: A short description of the agent. ADK injects this into
            the model-facing system instruction alongside the agent's name,
            so it's part of the card's behavior surface, not just metadata.
        instruction: The full effective system instruction the model actually
            receives — the configured instruction plus ADK's own injected
            identity preamble (see services.agent_service.effective_instruction).
            Deliberately not just the raw configured string, since that alone
            wouldn't match what the model is given.
        tools: This agent's equipped tools, resolved to their manifest
            entries and sorted by name for deterministic hashing.
        model: The model and generation hyperparameters this agent runs with.
        guardrails: This agent's wired guardrails, resolved to their full
            specs and sorted by name. A guardrail's injected instruction
            never appears in `instruction` above — it's only added to a
            turn's effective prompt when the guardrail actually fires — so
            without recording it here, adding or changing a guardrail would
            be an invisible change to anyone just reading the agent's code.
    """

    name: str
    description: str
    instruction: str
    tools: list[ToolManifestEntry]
    model: ModelConfig
    guardrails: list[GuardrailSpec]
