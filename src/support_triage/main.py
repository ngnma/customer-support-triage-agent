#!/usr/bin/env python
import sys
from pydantic import BaseModel
from crewai.flow import Flow, listen, start, persist
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
    status: str = "new"

@persist()
class SupportTriageFlow(Flow[TicketState]):

    @start()
    def load_ticket(self):
        """Entry point for the flow"""
        print("Ticket UUID:", self.state.id)
        if self.state.status == "new":
            print("This is a new ticket. Loading ticket from user input.")
            self.state.ticket = parse_ticket(self.state.ticket_path)
            self.state.status = "open"
            logger.info("Ticket loaded from user input. Ticket number: %s", self.state.ticket.ticket_number)
            logger.info("Ticket loaded from user input. Ticket content: %s", self.state.ticket.content) # TODO: Remove this line in PII protection phase, as it may contain sensitive information
        elif self.state.status == "open":
            print("This is an open ticket. Loading ticket from memory.")
            logger.info("Ticket loaded from memory. Ticket number: %s", self.state.ticket.ticket_number)
            logger.info("Ticket loaded from memory. Ticket content: %s", self.state.ticket.content) # TODO: Remove this line in PII protection phase, as it may contain sensitive information



def kickoff() -> None:
    # logging setup
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    # Input from command line arguments
    parser = argparse.ArgumentParser(description="Run the support triage flow on one ticket.")
    parser.add_argument("ticket_path", help="Path to the ticket JSON file")
    args = parser.parse_args()

    # Initialize the flow with the input arguments
    support_flow = SupportTriageFlow()
    try:
        support_flow.kickoff(
            inputs={
                "ticket_path": args.ticket_path
                , "id": "accfd40e-6435-4759-9ec8-b998cb373e75" # Tip: It updates the state of the flow with the given ID, if it exists.
            }
            #, restore_from_state_id='accfd40e-6435-4759-9ec8-b998cb373e75' # Tip: It forks the existing flow's state from the given ID, and creates a new flow with a new ID. This keep records of all changes.
            )
    except TicketParseError as e:
        logger.error("Invalid ticket: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    kickoff()
