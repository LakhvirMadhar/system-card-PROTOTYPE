"""Registers the project's toy tools into a ToolRegistry."""

from system_card.registry.tool_entry import ToolEntry
from system_card.registry.tool_registry import ToolRegistry

_DEFAULT_TOOLS: tuple[tuple[str, str, str], ...] = (
    ("calculator", "system_card.tools.calculator", "calculator"),
    ("dad_joke", "system_card.tools.dad_joke", "dad_joke"),
    ("shakespearify", "system_card.tools.shakespearify", "shakespearify"),
    ("coin_flip", "system_card.tools.coin_flip", "coin_flip"),
    ("word_count", "system_card.tools.word_count", "word_count"),
    ("ollama_list", "system_card.tools.ollama_list", "ollama_list"),
    (
        "nook_product_lookup",
        "system_card.tools.nook_product_lookup",
        "nook_product_lookup",
    ),
    (
        "nook_policy_lookup",
        "system_card.tools.nook_policy_lookup",
        "nook_policy_lookup",
    ),
    (
        "escalate_to_specialist",
        "system_card.tools.escalate_to_specialist",
        "escalate_to_specialist",
    ),
)


def register_default_tools(registry: ToolRegistry) -> None:
    """Registers every toy tool from system_card.tools into the given registry.

    Args:
        registry: The registry to populate.
    """
    for name, module_path, fn_name in _DEFAULT_TOOLS:
        registry.register(name, ToolEntry(module_path=module_path, fn_name=fn_name))
