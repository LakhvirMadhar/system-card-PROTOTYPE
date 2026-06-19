"""Trivial randomness tool exposed to the agent."""

from system_card.tools.coin_flip.coin_flip import coin_flip
from system_card.tools.coin_flip.types import CoinFace

__all__ = ["CoinFace", "coin_flip"]
