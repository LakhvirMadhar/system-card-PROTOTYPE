"""Registers the project's toy tools into a ToolRegistry."""

from system_card.registry.tool_entry import ToolEntry
from system_card.registry.tool_registry import ToolRegistry

_DEFAULT_TOOLS: tuple[tuple[str, str, str], ...] = (
    ("calculator", "system_card.tools.calculator", "calculator"),
    ("dad_joke", "system_card.tools.dad_joke", "dad_joke"),
    ("shakespearify", "system_card.tools.shakespearify", "shakespearify"),
    ("coin_flip", "system_card.tools.coin_flip", "coin_flip"),
    ("word_count", "system_card.tools.word_count", "word_count"),
)


def register_default_tools(registry: ToolRegistry) -> None:
    """Registers every toy tool from system_card.tools into the given registry.

    Args:
        registry: The registry to populate.
    """
    for name, module_path, fn_name in _DEFAULT_TOOLS:
        registry.register(name, ToolEntry(module_path=module_path, fn_name=fn_name))
