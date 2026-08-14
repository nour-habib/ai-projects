
from connect import db_params
import psycopg

def get_connection():
    return psycopg.connect(**db_params)

def get_tickets():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM tickets;")
            return cur.fetchall()


def search_tickets(status: str, priority: str, date_from: str, date_to: str, assignee: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM tickets WHERE status = %s AND priority = %s AND created_at >= %s AND created_at <= %s AND assignee = %s;", (status, priority, date_from, date_to, assignee))
            return cur.fetchall()

def get_ticket(ticket_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM tickets WHERE id = %s;", (ticket_id,))
            return cur.fetchone()


def update_ticket_status(ticket_id: int, status: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE tickets SET status = %s WHERE id = %s;", (status, ticket_id))
            conn.commit()
            return cur.rowcount


def reassign_ticket(ticket_id: int, assignee: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE tickets SET assignee = %s WHERE id = %s;", (assignee, ticket_id))
            conn.commit()
            return cur.rowcount
