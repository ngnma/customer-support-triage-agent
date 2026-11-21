from pydantic import BaseModel, Field
from typing import Literal

class Ticket(BaseModel):
    ticket_id: str
    content: str

class TicketResolution(BaseModel):
    """Decision made by the support crew for an investigated ticket."""

    category: Literal[
        "late_delivery",
        "damaged_item",
        "wrong_item",
        "missing_item",
        "billing_issue",
        "return_request",
        "other",
    ] = Field(description="The type of problem the customer reported.")
    refund_eligible: bool = Field(
        description="True if the refund policy allows a refund for this case."
    )
    actions: list[str] = Field(
        min_length=1,
        description="Concrete next steps to resolve the ticket, e.g. 'Reship order 48213'.",
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="How confident you are in this decision, from 0.0 to 1.0.",
    )
    

