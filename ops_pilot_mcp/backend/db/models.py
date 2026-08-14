from pydantic import BaseModel

class Ticket(BaseModel):
    id: int
    title: str
    description: str
    status: str
    priority: str
    assignee: str
    created_at: str
    updated_at: str
