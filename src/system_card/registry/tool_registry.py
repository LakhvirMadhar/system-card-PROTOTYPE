"""Thread-safe registry of tools, keyed by name."""

import threading

from system_card.registry.exceptions import DuplicateToolError, ToolNotFoundError
from system_card.registry.tool_entry import ToolEntry
from system_card.schemas.tool_manifest import ToolManifestEntry


class ToolRegistry:
    """Holds registered tools and exposes their manifest entries."""

    def __init__(self) -> None:
        """Creates an empty registry."""
        self._entries: dict[str, ToolEntry] = {}
        self._lock = threading.RLock()

    def register(self, name: str, entry: ToolEntry) -> None:
        """Registers a tool entry under the given name.

        Args:
            name: The name the agent will call the tool by.
            entry: The lazy-loading handle to the tool's function.

        Raises:
            DuplicateToolError: If a tool is already registered under this name.
        """
        with self._lock:
            if name in self._entries:
                raise DuplicateToolError(f"Tool '{name}' is already registered.")
            self._entries[name] = entry

    def get(self, name: str) -> ToolEntry:
        """Returns the registered entry for a tool name.

        Args:
            name: The registered tool name.

        Returns:
            The tool's ToolEntry.

        Raises:
            ToolNotFoundError: If no tool is registered under this name.
        """
        with self._lock:
            entry = self._entries.get(name)

        if entry is None:
            raise ToolNotFoundError(f"No tool registered under '{name}'.")

        return entry

    def entries(self) -> list[ToolEntry]:
        """Returns every registered tool entry.

        Returns:
            One ToolEntry per registered tool.
        """
        with self._lock:
            return list(self._entries.values())

    def list_tools(self) -> list[ToolManifestEntry]:
        """Returns the manifest entry for every registered tool.

        Returns:
            One ToolManifestEntry per registered tool.
        """
        return [entry.manifest() for entry in self.entries()]
