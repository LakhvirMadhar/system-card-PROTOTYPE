"""CLI smoke test: sends one message to the agent and prints its reply."""

import asyncio
import io
import sys

import structlog

from system_card.core.config import Settings
from system_card.schemas.model_config import ModelConfig
from system_card.services.agent_service import AgentService, build_agent

logger = structlog.get_logger(__name__)


async def _main(message: str) -> None:
    settings = Settings()
    model = ModelConfig(
        provider="ollama",
        model_name="gemma4:latest",
        temperature=0.7,
        top_p=1.0,
        max_output_tokens=None,
    )

    agent = build_agent(model, settings.ollama_api_base)
    service = AgentService(agent)

    reply = await service.run(message)

    logger.info("agent.reply", message=message, reply=reply)


if __name__ == "__main__":
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8")

    user_message = sys.argv[1] if len(sys.argv) > 1 else "Flip a coin for me."
    asyncio.run(_main(user_message))
