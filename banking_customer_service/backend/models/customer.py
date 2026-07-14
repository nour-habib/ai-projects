from dataclasses import dataclass
from typing import Optional

@dataclass
class Customer:
    id: int
    name: str
    address: str
    dob: str
    created_at: Optional[str] = None