"""Escalates a case to a human specialist."""

from system_card.tools.escalate_to_specialist.escalate_to_specialist import (
    escalate_to_specialist,
)
from system_card.tools.escalate_to_specialist.types import EscalationTicket

__all__ = ["EscalationTicket", "escalate_to_specialist"]
