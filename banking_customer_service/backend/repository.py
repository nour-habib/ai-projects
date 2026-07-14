import random
from backend.db import get_connection
from backend.models import Account, Customer, Ticket
from typing import Optional


#Customers
def create_customer(name: str, address: str, dob: str) -> Customer:
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO customers (name, address, dob)  VALUES (?, ?, ?)",
            (name, address, dob),
        )
        new_id = cursor.lastrowid
    return get_customer(new_id)


#Leave this as an example

# def get_customer(customer_id: int) -> Optional[Customer]:
#     with get_connection() as conn:
#         row = conn.execute(
#             "SELECT * FROM CUSTOMERS WHERE id= ?",
#             (customer_id,),
#             ).fetchone()
#         if row is None:
#             return None
#         return Customer(
#             id=row["id"],
#             name=row["name"],
#             address=row["address"],
#             dob=row["dob"],
#             created_at=row["created_at"],
#         )


#DRY

def get_customer(customer_id: int) -> Optional[Customer]:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM customers WHERE id= ?", (customer_id,)).fetchone()
    if row is None:
        return None
    return _row_to_customer(row)

def update_customer(customer_id: int, name: str, address: str, dob: str) -> Optional[Customer]:
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE customers
                SET name= :name, address = :address, dob = :dob
                WHERE id = :id
            """,
            {"id": customer_id, "name": name, "address": address, "dob": dob},
        )
    return get_customer(customer_id)

def delete_customer(customer_id: int) -> bool:
    with get_connection() as conn:
       cursor = conn.execute("DELETE FROM customers WHERE id= ?", (customer_id,))
       return cursor.rowcount > 0
        
def _row_to_customer(row) -> Customer:
    return Customer(
        id=row["id"],
        name=row["name"],
        address=row["address"],
        dob=row["dob"],
        created_at=row["created_at"]
    )


#Accounts
def create_account(customer_id: str, account_type: str) -> Account:
    pass

def get_account(ticket_id: str, customer_id: str) -> Account:
    pass

def update_account() -> Account:
    pass

def delete_account() -> None:
    pass


#Tickets
def create_ticket(customer_id: int, message: str, status: str = "Unresolved") -> Ticket:
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO tickets (customer_id, message, status) VALUES (?, ?, ?)",
            (customer_id, message, status),
        )
        ticket_id = cursor.lastrowid
        ticket_number = generate_ticket_number(ticket_id)
        conn.execute(
            "UPDATE tickets SET ticket_number = ? WHERE id = ?",
            (ticket_number, ticket_id),
        )
    return get_ticket(ticket_id)

def get_ticket(id: Optional[int] = None, ticket_number: Optional[str] = None) -> Optional[Ticket]:
    if id is not None:
        query, param = "SELECT * FROM tickets WHERE id = ?", (id,)
    elif ticket_number is not None:
        query, param = "SELECT * FROM tickets WHERE ticket_number = ?", (ticket_number,)
    else:
        raise ValueError("Provide either id or ticket_number")
    with get_connection() as conn:
        row = conn.execute(query, param).fetchone()
    return _row_to_ticket(row) if row else None

def _row_to_ticket(row) -> Ticket:
    return Ticket(
        id=row["id"],
        ticket_number=row["ticket_number"],
        customer_id=row["customer_id"],
        message=row["message"],
        status=row["status"],
        created_at=row["created_at"],
    )

def update_ticket(id: int, customer_id: int, status: str) -> Optional[Ticket]:
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE tickets
                SET customer_id = :customer_id, status = :status
                WHERE id = :id
            """,
            {"id": id, "customer_id": customer_id, "status": status},
        )
    return get_ticket(id)

def delete_ticket(id: int) -> bool:
      with get_connection() as conn:
       cursor = conn.execute("DELETE FROM tickets WHERE id= ?", (id,))
       return cursor.rowcount > 0

def generate_ticket_number(ticket_id: int) -> str:
    """6-digit ticket number: 3 random digits + the zero-padded id (fixed width).

    The id occupies the last 3 digits, so two different ids always differ ->
    guaranteed unique, no collision retry. (Caps at id 999.)
    """
    random_part = random.randint(0, 999)
    return f"{random_part:03d}{ticket_id:03d}"  # e.g. 047 + 005 -> "047005"
