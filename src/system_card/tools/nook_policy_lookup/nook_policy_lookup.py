"""Looks up Nook's customer-facing policy text by topic.

Kept as a separate tool from nook_product_lookup deliberately: policy
text (returns, shipping, warranty terms) is reviewed and approved
content, distinct from the product catalog, and the two should be
trackable as independent surfaces in the system card.
"""

from system_card.tools.nook_policy_lookup.types import PolicyNotFoundError, PolicyTopic

_POLICIES: dict[str, str] = {
    "returns": "Returns are accepted within 30 days of delivery, in original packaging.",
    "shipping": "Standard shipping takes 3-5 business days. Expedited shipping is not yet offered.",
    "warranty": "All Nook Readers carry a 1-year limited warranty covering manufacturing defects.",
}


def nook_policy_lookup(topic: PolicyTopic) -> str:
    """Looks up Nook's policy text for a given topic.

    Args:
        topic: One of "returns", "shipping", "warranty".

    Returns:
        The policy text for that topic.

    Raises:
        PolicyNotFoundError: If no policy text exists for topic.
    """
    policy = _POLICIES.get(topic)
    if policy is None:
        raise PolicyNotFoundError(f"No policy found for topic '{topic}'.")

    return policy
