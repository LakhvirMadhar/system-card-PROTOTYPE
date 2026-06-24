"""CLI: runs the agent with the custom span processor, tagging every span with the card hash.

This is the "after" (Build Order step 6) — same agent, same console exporter
as scripts/inspect_otel_baseline.py, but every span now also carries
agent.system_card_hash. Run both scripts back to back and diff the printed
span attributes to see the actual difference.
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
from system_card.observability.span_processor import SystemCardSpanProcessor
from system_card.services.agent_service import AgentService, build_agent_from_spec
from system_card.services.system_card_service import build_system_card, hash_system_card

logger = structlog.get_logger(__name__)


def _configure_tracing_with_card_hash(system_card_hash: str) -> None:
    provider = TracerProvider()
    provider.add_span_processor(SystemCardSpanProcessor(system_card_hash))
    provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
    trace.set_tracer_provider(provider)


async def _main(message: str) -> None:
    settings = Settings()
    model = build_pinned_model(settings)
    registries = build_registries(model)

    card = build_system_card(registries.agents, registries.tools, registries.guardrails)
    card_hash = hash_system_card(card)
    _configure_tracing_with_card_hash(card_hash)

    agent = build_agent_from_spec(
        registries.agents.get(system_card_agent.NAME), registries.tools, settings.ollama_api_base
    )
    service = AgentService(agent)

    reply = await service.run(message)

    logger.info("agent.reply", message=message, reply=reply, system_card_hash=card_hash)


if __name__ == "__main__":
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8")

    user_message = sys.argv[1] if len(sys.argv) > 1 else "Flip a coin for me."
    asyncio.run(_main(user_message))
