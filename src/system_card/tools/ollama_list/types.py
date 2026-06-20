"""Types for the ollama_list tool, kept separate so importing them never pulls in the tool."""


class OllamaListError(Exception):
    """Raised when the Ollama API is unreachable or returns an unexpected response."""
