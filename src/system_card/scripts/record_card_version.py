"""CLI: compares the current system card to the latest recorded version.

Used by .github/workflows/system-card-diff.yml. Two modes:

- `--dry-run` (pull requests): prints the diff against the latest recorded
  version, writes nothing. Exit code 0 always.
- default (push to main): if the hash changed, writes the next
  `card-versions/vN.json` and prints the diff. If unchanged, writes nothing.

Either way, when there's a change, the rendered diff is written to
GITHUB_OUTPUT (if set) under the key `diff`, and the new version label
under `version`, so the workflow can use them in a PR comment or commit
message without re-parsing stdout.
"""

import io
import json
import os
import re
import sys
from pathlib import Path

import structlog

from system_card.agents import system_card_agent
from system_card.registry.agent_registry import AgentRegistry
from system_card.registry.default_agents import register_default_agents
from system_card.registry.default_tools import register_default_tools
from system_card.registry.tool_registry import ToolRegistry
from system_card.schemas.model_config import ModelConfig, ModelProvider
from system_card.schemas.system_card import SystemCard
from system_card.services.system_card_diff_service import diff_system_cards, format_diff
from system_card.services.system_card_service import build_system_card, hash_system_card

logger = structlog.get_logger(__name__)

CARD_VERSIONS_DIR = Path("card-versions")
VERSION_FILE_PATTERN = re.compile(r"^v(\d+)\.json$")


def _build_current_card() -> SystemCard:
    """Builds the card from the pinned model digest declared in source.

    Deliberately does not call verify_model_digest(): that check needs a
    live local Ollama server, which CI doesn't have. The card hash reflects
    what's pinned in source — the actual source of truth for "what we
    believe the config is" — not a live runtime check, which is a separate,
    local-only concern for when the agent actually runs.
    """
    tool_registry = ToolRegistry()
    register_default_tools(tool_registry)

    model = ModelConfig(
        provider=ModelProvider.OLLAMA,
        model_name=system_card_agent.PINNED_MODEL_TAG,
        model_digest=system_card_agent.PINNED_MODEL_DIGEST,
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

    return build_system_card(agent_registry, tool_registry)


def _latest_version_number(versions_dir: Path) -> int:
    if not versions_dir.exists():
        return 0

    numbers = [
        int(match.group(1))
        for path in versions_dir.iterdir()
        if (match := VERSION_FILE_PATTERN.match(path.name))
    ]

    return max(numbers, default=0)


def _load_card(version_path: Path) -> SystemCard:
    payload = json.loads(version_path.read_text(encoding="utf-8"))
    return SystemCard.model_validate(payload["card"])


def _write_github_output(name: str, value: str) -> None:
    output_path = os.environ.get("GITHUB_OUTPUT")
    if output_path is None:
        return

    delimiter = "EOF_SYSTEM_CARD_DIFF"
    with Path(output_path).open("a", encoding="utf-8") as f:
        f.write(f"{name}<<{delimiter}\n{value}\n{delimiter}\n")


def _main(dry_run: bool) -> None:
    current_card = _build_current_card()
    current_hash = hash_system_card(current_card)

    latest_number = _latest_version_number(CARD_VERSIONS_DIR)

    if latest_number == 0:
        diff_text = format_diff(diff_system_cards(SystemCard(agents=[]), current_card))
        next_version = "v1"
    else:
        latest_path = CARD_VERSIONS_DIR / f"v{latest_number}.json"
        latest_payload = json.loads(latest_path.read_text(encoding="utf-8"))

        if latest_payload["hash"] == current_hash:
            logger.info("record_card_version.unchanged", version=f"v{latest_number}")
            return

        diff_text = format_diff(diff_system_cards(_load_card(latest_path), current_card))
        next_version = f"v{latest_number + 1}"

    logger.info("record_card_version.changed", version=next_version, diff=diff_text)
    _write_github_output("diff", diff_text)
    _write_github_output("version", next_version)

    if dry_run:
        return

    CARD_VERSIONS_DIR.mkdir(parents=True, exist_ok=True)
    version_path = CARD_VERSIONS_DIR / f"{next_version}.json"
    version_path.write_text(
        json.dumps(
            {"version": next_version, "hash": current_hash, "card": current_card.model_dump()},
            indent=2,
        ),
        encoding="utf-8",
    )
    logger.info("record_card_version.written", path=str(version_path))


if __name__ == "__main__":
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8")

    _main(dry_run="--dry-run" in sys.argv)
