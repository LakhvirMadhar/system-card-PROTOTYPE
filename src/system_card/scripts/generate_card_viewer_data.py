"""CLI: builds the real system card and writes it as JSON for viewer/index.html.

viewer/script.js loads this via fetch(). That only fails under file://
(browsers block fetch() against local files); serving viewer/ through any
HTTP server — a local one during development, or GitHub Pages once
deployed — works with no special-casing.
"""

import io
import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

import structlog

from system_card.adapters.ollama_digest import verify_model_digest
from system_card.agents import system_card_agent
from system_card.core.config import Settings
from system_card.registry.agent_registry import AgentRegistry
from system_card.registry.default_agents import register_default_agents
from system_card.registry.default_tools import register_default_tools
from system_card.registry.tool_registry import ToolRegistry
from system_card.schemas.model_config import ModelConfig, ModelProvider
from system_card.schemas.system_card import SystemCard
from system_card.services.system_card_diff_service import diff_system_cards, format_diff
from system_card.services.system_card_service import build_system_card, hash_system_card

logger = structlog.get_logger(__name__)

DEFAULT_OUTPUT_PATH = Path("viewer/system_card_data.json")
CARD_VERSIONS_DIR = Path("card-versions")
VERSION_FILE_PATTERN = re.compile(r"^v(\d+)\.json$")


def _build_version_history(versions_dir: Path) -> list[dict[str, object]]:
    """Reads every recorded card-versions/vN.json and diffs each against its predecessor.

    Args:
        versions_dir: The card-versions/ directory.

    Returns:
        One entry per recorded version, oldest first, each carrying its own
        version label, hash, generated_at, and the diff against the version
        immediately before it (against an empty card, for the first version).
    """
    if not versions_dir.exists():
        return []

    numbered_paths = sorted(
        (
            (int(match.group(1)), path)
            for path in versions_dir.iterdir()
            if (match := VERSION_FILE_PATTERN.match(path.name))
        ),
        key=lambda pair: pair[0],
    )

    history: list[dict[str, object]] = []
    previous_card = SystemCard(agents=[])

    for _, path in numbered_paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        current_card = SystemCard.model_validate(payload["card"])
        diff = diff_system_cards(previous_card, current_card)

        history.append(
            {
                "version": payload["version"],
                "hash": payload["hash"],
                "diff": format_diff(diff),
                "agent_diffs": diff.model_dump()["agent_diffs"],
            }
        )
        previous_card = current_card

    return history


def _main(output_path: Path) -> None:
    settings = Settings()

    tool_registry = ToolRegistry()
    register_default_tools(tool_registry)

    model = ModelConfig(
        provider=ModelProvider.OLLAMA,
        model_name=system_card_agent.PINNED_MODEL_TAG,
        model_digest=verify_model_digest(
            system_card_agent.PINNED_MODEL_TAG,
            settings.ollama_api_base,
            system_card_agent.PINNED_MODEL_DIGEST,
        ),
        temperature=0.7,
        top_p=1.0,
        top_k=64,
        seed=None,
        presence_penalty=None,
        frequency_penalty=None,
        stop_sequences=None,
        max_output_tokens=None,
    )

    agent_registry = AgentRegistry()
    register_default_agents(agent_registry, model)

    card = build_system_card(agent_registry, tool_registry)
    card_hash = hash_system_card(card)
    agents = card.model_dump()["agents"]

    tools = []
    for tool in sorted(tool_registry.list_tools(), key=lambda entry: entry.name):
        used_by = sorted(
            agent["name"] for agent in agents if tool.name in {t["name"] for t in agent["tools"]}
        )
        tools.append({**tool.model_dump(), "used_by": used_by})

    payload = {
        "hash": card_hash,
        "generated_at": datetime.now(UTC).isoformat(),
        "agents": agents,
        "tools": tools,
        "history": _build_version_history(CARD_VERSIONS_DIR),
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    logger.info("card_viewer_data.written", output_path=str(output_path), card_hash=card_hash)


if __name__ == "__main__":
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8")

    _main(DEFAULT_OUTPUT_PATH)
