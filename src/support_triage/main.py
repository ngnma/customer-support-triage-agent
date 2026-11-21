#!/usr/bin/env python
import sys
from pydantic import BaseModel
import argparse

from crewai import LLM
from crewai.flow import Flow, listen, start, persist, router, or_

from support_triage.schemas import Ticket
from support_triage.utils import parse_ticket, TicketParseError
from support_triage.prompts import ROUTER_PROMPT





# logging setup
import logging
logger = logging.getLogger(__name__)    # one per file, at the top


class TicketState(BaseModel):
    ticket: Ticket | None = None
    category: str = ""
    ticket_path: str = ""
    status: str = "new"
    reply: str = ""

@persist()
class SupportTriageFlow(Flow[TicketState]):

    @start()
    def load_ticket(self):
        """Entry point for the flow. Loading the ticket from memory or user input"""
        print("Ticket UUID:", self.state.id)
        if self.state.status == "new":
            print("This is a new ticket. Loading ticket from user input.")
            self.state.ticket = parse_ticket(self.state.ticket_path)
            self.state.status = "open"
            logger.info("Ticket loaded from user input. Ticket ID: %s", self.state.ticket.ticket_id)
            logger.info("Ticket loaded from user input. Ticket content: %s", self.state.ticket.content) # TODO: Remove this line in PII protection phase, as it may contain sensitive information
        elif self.state.status == "open":
            print("This is an open ticket. Loading ticket from memory.")
            logger.info("Ticket loaded from memory. Ticket ID: %s", self.state.ticket.ticket_id)
            logger.info("Ticket loaded from memory. Ticket content: %s", self.state.ticket.content) # TODO: Remove this line in PII protection phase, as it may contain sensitive information


    @router(load_ticket)
    def categorize_ticket(self):
        """Categorize the ticket based on its content"""
        print("Categorizing ticket...")

        llm = LLM(model="gpt-4o-mini",)
        prompt = ROUTER_PROMPT.format(ticket_content=self.state.ticket.content)
        decision = llm.call(messages=prompt)
        print("Decision:", decision)

        if "FAQ" in decision:
            self.state.category = "FAQ"
            logger.info("Ticket categorized as FAQ.")
            return "FAQ"
        elif "ESCALATE" in decision:
            self.state.category = "ESCALATE"
            logger.info("Ticket categorized as ESCALATE.")
            return "ESCALATE"
        elif "INVESTIGATE" in decision:
            self.state.category = "INVESTIGATE"
            logger.info("Ticket categorized as INVESTIGATE.")
            return "INVESTIGATE"
        else:
            logger.error("Invalid category decision: %s", decision)
            raise ValueError(f"Invalid category decision: {decision}")
        
    @listen("FAQ")
    def answer_faq(self):
        # TODO: To be completed
        print("Answering FAQ...")
        self.state.reply = "This is a placeholder answer for the FAQ category."

    @listen("ESCALATE")
    def escalate_ticket(self):
        # TODO: To be completed
        print("Escalating ticket...")
        self.state.reply = "This ticket has been escalated to a human agent."

    @listen("INVESTIGATE")
    def run_support_crew(self):
        # TODO: To be completed
        print("Investigating ticket...")
        self.state.reply = "This ticket requires further investigation by the support crew."

        # crew.kickoff(inputs={"ticket_id": ..., "content": self.state.ticket.content})

    @listen(or_(answer_faq, escalate_ticket, run_support_crew))
    def finalize(self):
        print("Finalizing ticket processing...")
        print("Ticket UUID:", self.state.id)
        print("Ticket ID:", self.state.ticket.ticket_id)
        print("Ticket category:", self.state.category)
        print("Ticket reply:", self.state.reply)
        logger.info("Ticket processing finalized. Ticket UUID: %s, Ticket ID: %s, Category: %s", self.state.id, self.state.ticket.ticket_id, self.state.category)
        # TODO: summary



def plot():
    flow = SupportTriageFlow()  # Replace with your actual Flow class name
    flow.plot()

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
                # , "id": "accfd40e-6435-4759-9ec8-b998cb373e75" # Tip: It updates the state of the flow with the given ID, if it exists.
            }
            #, restore_from_state_id='accfd40e-6435-4759-9ec8-b998cb373e75' # Tip: It forks the existing flow's state from the given ID, and creates a new flow with a new ID. This keep records of all changes.
            )
    except TicketParseError as e:
        logger.error("Invalid ticket: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    kickoff()
