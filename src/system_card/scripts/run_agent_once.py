"""CLI smoke test: sends one message to the agent and prints its reply."""

import asyncio
import io
import sys

import structlog

from system_card.adapters.ollama_digest import verify_model_digest
from system_card.core.config import Settings
from system_card.schemas.model_config import ModelConfig, ModelProvider
from system_card.services.agent_service import AgentService, build_agent

logger = structlog.get_logger(__name__)

PINNED_MODEL_TAG = "gemma4:latest"
PINNED_MODEL_DIGEST = "c6eb396dbd5992bbe3f5cdb947e8bbc0ee413d7c17e2beaae69f5d569cf982eb"


async def _main(message: str) -> None:
    settings = Settings()
    model = ModelConfig(
        provider=ModelProvider.OLLAMA,
        model_name=PINNED_MODEL_TAG,
        model_digest=verify_model_digest(
            PINNED_MODEL_TAG, settings.ollama_api_base, PINNED_MODEL_DIGEST
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

    agent = build_agent(model, settings.ollama_api_base)
    service = AgentService(agent)

    reply = await service.run(message)

    logger.info("agent.reply", message=message, reply=reply)


if __name__ == "__main__":
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8")

    user_message = sys.argv[1] if len(sys.argv) > 1 else "Flip a coin for me."
    asyncio.run(_main(user_message))
