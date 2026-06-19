"""Typed shape of the LLM model surface in the system card."""

from pydantic import BaseModel


class ModelConfig(BaseModel):
    """Describes the LLM backing the agent and its generation hyperparameters.

    Attributes:
        provider: The model backend, e.g. "ollama".
        model_name: The model identifier, e.g. "gemma4:latest".
        temperature: Sampling temperature.
        top_p: Nucleus sampling threshold.
        max_output_tokens: Maximum tokens to generate, or None if uncapped.
    """

    provider: str
    model_name: str
    temperature: float
    top_p: float
    max_output_tokens: int | None
