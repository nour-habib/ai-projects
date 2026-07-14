from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class CustomerInput(BaseModel):
    customer_id: int
    ticket_number: Optional[int] = None
    query: str

class PositiveResponse(str, Enum):
    R1 = "Thank you for your kind words, {name}! We're delighted to assist you."
    R2 = "We really appreciate your feedback, {name}. So glad we could help!"

class Feedback(BaseModel):
    response: PositiveResponse

class Query(BaseModel):
    original_query: str
    sentiment: str
    customer_id: int

class Response(BaseModel):
    customer_id: str
    ticket_number: str
    status: str
    original_query: str

class QueryType(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    QUERY = "query"


class Intent(str, Enum):
    PRAISE = "praise"
    COMPLAINT = "complaint"
    TICKET_STATUS = "ticket_status"
    GENERAL_QUESTION = "general_question"