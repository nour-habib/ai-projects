from dataclasses import dataclass
from typing import Optional


@dataclass
class Ticket:
    id: int
    customer_id: int
    ticket_number: Optional[str] = None
    message: Optional[str] = None
    status: str = "Unresolved"
    created_at: Optional[str] = None