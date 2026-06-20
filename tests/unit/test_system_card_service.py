"""Unit tests for the system card service — the project's central versioning guarantee."""

from system_card.registry.default_tools import register_default_tools
from system_card.registry.tool_entry import ToolEntry
from system_card.registry.tool_registry import ToolRegistry
from system_card.schemas.model_config import ModelConfig, ModelProvider
from system_card.services.system_card_service import build_system_card, hash_system_card


def _populated_registry() -> ToolRegistry:
    registry = ToolRegistry()
    register_default_tools(registry)

    return registry


def _model(temperature: float = 0.7, model_digest: str = "abc123") -> ModelConfig:
    return ModelConfig(
        provider=ModelProvider.OLLAMA,
        model_name="gemma4:latest",
        model_digest=model_digest,
        temperature=temperature,
        top_p=1.0,
        top_k=64,
        seed=None,
        presence_penalty=None,
        frequency_penalty=None,
        stop_sequences=None,
        max_output_tokens=None,
    )


def test_build_system_card_includes_every_registered_tool() -> None:
    card = build_system_card(_populated_registry(), _model())

    names = [tool.name for tool in card.tools]
    assert names == sorted(names)
    assert set(names) == {
        "calculator",
        "dad_joke",
        "shakespearify",
        "coin_flip",
        "word_count",
        "ollama_list",
    }


def test_build_system_card_includes_the_model_surface() -> None:
    card = build_system_card(_populated_registry(), _model())

    assert card.model.model_name == "gemma4:latest"
    assert card.model.temperature == 0.7


def test_hash_is_a_64_character_hex_digest() -> None:
    card_hash = hash_system_card(build_system_card(_populated_registry(), _model()))

    assert len(card_hash) == 64
    assert all(char in "0123456789abcdef" for char in card_hash)


def test_hash_is_stable_for_the_same_registry_and_model() -> None:
    first_hash = hash_system_card(build_system_card(_populated_registry(), _model()))
    second_hash = hash_system_card(build_system_card(_populated_registry(), _model()))

    assert first_hash == second_hash


def test_hash_changes_when_a_tool_is_added() -> None:
    before = hash_system_card(build_system_card(_populated_registry(), _model()))

    registry = _populated_registry()
    registry.register(
        "dice_roll",
        ToolEntry(module_path="system_card.tools.word_count", fn_name="word_count"),
    )
    after = hash_system_card(build_system_card(registry, _model()))

    assert before != after


def test_hash_changes_when_a_hyperparameter_changes() -> None:
    before = hash_system_card(build_system_card(_populated_registry(), _model(temperature=0.7)))
    after = hash_system_card(build_system_card(_populated_registry(), _model(temperature=0.2)))

    assert before != after


def test_hash_changes_when_the_model_digest_changes_even_if_the_tag_does_not() -> None:
    card_before = build_system_card(_populated_registry(), _model(model_digest="abc123"))
    card_after = build_system_card(_populated_registry(), _model(model_digest="def456"))

    assert hash_system_card(card_before) != hash_system_card(card_after)


def test_hash_changes_when_seed_changes() -> None:
    registry = _populated_registry()
    model_without_seed = _model()
    model_with_seed = model_without_seed.model_copy(update={"seed": 42})

    before = hash_system_card(build_system_card(registry, model_without_seed))
    after = hash_system_card(build_system_card(registry, model_with_seed))

    assert before != after
