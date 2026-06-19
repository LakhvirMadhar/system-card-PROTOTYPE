"""Typed shape of a single registered tool's entry in the system card manifest."""

from typing import Any

from pydantic import BaseModel


class ToolManifestEntry(BaseModel):
    """Describes one tool's LLM-facing surface for the system card.

    Attributes:
        name: The tool's registered name, as the agent sees it.
        description: The tool's docstring — part of what the LLM reads
            to decide when and how to call the tool.
        parameters: A JSON-schema-shaped description of the tool's
            callable signature.
    """

    name: str
    description: str
    parameters: dict[str, Any]
