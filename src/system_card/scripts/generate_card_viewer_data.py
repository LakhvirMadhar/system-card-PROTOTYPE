"""CLI: builds the real system card and writes it as JSON for viewer/index.html.

viewer/script.js loads this via fetch(). That only fails under file://
(browsers block fetch() against local files); serving viewer/ through any
HTTP server — a local one during development, or GitHub Pages once
deployed — works with no special-casing.
"""

import io
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import structlog

from system_card.core.config import Settings
from system_card.dependencies.registries import build_pinned_model, build_registries
from system_card.schemas.system_card import SystemCard
from system_card.scripts._git_card_history import card_at_tag, commit_sha_for_tag, list_card_tags
from system_card.services.system_card_diff_service import diff_system_cards, format_diff
from system_card.services.system_card_service import build_system_card, hash_system_card

logger = structlog.get_logger(__name__)

DEFAULT_OUTPUT_PATH = Path("viewer/system_card_data.json")


def _build_version_history() -> list[dict[str, object]]:
    """Walks every recorded card-vN git tag and diffs each against its predecessor.

    Returns:
        One entry per recorded version, oldest first, each carrying its own
        version label, hash, and the diff against the version immediately
        before it (against an empty card, for the first version).
    """
    history: list[dict[str, object]] = []
    previous_card = SystemCard(agents=[])

    for _, tag in list_card_tags():
        current_card = card_at_tag(tag)
        diff = diff_system_cards(previous_card, current_card)

        history.append(
            {
                "version": tag,
                "commit": commit_sha_for_tag(tag),
                "hash": hash_system_card(current_card),
                "diff": format_diff(diff),
                "agent_diffs": diff.model_dump()["agent_diffs"],
            }
        )
        previous_card = current_card

    return history


def _main(output_path: Path) -> None:
    settings = Settings()
    model = build_pinned_model(settings)
    registries = build_registries(model)

    card = build_system_card(registries.agents, registries.tools, registries.guardrails)
    card_hash = hash_system_card(card)
    agents = card.model_dump()["agents"]

    tools = []
    for tool in sorted(registries.tools.list_tools(), key=lambda entry: entry.name):
        used_by = sorted(
            agent["name"] for agent in agents if tool.name in {t["name"] for t in agent["tools"]}
        )
        tools.append({**tool.model_dump(), "used_by": used_by})

    payload = {
        "hash": card_hash,
        "generated_at": datetime.now(UTC).isoformat(),
        "repo_url": settings.repo_url,
        "agents": agents,
        "tools": tools,
        "history": _build_version_history(),
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    logger.info("card_viewer_data.written", output_path=str(output_path), card_hash=card_hash)


if __name__ == "__main__":
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8")

    _main(DEFAULT_OUTPUT_PATH)
