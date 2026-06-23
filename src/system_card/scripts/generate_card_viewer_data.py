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

from system_card.adapters.ollama_digest import verify_model_digest
from system_card.agents import system_card_agent
from system_card.core.config import Settings
from system_card.registry.agent_registry import AgentRegistry
from system_card.registry.default_agents import register_default_agents
from system_card.registry.default_tools import register_default_tools
from system_card.registry.tool_registry import ToolRegistry
from system_card.schemas.model_config import ModelConfig, ModelProvider
from system_card.services.system_card_service import build_system_card, hash_system_card

logger = structlog.get_logger(__name__)

DEFAULT_OUTPUT_PATH = Path("viewer/system_card_data.json")


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
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    logger.info("card_viewer_data.written", output_path=str(output_path), card_hash=card_hash)


if __name__ == "__main__":
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8")

    _main(DEFAULT_OUTPUT_PATH)
