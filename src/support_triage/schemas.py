from pydantic import BaseModel

class Ticket(BaseModel):
    ticket_id: int
    content: str
    