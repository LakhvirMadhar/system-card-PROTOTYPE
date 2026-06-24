"""Types for the escalate_to_specialist tool."""

from pydantic import BaseModel


class EscalationTicket(BaseModel):
    """A fixed-format confirmation that a case was escalated.

    Attributes:
        ticket_id: A generated identifier for the escalation.
        reason: The reason the case was escalated, as given by the caller.
    """

    ticket_id: str
    reason: str
