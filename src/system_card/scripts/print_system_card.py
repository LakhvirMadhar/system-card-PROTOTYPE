"""CLI: builds the system card from the registered tools and model, prints it with its hash."""

import io
import sys

from system_card.adapters.ollama_digest import verify_model_digest
from system_card.core.config import Settings
from system_card.registry.default_tools import register_default_tools
from system_card.registry.tool_registry import ToolRegistry
from system_card.schemas.model_config import ModelConfig
from system_card.services.system_card_service import build_system_card, hash_system_card

PINNED_MODEL_TAG = "gemma4:latest"
PINNED_MODEL_DIGEST = "c6eb396dbd5992bbe3f5cdb947e8bbc0ee413d7c17e2beaae69f5d569cf982eb"


def _main() -> None:
    settings = Settings()

    registry = ToolRegistry()
    register_default_tools(registry)

    model = ModelConfig(
        provider="ollama",
        model_name=PINNED_MODEL_TAG,
        model_digest=verify_model_digest(
            PINNED_MODEL_TAG, settings.ollama_api_base, PINNED_MODEL_DIGEST
        ),
        temperature=0.7,
        top_p=1.0,
        max_output_tokens=None,
    )

    card = build_system_card(registry, model)
    card_hash = hash_system_card(card)

    print(card.model_dump_json(indent=2))
    print()
    print(f"system_card_hash = {card_hash}")


if __name__ == "__main__":
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8")

    _main()
