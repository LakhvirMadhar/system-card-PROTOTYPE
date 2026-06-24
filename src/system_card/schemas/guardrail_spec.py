"""Typed shape describing a single guardrail's configuration."""

from pydantic import BaseModel


class GuardrailSpec(BaseModel):
    """Declares a guardrail's trigger condition and the instruction it injects.

    A guardrail is a conditionally-injected instruction: it never appears in
    an agent's static instruction text, only in the model-facing prompt for
    turns where its trigger condition matches the incoming message. This is
    exactly the kind of runtime-assembled surface a plain file diff can't
    show — the system card resolves it explicitly so it's still tracked.

    Attributes:
        name: The guardrail's unique name.
        trigger_keywords: Lowercase keywords; the guardrail fires for a turn
            if any keyword appears in the incoming message. Deliberately
            simple/deterministic rather than a second LLM classifier call,
            so triggering is testable without a live model.
        classifier_instruction: Describes, for documentation/extensibility,
            what this guardrail is meant to detect. Not executed today —
            the real trigger check is trigger_keywords — but kept as a
            schema field so a future LLM-based classifier could replace the
            keyword check without changing the card's shape.
        injected_instruction: The instruction appended to the agent's
            effective instruction for a turn where this guardrail fires.
    """

    name: str
    trigger_keywords: tuple[str, ...]
    classifier_instruction: str
    injected_instruction: str
