"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Infrastructure-level configuration shared across all agents.

    Per-agent model identity and hyperparameters do not belong here — those
    vary per agent and are passed explicitly as a ModelConfig instead, so
    running many agents on many models never means juggling one shared
    global settings object.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ollama_api_base: str = "http://localhost:11434"
