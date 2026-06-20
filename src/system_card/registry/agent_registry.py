"""Thread-safe registry of agent specs, keyed by name."""

import threading

from system_card.registry.exceptions import AgentNotFoundError, DuplicateAgentError
from system_card.schemas.agent_spec import AgentSpec


class AgentRegistry:
    """Holds registered agent specs."""

    def __init__(self) -> None:
        """Creates an empty registry."""
        self._specs: dict[str, AgentSpec] = {}
        self._lock = threading.RLock()

    def register(self, spec: AgentSpec) -> None:
        """Registers an agent spec under its own name.

        Args:
            spec: The agent configuration to register.

        Raises:
            DuplicateAgentError: If an agent is already registered under this name.
        """
        with self._lock:
            if spec.name in self._specs:
                raise DuplicateAgentError(f"Agent '{spec.name}' is already registered.")
            self._specs[spec.name] = spec

    def get(self, name: str) -> AgentSpec:
        """Returns the registered spec for an agent name.

        Args:
            name: The registered agent name.

        Returns:
            The agent's AgentSpec.

        Raises:
            AgentNotFoundError: If no agent is registered under this name.
        """
        with self._lock:
            spec = self._specs.get(name)

        if spec is None:
            raise AgentNotFoundError(f"No agent registered under '{name}'.")

        return spec

    def list_agents(self) -> list[AgentSpec]:
        """Returns every registered agent spec.

        Returns:
            One AgentSpec per registered agent.
        """
        with self._lock:
            return list(self._specs.values())
