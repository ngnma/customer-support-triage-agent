#!/usr/bin/env python
import sys
from pydantic import BaseModel
from crewai.flow import Flow, listen, start
from support_triage.schemas import Ticket
from support_triage.utils import parse_ticket, TicketParseError
import argparse


# logging setup
import logging
logger = logging.getLogger(__name__)    # one per file, at the top


class TicketState(BaseModel):
    ticket: Ticket | None = None
    category: str = ""
    ticket_path: str = ""


class SupportTriageFlow(Flow[TicketState]):

    @start()
    def load_ticket(self):
        """Entry point for the flow"""
        ticket = parse_ticket(self.state.ticket_path)
        self.state.ticket = ticket
        logger.info("Ticket loaded from user input. Ticket ID: %s", ticket.ticket_id)



def kickoff() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    parser = argparse.ArgumentParser(description="Run the support triage flow on one ticket.")
    parser.add_argument("ticket_path", help="Path to the ticket JSON file")
    args = parser.parse_args()

    support_flow = SupportTriageFlow()
    try:
        support_flow.kickoff(inputs={"ticket_path": args.ticket_path})
    except TicketParseError as e:
        logger.error("Invalid ticket: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    kickoff()
