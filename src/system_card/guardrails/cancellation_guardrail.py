"""Defines the cancellation_guardrail — detects cancellation/frustration intent."""

from system_card.schemas.guardrail_spec import GuardrailSpec

NAME = "cancellation_guardrail"

TRIGGER_KEYWORDS = ("cancel", "refund", "frustrated", "angry", "fed up")

CLASSIFIER_INSTRUCTION = (
    "Detect whether the customer is expressing intent to cancel, asking for a "
    "refund, or showing frustration severe enough to warrant human attention."
)

INJECTED_INSTRUCTION = (
    "The customer's message may signal a cancellation request or significant "
    "frustration. Respond with empathy first. Do not attempt to talk the "
    "customer out of cancelling yourself — use escalate_to_specialist instead "
    "of resolving this directly."
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
