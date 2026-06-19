"""Trivial text analysis tool exposed to the agent."""


def word_count(text: str) -> int:
    """Counts the number of whitespace-separated words in text.

    Args:
        text: The input text to count words in.

    Returns:
        The number of words found. An empty or whitespace-only string returns 0.
    """
    return len(text.split())
