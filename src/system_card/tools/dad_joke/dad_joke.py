"""Dad joke tool exposed to the agent."""

import random

_JOKES: tuple[str, ...] = (
    "I'm reading a book about anti-gravity. It's impossible to put down.",
    "Did you hear about the claustrophobic astronaut? He just needed a little space.",
    "Why don't skeletons fight each other? They don't have the guts.",
    "I used to be a banker, but I lost interest.",
    "Why did the scarecrow win an award? He was outstanding in his field.",
    "I would tell you a chemistry joke, but I know I wouldn't get a reaction.",
)


def dad_joke() -> str:
    """Returns a random, groan-worthy dad joke from a fixed list.

    Returns:
        A single joke as a plain string.
    """
    return random.choice(_JOKES)
