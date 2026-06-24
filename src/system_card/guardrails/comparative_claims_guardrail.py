"""Defines the comparative_claims_guardrail — detects competitor comparison requests."""

from system_card.schemas.guardrail_spec import GuardrailSpec

NAME = "comparative_claims_guardrail"

TRIGGER_KEYWORDS = ("competitor", "better than", "vs", "versus", "compared to")

CLASSIFIER_INSTRUCTION = (
    "Detect whether the customer is asking for a comparison between Nook and "
    "a competing product or brand."
)

INJECTED_INSTRUCTION = (
    "The customer's message may be asking for a comparison against a competitor. "
    "Do not make comparative claims about other brands or products. Stick to "
    "factual information about Nook's own products and policies only."
)


def build_spec() -> GuardrailSpec:
    """Builds this guardrail's spec.

    Returns:
        This guardrail's GuardrailSpec.
    """
    return GuardrailSpec(
        name=NAME,
        trigger_keywords=TRIGGER_KEYWORDS,
        classifier_instruction=CLASSIFIER_INSTRUCTION,
        injected_instruction=INJECTED_INSTRUCTION,
    )
