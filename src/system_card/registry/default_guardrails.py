"""Registers the project's default guardrails into a GuardrailRegistry."""

from system_card.guardrails import cancellation_guardrail, comparative_claims_guardrail
from system_card.registry.guardrail_registry import GuardrailRegistry


def register_default_guardrails(registry: GuardrailRegistry) -> None:
    """Registers every default guardrail into the given registry.

    Args:
        registry: The registry to populate.
    """
    registry.register(comparative_claims_guardrail.build_spec())
    registry.register(cancellation_guardrail.build_spec())
