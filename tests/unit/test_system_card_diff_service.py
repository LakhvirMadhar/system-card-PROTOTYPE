"""Unit tests for diffing two system card versions."""

from system_card.schemas.agent_manifest import AgentManifestEntry
from system_card.schemas.model_config import ModelConfig, ModelProvider
from system_card.schemas.system_card import SystemCard
from system_card.schemas.system_card_diff import ToolDiff
from system_card.schemas.tool_manifest import ToolManifestEntry
from system_card.services.system_card_diff_service import diff_system_cards, format_diff


def _model(temperature: float = 0.7) -> ModelConfig:
    return ModelConfig(
        provider=ModelProvider.OLLAMA,
        model_name="gemma4:latest",
        model_digest="abc123",
        temperature=temperature,
        top_p=1.0,
        top_k=64,
        seed=None,
        presence_penalty=None,
        frequency_penalty=None,
        stop_sequences=None,
        max_output_tokens=None,
    )


def _tool(name: str = "calculator", description: str = "Adds numbers.") -> ToolManifestEntry:
    return ToolManifestEntry(name=name, description=description, parameters={})


def _agent(
    name: str = "agent",
    tools: list[ToolManifestEntry] | None = None,
    instruction: str = "Be helpful.",
    model: ModelConfig | None = None,
) -> AgentManifestEntry:
    return AgentManifestEntry(
        name=name,
        instruction=instruction,
        tools=tools if tools is not None else [_tool()],
        model=model if model is not None else _model(),
    )


def test_identical_cards_produce_an_empty_diff() -> None:
    card = SystemCard(agents=[_agent()])

    diff = diff_system_cards(card, card)

    assert diff.is_empty()


def test_added_tool_is_reported_on_the_agent_it_was_added_to() -> None:
    old = SystemCard(agents=[_agent(tools=[_tool("calculator")])])
    new = SystemCard(agents=[_agent(tools=[_tool("calculator"), _tool("dad_joke")])])

    diff = diff_system_cards(old, new)

    assert len(diff.agent_diffs) == 1
    agent_diff = diff.agent_diffs[0]
    assert agent_diff.change == "changed"
    assert agent_diff.tool_diffs == [ToolDiff(name="dad_joke", change="added")]


def test_removed_tool_is_reported() -> None:
    old = SystemCard(agents=[_agent(tools=[_tool("calculator"), _tool("dad_joke")])])
    new = SystemCard(agents=[_agent(tools=[_tool("calculator")])])

    diff = diff_system_cards(old, new)

    assert diff.agent_diffs[0].tool_diffs[0].name == "dad_joke"
    assert diff.agent_diffs[0].tool_diffs[0].change == "removed"


def test_changed_tool_description_is_reported_as_changed_not_added_and_removed() -> None:
    old = SystemCard(agents=[_agent(tools=[_tool("calculator", "Old description.")])])
    new = SystemCard(agents=[_agent(tools=[_tool("calculator", "New description.")])])

    diff = diff_system_cards(old, new)

    assert len(diff.agent_diffs[0].tool_diffs) == 1
    assert diff.agent_diffs[0].tool_diffs[0].change == "changed"


def test_instruction_change_is_flagged_without_a_tool_diff() -> None:
    old = SystemCard(agents=[_agent(instruction="Old instruction.")])
    new = SystemCard(agents=[_agent(instruction="New instruction.")])

    diff = diff_system_cards(old, new)

    assert diff.agent_diffs[0].instruction_changed is True
    assert diff.agent_diffs[0].tool_diffs == []


def test_model_change_is_flagged() -> None:
    old = SystemCard(agents=[_agent(model=_model(temperature=0.7))])
    new = SystemCard(agents=[_agent(model=_model(temperature=0.2))])

    diff = diff_system_cards(old, new)

    assert diff.agent_diffs[0].model_changed is True


def test_added_and_removed_agents_are_both_reported() -> None:
    old = SystemCard(agents=[_agent(name="agent_a")])
    new = SystemCard(agents=[_agent(name="agent_b")])

    diff = diff_system_cards(old, new)

    changes = {(d.name, d.change) for d in diff.agent_diffs}
    assert changes == {("agent_a", "removed"), ("agent_b", "added")}


def test_format_diff_renders_added_tool_with_a_plus_marker() -> None:
    old = SystemCard(agents=[_agent(tools=[_tool("calculator")])])
    new = SystemCard(agents=[_agent(tools=[_tool("calculator"), _tool("dad_joke")])])

    text = format_diff(diff_system_cards(old, new))

    assert "+ added tool: dad_joke" in text


def test_format_diff_is_empty_for_an_unchanged_card() -> None:
    card = SystemCard(agents=[_agent()])

    text = format_diff(diff_system_cards(card, card))

    assert text == ""
