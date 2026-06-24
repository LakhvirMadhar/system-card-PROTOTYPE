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

from system_card.agents import system_card_agent
from system_card.core.config import Settings
from system_card.dependencies.registries import build_pinned_model, build_registries
from system_card.services.agent_service import AgentService, build_agent_from_spec

logger = structlog.get_logger(__name__)


def _configure_console_tracing() -> None:
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
    trace.set_tracer_provider(provider)


async def _main(message: str) -> None:
    settings = Settings()
    model = build_pinned_model(settings)
    registries = build_registries(model)

    agent = build_agent_from_spec(
        registries.agents.get(system_card_agent.NAME), registries.tools, settings.ollama_api_base
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
