"""Integration tests for the Ollama digest adapter — requires a running local Ollama server."""

import pytest

from system_card.adapters.ollama_digest import (
    ModelDigestMismatchError,
    OllamaDigestLookupError,
    resolve_ollama_digest,
    verify_model_digest,
)

OLLAMA_API_BASE = "http://localhost:11434"
PINNED_MODEL_TAG = "gemma4:latest"
PINNED_MODEL_DIGEST = "c6eb396dbd5992bbe3f5cdb947e8bbc0ee413d7c17e2beaae69f5d569cf982eb"


def test_resolve_ollama_digest_returns_the_pinned_digest() -> None:
    digest = resolve_ollama_digest(PINNED_MODEL_TAG, OLLAMA_API_BASE)

    assert digest == PINNED_MODEL_DIGEST


def test_resolve_ollama_digest_raises_for_an_unknown_tag() -> None:
    with pytest.raises(OllamaDigestLookupError):
        resolve_ollama_digest("definitely-not-a-real-tag:latest", OLLAMA_API_BASE)


def test_verify_model_digest_passes_when_pinned_digest_matches() -> None:
    digest = verify_model_digest(PINNED_MODEL_TAG, OLLAMA_API_BASE, PINNED_MODEL_DIGEST)

    assert digest == PINNED_MODEL_DIGEST


def test_verify_model_digest_raises_when_pinned_digest_is_stale() -> None:
    with pytest.raises(ModelDigestMismatchError):
        verify_model_digest(PINNED_MODEL_TAG, OLLAMA_API_BASE, "stale-digest-from-before")
