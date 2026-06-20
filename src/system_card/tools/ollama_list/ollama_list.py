"""Tool that lists locally available Ollama models, exposed to the agent."""

import httpx

from system_card.tools.ollama_list.types import OllamaListError


def ollama_list(api_base: str = "http://localhost:11434") -> list[str]:
    """Lists the names of Ollama models currently available on this machine.

    Args:
        api_base: Base URL of the local Ollama server. Leave at the default
            unless Ollama is reachable somewhere else.

    Returns:
        One model name (e.g. "gemma4:latest") per locally available model.

    Raises:
        OllamaListError: If the Ollama API is unreachable or returns an
            unexpected response.
    """
    try:
        response = httpx.get(f"{api_base}/api/tags", timeout=5.0)
        response.raise_for_status()
    except httpx.HTTPError as error:
        raise OllamaListError("Failed to reach the Ollama API.") from error

    return [entry["name"] for entry in response.json()["models"]]
