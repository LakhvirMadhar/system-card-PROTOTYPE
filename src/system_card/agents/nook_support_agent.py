"""Defines the nook_support_agent — Nook Inc.'s contact-center agent.

A fictional contact-center scenario inspired by — not copied from — a
published case study on agentic contact-center risks. All tools, prompts,
and guardrails here are original. The point of this agent over the toy
calculator/dad_joke demo: it has guardrails wired in, whose injected
instructions never appear in INSTRUCTION below — making them exactly the
kind of runtime-assembled surface a plain file diff can't show, but the
system card resolves explicitly.
"""

from system_card.schemas.agent_spec import AgentSpec
from system_card.schemas.model_config import ModelConfig

NAME = "nook_support_agent"

DESCRIPTION = "Nook Inc.'s customer support agent for product, policy, and escalation requests."

INSTRUCTION = (
    "Use the available tools to answer the customer's request about Nook products and "
    "policies. When you reply, name which tool(s) you used and what each one returned. "
    "Escalate to a specialist when you cannot resolve the request directly."
)

TOOL_NAMES = ("nook_product_lookup", "nook_policy_lookup", "escalate_to_specialist")

GUARDRAIL_NAMES = ("comparative_claims_guardrail", "cancellation_guardrail")

PINNED_MODEL_TAG = "gemma4:latest"
PINNED_MODEL_DIGEST = "c6eb396dbd5992bbe3f5cdb947e8bbc0ee413d7c17e2beaae69f5d569cf982eb"


def build_spec(model: ModelConfig) -> AgentSpec:
    """Builds this agent's spec for the given model configuration.

    Args:
        model: The model and generation hyperparameters to run this agent
            with — construct it from PINNED_MODEL_TAG/PINNED_MODEL_DIGEST.

    Returns:
        This agent's AgentSpec.
    """
    return AgentSpec(
        name=NAME,
        description=DESCRIPTION,
        instruction=INSTRUCTION,
        model=model,
        tool_names=TOOL_NAMES,
        guardrail_names=GUARDRAIL_NAMES,
    )
