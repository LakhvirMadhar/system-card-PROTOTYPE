"""Typed shape of the LLM model surface in the system card."""

from pydantic import BaseModel


class ModelConfig(BaseModel):
    """Describes the LLM backing the agent and its generation hyperparameters.

    Attributes:
        provider: The model backend, e.g. "ollama".
        model_name: The model identifier, e.g. "gemma4:latest". This can be
            a mutable tag — see model_digest.
        model_digest: The model's actual content-addressable identifier,
            e.g. an Ollama digest, if the provider exposes one. None if the
            provider gives no way to pin the exact weights (e.g. a bare
            cloud model name with no resolvable snapshot). A card hash is
            only trustworthy as "the exact model that ran" when this is set.
        temperature: Sampling temperature.
        top_p: Nucleus sampling threshold.
        max_output_tokens: Maximum tokens to generate, or None if uncapped.
    """

    provider: str
    model_name: str
    model_digest: str | None
    temperature: float
    top_p: float
    max_output_tokens: int | None
