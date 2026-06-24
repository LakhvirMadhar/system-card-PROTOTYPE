"""CLI: compares the current system card to the most recent card-vN git tag.

Used by .github/workflows/system-card-diff.yml. Two modes:

- `--print-card-json`: prints only the current card's JSON to stdout, no
  diffing. Used internally by _git_card_history.card_at_tag(), which
  re-runs this same script inside a temporary worktree checked out at an
  old tag, so that version's card is computed by that version's own code
  against its own schema.
- default: compares the current card to the most recent card-vN tag (if
  any). `--dry-run` (pull requests) stops after computing the diff, writes
  nothing. Without it (push to main), creates the next card-v{N} tag on
  HEAD if the hash changed.

Either way, when there's a change, the rendered diff is written to
GITHUB_OUTPUT (if set) under the key `diff`, and the new version label
under `version`, so the workflow can use them in a PR comment or push the
new tag without re-parsing stdout.
"""

import io
import os
import subprocess
import sys
from pathlib import Path

import structlog

from system_card.dependencies.registries import build_pinned_model_from_source, build_registries
from system_card.schemas.system_card import SystemCard
from system_card.scripts._git_card_history import TAG_PREFIX, card_at_tag, latest_card_tag
from system_card.services.system_card_diff_service import diff_system_cards, format_diff
from system_card.services.system_card_service import build_system_card, hash_system_card

logger = structlog.get_logger(__name__)


def _build_current_card() -> SystemCard:
    """Builds the card from the pinned model digest declared in source.

    Deliberately does not call verify_model_digest(): that check needs a
    live local Ollama server, which CI doesn't have. The card hash reflects
    what's pinned in source — the actual source of truth for "what we
    believe the config is" — not a live runtime check, which is a separate,
    local-only concern for when the agent actually runs.
    """
    model = build_pinned_model_from_source()
    registries = build_registries(model)

    return build_system_card(registries.agents, registries.tools, registries.guardrails)


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

    latest = latest_card_tag()

    if latest is None:
        previous_card = SystemCard(agents=[])
        next_version_number = 1
    else:
        latest_number, latest_tag = latest
        previous_card = card_at_tag(latest_tag)

        if hash_system_card(previous_card) == current_hash:
            logger.info("record_card_version.unchanged", version=f"{TAG_PREFIX}{latest_number}")
            return

        next_version_number = latest_number + 1

    next_version = f"{TAG_PREFIX}{next_version_number}"
    diff_text = format_diff(diff_system_cards(previous_card, current_card))

    logger.info("record_card_version.changed", version=next_version, diff=diff_text)
    _write_github_output("diff", diff_text)
    _write_github_output("version", next_version)

    if dry_run:
        return

    subprocess.run(["git", "tag", next_version], check=True)
    logger.info("record_card_version.tagged", tag=next_version)


if __name__ == "__main__":
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8")

    if "--print-card-json" in sys.argv:
        print(_build_current_card().model_dump_json())
    else:
        _main(dry_run="--dry-run" in sys.argv)
