"""Mock-Shakespearean text rewriting tool exposed to the agent."""

import re

_REPLACEMENTS: dict[str, str] = {
    "you": "thou",
    "your": "thy",
    "yours": "thine",
    "are": "art",
    "is": "'tis",
    "my": "mine",
    "hello": "hail",
    "friend": "fellow",
}


def shakespearify(text: str) -> str:
    """Rewrites text with mock-Shakespearean word substitutions.

    Args:
        text: The input text to rewrite.

    Returns:
        The text with common words swapped for archaic equivalents,
        case-insensitively, preserving the original capitalisation style.
    """

    def replace(match: re.Match[str]) -> str:
        word = match.group(0)
        replacement = _REPLACEMENTS.get(word.lower())

        if replacement is None:
            return word

        return replacement.capitalize() if word[0].isupper() else replacement

    return re.sub(r"\b\w+\b", replace, text)
