import logging
import os
from dotenv import load_dotenv
from openai import OpenAI
from ai.models.models import Feedback, CustomerInput, QueryType
from ai.agents.classifier_agent import ResponseObject
from ai.tools.tickets import open_ticket

load_dotenv()

PROMPT = """
    Return the appropriate response based on the customer's sentiment. Choose the response from
    the RESPONSES and return a Feedback object containing the text string only.

    RESPONSES: dict[Sentiment, list[str]] = {
    Sentiment.POSITIVE: [
        "Thank you for your kind words, {name}! We're delighted to assist you.",
        "We really appreciate your feedback, {name}. So glad we could help!",
    ],
    Sentiment.NEGATIVE: [
        "We apologize for the inconvenience. A new ticket has been generated, and our team will follow up shortly.",
        "Sorry to hear that. We've opened a ticket and we will look into it promptly.",
    ],
    Sentiment.NEUTRAL: [
        "Thanks for reaching out. Let us know if there's anything we can help with.",
    ],
}
"""

class FeedbackAgent():
    def __init__(self):
        self.model = os.getenv("FEEDBACK_MODEL", "gpt-4o")
        self.client = OpenAI()

    def process_feedback(self, response_object: ResponseObject) -> str:
        if response_object.query_type == QueryType.POSITIVE:
            feedback = self._generate_positive_feedback(response_object)
            return feedback.response.value
        # NEGATIVE
        ticket = open_ticket(response_object.customer_id, response_object.original_query)
        return (
            f"We apologize for the inconvenience. A new ticket #{ticket.ticket_number} "
            "has been generated, and our team will follow up shortly."
        )

    def _generate_positive_feedback(self, response_object: ResponseObject) -> Feedback:
        response = self.client.responses.parse(
            model=self.model,
            instructions=PROMPT,
            input=response_object.original_query,
            text_format=Feedback
        )
        return response.output_parsed
        
