"""CLI: runs the agent with a plain console span exporter to show ADK's native OTel output.

No custom span processor here — this is the "before" baseline (Build Order
step 5) that the custom processor (step 6) gets compared against.
"""

import asyncio
import io
import sys

import structlog
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

from system_card.adapters.ollama_digest import verify_model_digest
from system_card.agents import system_card_agent
from system_card.core.config import Settings
from system_card.registry.agent_registry import AgentRegistry
from system_card.registry.default_agents import register_default_agents
from system_card.registry.default_tools import register_default_tools
from system_card.registry.tool_registry import ToolRegistry
from system_card.schemas.model_config import ModelConfig, ModelProvider
from system_card.services.agent_service import AgentService, build_agent_from_spec

logger = structlog.get_logger(__name__)


def _configure_console_tracing() -> None:
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
    trace.set_tracer_provider(provider)


async def _main(message: str) -> None:
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

    agent = build_agent_from_spec(
        agent_registry.get(system_card_agent.NAME), tool_registry, settings.ollama_api_base
    )
    service = AgentService(agent)

    reply = await service.run(message)

    logger.info("agent.reply", message=message, reply=reply)


if __name__ == "__main__":
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8")

    _configure_console_tracing()

    user_message = sys.argv[1] if len(sys.argv) > 1 else "Flip a coin for me."
    asyncio.run(_main(user_message))
