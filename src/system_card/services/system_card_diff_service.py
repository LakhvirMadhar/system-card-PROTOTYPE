"""Diffs two system card versions and renders the diff as human-readable text."""

from system_card.schemas.agent_manifest import AgentManifestEntry
from system_card.schemas.system_card import SystemCard
from system_card.schemas.system_card_diff import AgentDiff, SystemCardDiff, ToolDiff


def _diff_tools(old: AgentManifestEntry, new: AgentManifestEntry) -> list[ToolDiff]:
    old_tools = {tool.name: tool for tool in old.tools}
    new_tools = {tool.name: tool for tool in new.tools}

    diffs = [ToolDiff(name=name, change="added") for name in new_tools if name not in old_tools]
    diffs += [ToolDiff(name=name, change="removed") for name in old_tools if name not in new_tools]
    diffs += [
        ToolDiff(name=name, change="changed")
        for name in old_tools.keys() & new_tools.keys()
        if old_tools[name] != new_tools[name]
    ]

    return diffs


def _diff_agent(old: AgentManifestEntry, new: AgentManifestEntry) -> AgentDiff | None:
    tool_diffs = _diff_tools(old, new)
    instruction_changed = old.instruction != new.instruction
    model_changed = old.model != new.model

    if not tool_diffs and not instruction_changed and not model_changed:
        return None

    return AgentDiff(
        name=new.name,
        change="changed",
        tool_diffs=tool_diffs,
        instruction_changed=instruction_changed,
        model_changed=model_changed,
    )


def diff_system_cards(old: SystemCard, new: SystemCard) -> SystemCardDiff:
    """Computes every agent-level change between two system card versions.

    Args:
        old: The previously recorded card version.
        new: The current card version.

    Returns:
        A SystemCardDiff listing every added, removed, or changed agent.
        Agents identical between old and new produce no entry.
    """
    old_agents = {agent.name: agent for agent in old.agents}
    new_agents = {agent.name: agent for agent in new.agents}

    agent_diffs = [
        AgentDiff(name=name, change="added") for name in new_agents if name not in old_agents
    ]
    agent_diffs += [
        AgentDiff(name=name, change="removed") for name in old_agents if name not in new_agents
    ]

    for name in old_agents.keys() & new_agents.keys():
        changed = _diff_agent(old_agents[name], new_agents[name])
        if changed is not None:
            agent_diffs.append(changed)

    return SystemCardDiff(agent_diffs=agent_diffs)


def format_diff(diff: SystemCardDiff) -> str:
    """Renders a SystemCardDiff as a human-readable bullet list.

    Args:
        diff: The diff to render.

    Returns:
        Markdown-friendly text, one line per change. Empty string if
        diff.is_empty().
    """
    lines: list[str] = []

    for agent_diff in diff.agent_diffs:
        if agent_diff.change == "added":
            lines.append(f"+ added agent: {agent_diff.name}")
            continue
        if agent_diff.change == "removed":
            lines.append(f"- removed agent: {agent_diff.name}")
            continue

        lines.append(f"~ changed agent: {agent_diff.name}")
        for tool_diff in agent_diff.tool_diffs:
            symbol = {"added": "+", "removed": "-", "changed": "~"}[tool_diff.change]
            lines.append(f"  {symbol} {tool_diff.change} tool: {tool_diff.name}")
        if agent_diff.instruction_changed:
            lines.append("  ~ changed: system instruction")
        if agent_diff.model_changed:
            lines.append("  ~ changed: model config")

    return "\n".join(lines)
