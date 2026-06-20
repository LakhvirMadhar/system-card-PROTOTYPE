"""Unit tests for the tool registry."""

import pytest

from system_card.registry.default_tools import register_default_tools
from system_card.registry.exceptions import DuplicateToolError, ToolNotFoundError
from system_card.registry.tool_entry import ToolEntry
from system_card.registry.tool_registry import ToolRegistry


def test_register_and_get_returns_the_same_entry() -> None:
    registry = ToolRegistry()
    entry = ToolEntry(module_path="system_card.tools.word_count", fn_name="word_count")

    registry.register("word_count", entry)

    assert registry.get("word_count") is entry


def test_register_duplicate_name_raises() -> None:
    registry = ToolRegistry()
    registry.register(
        "word_count",
        ToolEntry(module_path="system_card.tools.word_count", fn_name="word_count"),
    )

    with pytest.raises(DuplicateToolError):
        registry.register(
            "word_count",
            ToolEntry(module_path="system_card.tools.word_count", fn_name="word_count"),
        )


def test_get_unregistered_name_raises() -> None:
    registry = ToolRegistry()

    with pytest.raises(ToolNotFoundError):
        registry.get("nonexistent")


def test_entry_run_calls_the_underlying_function() -> None:
    entry = ToolEntry(module_path="system_card.tools.word_count", fn_name="word_count")

    assert entry.run(text="a b c") == 3


def test_entry_manifest_captures_name_description_and_parameters() -> None:
    entry = ToolEntry(module_path="system_card.tools.word_count", fn_name="word_count")

    manifest = entry.manifest()

    assert manifest.name == "word_count"
    assert "Counts the number of whitespace-separated words" in manifest.description
    assert "text" in manifest.parameters["properties"]


def test_register_default_tools_registers_all_six() -> None:
    registry = ToolRegistry()

    register_default_tools(registry)

    names = {entry.name for entry in registry.list_tools()}
    assert names == {
        "calculator",
        "dad_joke",
        "shakespearify",
        "coin_flip",
        "word_count",
        "ollama_list",
    }
