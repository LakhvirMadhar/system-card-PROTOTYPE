"""CLI: builds the system card from the registered agents and tools, prints it with its hash."""

import io
import sys

from system_card.core.config import Settings
from system_card.dependencies.registries import build_pinned_model, build_registries
from system_card.services.system_card_service import build_system_card, hash_system_card


def _main() -> None:
    settings = Settings()
    model = build_pinned_model(settings)
    registries = build_registries(model)

    card = build_system_card(registries.agents, registries.tools, registries.guardrails)
    card_hash = hash_system_card(card)

    print(card.model_dump_json(indent=2))
    print()
    print(f"system_card_hash = {card_hash}")


if __name__ == "__main__":
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8")

    _main()
