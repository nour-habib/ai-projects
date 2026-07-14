import logging
import os
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

from ai.models.models import QueryType, Intent

load_dotenv()


class ResponseObject(BaseModel):
    original_query: str
    query_type: QueryType
    intent: Intent
    customer_id: int


PROMPT = """
    You are responsible for classifying a user query into 1 of 3 categories: Positive, Negative or Query.
    Also classify the intent of the query into these categories:   
    
    PRAISE = "praise"
    COMPLAIN = "complaint"
    TICKET_STATUS = "ticket_status"
    GENERAL_QUESTION = "general_question"

    DEFINITIONS:
    Positive: Positive sentiment — praise, thanks, or satisfaction.
    Negative: Negative sentiment — a complaint or a report of a problem. This INCLUDES
              complaints phrased as questions (e.g. "Why hasn't my card arrived yet?").
    Query: A neutral request for information or a ticket status, where the user is NOT
           complaining — e.g. how something works, general info, or an existing ticket's status.

    IMPORTANT: Classify by INTENT, not grammar. A question that expresses frustration or
    reports a problem is Negative (a complaint), NOT a Query. Only use Query when the user
    is genuinely seeking information and is not upset.

    EXAMPLES:
    - Thank you for sending my credit card early.
        Return {original_query = Thank you for sending my credit card early.
                query_type = QueryType.POSITIVE
                intent = Intent.PRAISE
        }

    - There is an issue with my login.
     Return {original_query = There is an issue with my login.
                query_type = QueryType.NEGATIVE
                intent = Intent.COMPLAINT
        }
    - How do I create a new checking account?
    Return {original_query = How do I create a new checking account?
                query_type = QueryType.QUERY
                intent = Intent.GENERAL_QUESTION
        }

    - Why hasn't my debit card arrived yet?
    Return {original_query = Why hasn't my debit card arrived yet?
                query_type = QueryType.NEGATIVE
                intent = Intent.COMPLAINT
        }
"""


class ClassifierAgent():
    def __init__(self):
        self.model = os.getenv("CLASSIFIER_MODEL", "gpt-4o")
        self.client = OpenAI()

    def classify(self, input: str) -> ResponseObject:
        try:
            response = self.client.responses.parse(
                model=self.model,
                instructions=PROMPT,
                input=input,
                text_format=ResponseObject,
            )
            return response.output_parsed
        except Exception as e:
            logging.error(f"Classification error: {e}")
            raise
