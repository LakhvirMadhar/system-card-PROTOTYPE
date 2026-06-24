"""Unit tests for the system card service — the project's central versioning guarantee."""

from system_card.registry.agent_registry import AgentRegistry
from system_card.registry.default_tools import register_default_tools
from system_card.registry.guardrail_registry import GuardrailRegistry
from system_card.registry.tool_entry import ToolEntry
from system_card.registry.tool_registry import ToolRegistry
from system_card.schemas.agent_spec import AgentSpec
from system_card.schemas.model_config import ModelConfig, ModelProvider
from system_card.services.system_card_service import build_system_card, hash_system_card


def _populated_tool_registry() -> ToolRegistry:
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


def _agent_registry(
    model: ModelConfig | None = None,
    tool_names: tuple[str, ...] = ("calculator", "dad_joke"),
    name: str = "test_agent",
    description: str = "A test agent.",
) -> AgentRegistry:
    registry = AgentRegistry()
    registry.register(
        AgentSpec(
            name=name,
            description=description,
            instruction="Use the available tools.",
            model=model or _model(),
            tool_names=tool_names,
        )
    )

    return registry


def test_build_system_card_includes_every_registered_agent() -> None:
    card = build_system_card(_agent_registry(), _populated_tool_registry(), GuardrailRegistry())

    assert [agent.name for agent in card.agents] == ["test_agent"]


def test_build_system_card_resolves_each_agents_tools() -> None:
    card = build_system_card(_agent_registry(), _populated_tool_registry(), GuardrailRegistry())

    names = [tool.name for tool in card.agents[0].tools]
    assert names == sorted(names)
    assert set(names) == {"calculator", "dad_joke"}


def test_build_system_card_includes_each_agents_model_surface() -> None:
    card = build_system_card(
        _agent_registry(model=_model(temperature=0.3)),
        _populated_tool_registry(),
        GuardrailRegistry(),
    )

    assert card.agents[0].model.temperature == 0.3


def test_hash_is_a_64_character_hex_digest() -> None:
    card_hash = hash_system_card(
        build_system_card(_agent_registry(), _populated_tool_registry(), GuardrailRegistry())
    )

    assert len(card_hash) == 64
    assert all(char in "0123456789abcdef" for char in card_hash)


def test_hash_is_stable_for_the_same_agents_and_tools() -> None:
    tool_registry = _populated_tool_registry()
    guardrail_registry = GuardrailRegistry()

    first_hash = hash_system_card(
        build_system_card(_agent_registry(), tool_registry, guardrail_registry)
    )
    second_hash = hash_system_card(
        build_system_card(_agent_registry(), tool_registry, guardrail_registry)
    )

    assert first_hash == second_hash


def test_hash_changes_when_an_agent_gains_a_tool() -> None:
    tool_registry = _populated_tool_registry()
    guardrail_registry = GuardrailRegistry()

    before = hash_system_card(
        build_system_card(
            _agent_registry(tool_names=("calculator",)), tool_registry, guardrail_registry
        )
    )
    after = hash_system_card(
        build_system_card(
            _agent_registry(tool_names=("calculator", "dad_joke")),
            tool_registry,
            guardrail_registry,
        )
    )

    assert before != after


def test_hash_changes_when_description_changes_even_if_instruction_text_does_not() -> None:
    """description is folded into the model-facing effective instruction (ADK injects it),
    so it has to affect the hash even with the raw instruction string held constant."""
    tool_registry = _populated_tool_registry()
    guardrail_registry = GuardrailRegistry()

    before = hash_system_card(
        build_system_card(
            _agent_registry(description="Agent A."), tool_registry, guardrail_registry
        )
    )
    after = hash_system_card(
        build_system_card(
            _agent_registry(description="Agent B."), tool_registry, guardrail_registry
        )
    )

    assert before != after


def test_hash_changes_when_a_hyperparameter_changes() -> None:
    tool_registry = _populated_tool_registry()
    guardrail_registry = GuardrailRegistry()

    before = hash_system_card(
        build_system_card(
            _agent_registry(model=_model(temperature=0.7)), tool_registry, guardrail_registry
        )
    )
    after = hash_system_card(
        build_system_card(
            _agent_registry(model=_model(temperature=0.2)), tool_registry, guardrail_registry
        )
    )

    assert before != after


def test_hash_changes_when_the_model_digest_changes_even_if_the_tag_does_not() -> None:
    tool_registry = _populated_tool_registry()
    guardrail_registry = GuardrailRegistry()

    card_before = build_system_card(
        _agent_registry(model=_model(model_digest="abc123")), tool_registry, guardrail_registry
    )
    card_after = build_system_card(
        _agent_registry(model=_model(model_digest="def456")), tool_registry, guardrail_registry
    )

    assert hash_system_card(card_before) != hash_system_card(card_after)


def test_hash_changes_when_seed_changes() -> None:
    tool_registry = _populated_tool_registry()
    guardrail_registry = GuardrailRegistry()
    model_without_seed = _model()
    model_with_seed = model_without_seed.model_copy(update={"seed": 42})

    before = hash_system_card(
        build_system_card(
            _agent_registry(model=model_without_seed), tool_registry, guardrail_registry
        )
    )
    after = hash_system_card(
        build_system_card(_agent_registry(model=model_with_seed), tool_registry, guardrail_registry)
    )

    assert before != after


def test_hash_changes_when_a_second_agent_is_added() -> None:
    tool_registry = _populated_tool_registry()
    guardrail_registry = GuardrailRegistry()

    one_agent = _agent_registry()
    before = hash_system_card(build_system_card(one_agent, tool_registry, guardrail_registry))

    two_agents = _agent_registry()
    two_agents.register(
        AgentSpec(
            name="second_agent",
            description="A test agent.",
            instruction="Use the available tools.",
            model=_model(),
            tool_names=("coin_flip",),
        )
    )
    after = hash_system_card(build_system_card(two_agents, tool_registry, guardrail_registry))

    assert before != after


def test_hash_does_not_change_when_an_unused_tool_is_added_to_the_registry() -> None:
    tool_registry = _populated_tool_registry()
    guardrail_registry = GuardrailRegistry()
    agent_registry = _agent_registry(tool_names=("calculator",))

    before = hash_system_card(build_system_card(agent_registry, tool_registry, guardrail_registry))

    tool_registry.register(
        "dice_roll",
        ToolEntry(module_path="system_card.tools.word_count", fn_name="word_count"),
    )
    after = hash_system_card(build_system_card(agent_registry, tool_registry, guardrail_registry))

    assert before == after
