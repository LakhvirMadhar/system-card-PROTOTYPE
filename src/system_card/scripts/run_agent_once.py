"""CLI smoke test: sends one message to the agent and prints its reply."""

import asyncio
import io
import sys

import structlog

from system_card.agents import system_card_agent
from system_card.core.config import Settings
from system_card.dependencies.registries import build_pinned_model, build_registries
from system_card.services.agent_service import AgentService, build_agent_from_spec

logger = structlog.get_logger(__name__)


async def _main(message: str, agent_name: str) -> None:
    settings = Settings()
    model = build_pinned_model(settings)
    registries = build_registries(model)

    spec = registries.agents.get(agent_name)
    guardrails = [registries.guardrails.get(name) for name in spec.guardrail_names]
    agent = build_agent_from_spec(spec, registries.tools, settings.ollama_api_base, guardrails)
    service = AgentService(agent)

    reply = await service.run(message)

    logger.info("agent.reply", agent=agent_name, message=message, reply=reply)


if __name__ == "__main__":
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8")

    user_message = sys.argv[1] if len(sys.argv) > 1 else "Flip a coin for me."
    target_agent = sys.argv[2] if len(sys.argv) > 2 else system_card_agent.NAME
    asyncio.run(_main(user_message, target_agent))
