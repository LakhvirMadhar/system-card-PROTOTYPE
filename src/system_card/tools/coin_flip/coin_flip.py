"""Trivial randomness tool exposed to the agent."""

import random

from system_card.tools.coin_flip.types import CoinFace


def coin_flip() -> CoinFace:
    """Flips a fair coin.

    Returns:
        Either "heads" or "tails", each with equal probability.
    """
    return random.choice(("heads", "tails"))
