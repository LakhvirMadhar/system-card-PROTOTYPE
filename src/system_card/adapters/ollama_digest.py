"""Resolves a local Ollama model tag to its content digest via the Ollama API."""

import httpx


class OllamaDigestLookupError(Exception):
    """Raised when the Ollama API has no entry matching the requested model tag."""


def resolve_ollama_digest(model_tag: str, api_base: str) -> str:
    """Looks up the content digest backing a local Ollama model tag.

    A tag like "gemma4:latest" is mutable — pulling again can point it at
    different weights without the tag name changing. The digest is the
    actual content-addressable identifier, so it changes whenever the
    underlying model does.

    Args:
        model_tag: The Ollama model tag, e.g. "gemma4:latest".
        api_base: Base URL of the local Ollama server.

    Returns:
        The model's content digest, e.g. "c6eb396dbd59...".

    Raises:
        OllamaDigestLookupError: If no local model matches the given tag.
    """
    response = httpx.get(f"{api_base}/api/tags", timeout=5.0)
    response.raise_for_status()

    for entry in response.json()["models"]:
        if entry["name"] == model_tag:
            digest = entry["digest"]
            if not isinstance(digest, str):
                raise OllamaDigestLookupError(
                    f"Ollama returned a non-string digest for tag '{model_tag}'."
                )
            return digest

    raise OllamaDigestLookupError(f"No local Ollama model matches tag '{model_tag}'.")


class ModelDigestMismatchError(Exception):
    """Raised when a tag's live digest no longer matches the digest this project is pinned to."""


def verify_model_digest(model_tag: str, api_base: str, expected_digest: str) -> str:
    """Resolves a tag's live digest and confirms it matches the pinned digest.

    Ollama has no way to invoke a model by digest directly — only by tag — so
    a tag is never structurally immutable; re-pulling can repoint it at
    different weights. This is the only real version control available: pin
    the digest you tested against, and refuse to run silently on different
    weights if the tag ever drifts.

    Args:
        model_tag: The Ollama model tag, e.g. "gemma4:latest".
        api_base: Base URL of the local Ollama server.
        expected_digest: The digest this project is pinned to.

    Returns:
        The resolved digest, confirmed equal to expected_digest.

    Raises:
        OllamaDigestLookupError: If no local model matches the given tag.
        ModelDigestMismatchError: If the live digest no longer matches expected_digest.
    """
    actual_digest = resolve_ollama_digest(model_tag, api_base)

    if actual_digest != expected_digest:
        raise ModelDigestMismatchError(
            f"Tag '{model_tag}' now resolves to digest '{actual_digest}', but this "
            f"project is pinned to '{expected_digest}'. The model changed under the "
            "same tag — re-pin the expected digest once you've confirmed the change "
            "is intentional."
        )

    return actual_digest
