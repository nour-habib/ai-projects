"""Ticket methods as tools"""
from backend import repository
from typing import Optional
from backend.models import Ticket


def open_ticket(customer_id: int, message: str = None) -> Ticket:
    return repository.create_ticket(customer_id, message)

def update_ticket(id: int, status: str) -> Optional[Ticket]:
    return repository.update_ticket(id,status)

def get_ticket(id: int | None = None, ticket_number: str | None = None) -> Optional[Ticket]:
    if(id):
        return repository.get_ticket(id)
    elif ticket_number:
        return repository.get_ticket(ticket_number)