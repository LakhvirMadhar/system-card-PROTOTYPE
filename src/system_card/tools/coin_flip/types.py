"""Types for the coin flip tool, kept separate so importing them never pulls in the tool itself."""

from typing import Literal

CoinFace = Literal["heads", "tails"]
