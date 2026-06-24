"""Shared git-tag-based card history helpers.

Used by both record_card_version.py (decides whether to mint the next
version) and generate_card_viewer_data.py (walks every recorded version
for the viewer's Versions tabs). Kept here rather than in adapters/,
which is restricted to importing only core/models — this needs SystemCard
from schemas/, and scripts/ is architecturally unconstrained.
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from system_card.schemas.system_card import SystemCard

TAG_PREFIX = "card-v"


def list_card_tags() -> list[tuple[int, str]]:
    """Returns every card-vN tag as (version number, tag name), sorted ascending.

    Returns:
        One entry per recorded version, oldest first. Empty if none exist.
    """
    result = subprocess.run(
        ["git", "tag", "--list", f"{TAG_PREFIX}*"],
        capture_output=True,
        text=True,
        check=True,
    )

    numbered_tags = []
    for tag in result.stdout.splitlines():
        suffix = tag.removeprefix(TAG_PREFIX)
        if suffix.isdigit():
            numbered_tags.append((int(suffix), tag))

    return sorted(numbered_tags, key=lambda pair: pair[0])


def latest_card_tag() -> tuple[int, str] | None:
    """Returns the highest-numbered card-vN tag, or None if none exist yet."""
    tags = list_card_tags()
    return tags[-1] if tags else None


def commit_sha_for_tag(tag: str) -> str:
    """Resolves a tag to the full commit SHA it points at.

    Args:
        tag: The git tag to resolve.

    Returns:
        The full 40-character commit SHA.
    """
    result = subprocess.run(
        ["git", "rev-list", "-n", "1", tag],
        capture_output=True,
        text=True,
        check=True,
    )

    return result.stdout.strip()


def card_at_tag(tag: str) -> SystemCard:
    """Computes the system card exactly as it existed at the given git tag.

    Checks the tag out into a temporary worktree and re-runs
    record_card_version.py --print-card-json there, with PYTHONPATH pointed
    at that worktree's own src/ — not poetry's editable install of the
    current checkout — so the result reflects that version's actual code,
    not today's. Loading an old JSON snapshot against today's Pydantic
    model is exactly what kept breaking every time a field was added;
    re-running the matching code at that revision can't have that problem.

    Args:
        tag: The card-vN tag to compute the historical card for.

    Returns:
        The SystemCard as it existed at that tag.
    """
    with tempfile.TemporaryDirectory() as worktree_dir:
        subprocess.run(
            ["git", "worktree", "add", "--detach", worktree_dir, tag],
            check=True,
            capture_output=True,
        )
        try:
            worktree_src = str(Path(worktree_dir) / "src")
            env = os.environ.copy()
            env["PYTHONPATH"] = worktree_src + os.pathsep + env.get("PYTHONPATH", "")

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "system_card.scripts.record_card_version",
                    "--print-card-json",
                ],
                cwd=worktree_dir,
                env=env,
                capture_output=True,
                text=True,
                check=True,
            )
        finally:
            subprocess.run(
                ["git", "worktree", "remove", "--force", worktree_dir],
                check=True,
                capture_output=True,
            )

    return SystemCard.model_validate(json.loads(result.stdout))
