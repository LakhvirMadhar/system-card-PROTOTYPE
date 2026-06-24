"""Typed shape of a diff between two system card versions."""

from pydantic import BaseModel


class ToolDiff(BaseModel):
    """One tool's change between two card versions.

    Attributes:
        name: The tool's name.
        change: Whether the tool was added, removed, or had its
            description/schema changed.
    """

    name: str
    change: str


class AgentDiff(BaseModel):
    """One agent's changes between two card versions.

    Attributes:
        name: The agent's name.
        change: Whether the agent itself was added, removed, or changed.
        tool_diffs: Per-tool changes, only present when change == "changed".
        instruction_changed: Whether the system instruction text changed.
        model_changed: Whether the model config (name/digest/hyperparameters)
            changed.
    """

    name: str
    change: str
    tool_diffs: list[ToolDiff] = []
    instruction_changed: bool = False
    model_changed: bool = False


class SystemCardDiff(BaseModel):
    """The full set of agent-level changes between two card versions.

    Attributes:
        agent_diffs: One entry per agent that was added, removed, or changed.
            An unchanged agent has no entry at all.
    """

    agent_diffs: list[AgentDiff]

    def is_empty(self) -> bool:
        """Returns whether the two cards differ at all."""
        return len(self.agent_diffs) == 0
