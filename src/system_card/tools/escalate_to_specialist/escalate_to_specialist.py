"""Escalates a case to a human specialist."""

import uuid

from system_card.tools.escalate_to_specialist.types import EscalationTicket


def escalate_to_specialist(reason: str) -> EscalationTicket:
    """Escalates the current case to a human specialist.

    Args:
        reason: Why this case is being escalated rather than handled by the
            agent directly.

    Returns:
        A ticket confirming the escalation, with a generated ticket ID.
    """
    return EscalationTicket(ticket_id=f"esc-{uuid.uuid4().hex[:8]}", reason=reason)
