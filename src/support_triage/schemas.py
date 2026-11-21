from pydantic import BaseModel

class Ticket(BaseModel):
    ticket_number: int 
    content: str
    

