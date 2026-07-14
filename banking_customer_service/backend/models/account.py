from dataclasses import dataclass
from typing import Optional

@dataclass
class Account:
    id: int
    customer_id: int
    account_type: str
    balance: float = 0.0
    opened_at: Optional[str] = None



