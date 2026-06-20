"""Typed shape of the LLM model surface in the system card."""

from enum import StrEnum

from pydantic import BaseModel


class ModelProvider(StrEnum):
    """Routing path a model is served through — not the model family.

    Bedrock and Vertex AI can each serve multiple model families (Anthropic,
    Meta, Mistral, etc.), so the provider only says how the call is routed,
    not which model answers it; that distinction matters for the system card
    because the same model name can mean different infra, auth, and
    availability depending on the route. Values match litellm's own provider
    identifiers (the model-routing layer this project uses) so they plug
    directly into a litellm model string, without this schema importing
    litellm itself.
    """

    OLLAMA = "ollama"
    OLLAMA_CHAT = "ollama_chat"
    ANTHROPIC = "anthropic"
    BEDROCK = "bedrock"
    VERTEX_AI = "vertex_ai"
    AZURE = "azure"
    OPENAI = "openai"


class ModelConfig(BaseModel):
    """Describes the LLM backing the agent and its generation hyperparameters.

    Every field here is something agent_service.py actually configures on the
    agent, not just metadata — a field that's recorded but not enforced would
    let the card silently drift from what's really running.

    Attributes:
        provider: The routing path the model is served through.
        model_name: The model identifier as given to the provider, e.g.
            "gemma4:latest". This can be a mutable tag — see model_digest.
        model_digest: The model's actual content-addressable identifier,
            e.g. an Ollama digest, if the provider exposes one. None if the
            provider gives no way to pin the exact weights (e.g. a bare
            cloud model name with no resolvable snapshot). A card hash is
            only trustworthy as "the exact model that ran" when this is set.
        temperature: Sampling temperature.
        top_p: Nucleus sampling threshold.
        top_k: Number of highest-probability tokens considered at each step,
            or None to leave it at the provider's default.
        seed: Fixed sampling seed for reproducible output, or None for
            natural (non-reproducible) sampling.
        presence_penalty: Penalty for tokens already present in the output,
            or None to leave it at the provider's default.
        frequency_penalty: Penalty scaling with how often a token has
            already appeared, or None to leave it at the provider's default.
        stop_sequences: Sequences that end generation early, or None.
        max_output_tokens: Maximum tokens to generate, or None if uncapped.
    """

    provider: ModelProvider
    model_name: str
    model_digest: str | None
    temperature: float
    top_p: float
    top_k: int | None
    seed: int | None
    presence_penalty: float | None
    frequency_penalty: float | None
    stop_sequences: tuple[str, ...] | None
    max_output_tokens: int | None
