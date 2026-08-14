mcp.server.fastmcp import FastMCP
from backend.api import get_ticket, get_tickets, search_tickets, update_ticket_status, reassign_ticket
from models.models import Ticket


mcp = FastMCP("tickets")

"""Fetch ticket tool""""
@mcp.tool(
    name="find_ticket",
    description="Gets a ticket by its ID",
    tags=["ticket", "id"],
    meta={"version": "1.0.0"}

)
def fetch_ticket(ticket_id: int) -> Ticket | None:
    try:
        ticket = get_ticket(ticket_id)
        if ticket is None:
            return f"Ticket {ticket_id} not found."
        return ticket
    except Exception as e:
        return f"Error retrieving tickets {ticket_id}: {e}."


"""Fetch all tickets tool""""
@mcp.tool()
def fetch_all_tickets() -> list[Ticket] | None:
    try:
        tickets = get_tickets()
        if tickets is None:
            return "No tickets found."
        return tickets
    except Exception as e:
        return f"Error retrieving tickets: {e}."


"""Search tickets tool""""
@mcp.tool()
def search(status: str, priority: str, date_from: str, date_to: str, assignee: str) -> Ticket | None:
    try:
        tickets = search_tickets(status, priority, date_from, date_to, assignee)
        if tickets is None:
            return "No tickets found."
        return tickets
    except Exception as e:
        return f"Error searching tickets: {e}."

@mcp.tool()
def update_status(ticket_id: int, status: str) -> Ticket | None:
    try:
        updated_ticket = update_ticket_status(ticket_id, status)
        if updated_ticket is None:
            return f"Ticket {ticket_id} not found."
        return updated_ticket
    except Exception as e:
        return f"Error updating ticket {ticket_id}: {e}."


@mcp.tool()
def reassign(ticket_id: int, assignee: str) -> Ticket | None:
    try:
        ticket = reassign_ticket(ticket_id, assignee)
        if ticket is None:
            return f"Ticket {ticket_id} not found."
        return ticket
    except Exception as e:
        return f"Error reassigning ticket {ticket_id}: {e}."

if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=8000)


