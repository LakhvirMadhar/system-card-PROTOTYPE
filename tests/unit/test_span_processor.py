"""Unit tests for the custom system-card-hash span processor."""

from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from system_card.core.attributes import AgentAttributes
from system_card.observability.span_processor import SystemCardSpanProcessor


def _provider_with_card_hash(system_card_hash: str) -> tuple[TracerProvider, InMemorySpanExporter]:
    provider = TracerProvider()
    exporter = InMemorySpanExporter()
    provider.add_span_processor(SystemCardSpanProcessor(system_card_hash))
    provider.add_span_processor(SimpleSpanProcessor(exporter))

    return provider, exporter


def test_every_span_is_tagged_with_the_system_card_hash() -> None:
    provider, exporter = _provider_with_card_hash("abc123")
    tracer = provider.get_tracer(__name__)

    with tracer.start_as_current_span("a-span"):
        pass

    (exported_span,) = exporter.get_finished_spans()
    assert exported_span.attributes is not None
    assert exported_span.attributes[AgentAttributes.SYSTEM_CARD_HASH] == "abc123"


def test_nested_spans_all_get_tagged() -> None:
    provider, exporter = _provider_with_card_hash("abc123")
    tracer = provider.get_tracer(__name__)

    with tracer.start_as_current_span("outer"):
        with tracer.start_as_current_span("inner"):
            pass

    exported_spans = exporter.get_finished_spans()
    assert len(exported_spans) == 2
    for span in exported_spans:
        assert span.attributes is not None
        assert span.attributes[AgentAttributes.SYSTEM_CARD_HASH] == "abc123"


def test_different_processor_instances_tag_with_their_own_hash() -> None:
    provider_one, exporter_one = _provider_with_card_hash("hash-one")
    provider_two, exporter_two = _provider_with_card_hash("hash-two")

    with provider_one.get_tracer(__name__).start_as_current_span("span"):
        pass
    with provider_two.get_tracer(__name__).start_as_current_span("span"):
        pass

    (span_one,) = exporter_one.get_finished_spans()
    (span_two,) = exporter_two.get_finished_spans()
    assert span_one.attributes is not None
    assert span_two.attributes is not None
    assert span_one.attributes[AgentAttributes.SYSTEM_CARD_HASH] == "hash-one"
    assert span_two.attributes[AgentAttributes.SYSTEM_CARD_HASH] == "hash-two"
