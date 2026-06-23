"""Custom span processor that stamps every span with the active system card hash."""

from opentelemetry.context import Context
from opentelemetry.sdk.trace import ReadableSpan, Span, SpanProcessor

from system_card.core.attributes import AgentAttributes


class SystemCardSpanProcessor(SpanProcessor):
    """Tags every span with the system card hash active when it starts.

    Stamping happens in on_start rather than on_end: on_start receives the
    live, mutable Span (set_attribute works); on_end receives a ReadableSpan
    meant for export, not mutation.
    """

    def __init__(self, system_card_hash: str) -> None:
        """Stores the hash to stamp onto every span.

        Args:
            system_card_hash: The hash of the system card active for this run.
        """
        self._system_card_hash = system_card_hash

    def on_start(self, span: Span, parent_context: Context | None = None) -> None:
        """Stamps the system card hash onto a span as it starts.

        Args:
            span: The span being started.
            parent_context: The parent context, if any.
        """
        span.set_attribute(AgentAttributes.SYSTEM_CARD_HASH, self._system_card_hash)

    def on_end(self, span: ReadableSpan) -> None:
        """No-op — attributes are stamped in on_start, before export.

        Args:
            span: The span that just ended.
        """

    def shutdown(self) -> None:
        """No-op — this processor holds no resources to release."""

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        """No-op — nothing to flush.

        Args:
            timeout_millis: Unused.

        Returns:
            Always True, since there is nothing to flush.
        """
        return True
