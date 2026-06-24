"""Thread-safe registry of guardrail specs, keyed by name."""

import threading

from system_card.registry.exceptions import DuplicateGuardrailError, GuardrailNotFoundError
from system_card.schemas.guardrail_spec import GuardrailSpec


class GuardrailRegistry:
    """Holds registered guardrail specs."""

    def __init__(self) -> None:
        """Creates an empty registry."""
        self._specs: dict[str, GuardrailSpec] = {}
        self._lock = threading.RLock()

    def register(self, spec: GuardrailSpec) -> None:
        """Registers a guardrail spec under its own name.

        Args:
            spec: The guardrail configuration to register.

        Raises:
            DuplicateGuardrailError: If a guardrail is already registered
                under this name.
        """
        with self._lock:
            if spec.name in self._specs:
                raise DuplicateGuardrailError(f"Guardrail '{spec.name}' is already registered.")
            self._specs[spec.name] = spec

    def get(self, name: str) -> GuardrailSpec:
        """Returns the registered spec for a guardrail name.

        Args:
            name: The registered guardrail name.

        Returns:
            The guardrail's GuardrailSpec.

        Raises:
            GuardrailNotFoundError: If no guardrail is registered under this name.
        """
        with self._lock:
            spec = self._specs.get(name)

        if spec is None:
            raise GuardrailNotFoundError(f"No guardrail registered under '{name}'.")

        return spec

    def list_guardrails(self) -> list[GuardrailSpec]:
        """Returns every registered guardrail spec.

        Returns:
            One GuardrailSpec per registered guardrail.
        """
        with self._lock:
            return list(self._specs.values())
