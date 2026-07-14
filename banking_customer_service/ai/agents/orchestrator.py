import logging
import os
from dotenv import load_dotenv

from ai.agents.classifier_agent import ClassifierAgent, ResponseObject
from ai.agents.feedback_agent import FeedbackAgent
from ai.agents.query_agent import QueryAgent
from ai.tools.query_parser import QueryParser
from ai.models.models import CustomerInput, QueryType

load_dotenv()
class Orchestrator():
    def __init__(self):
        self.classifier_agent = ClassifierAgent()
        self.feedback_agent = FeedbackAgent()
        self.query_agent = QueryAgent()
        self.parser = QueryParser()

    def process_user_input(self, customer_input: CustomerInput) -> str:
        sanitized_text = self.parser.clean(customer_input.query)

        response_object = self.classifier_agent.classify(sanitized_text)

        if response_object.query_type == QueryType.QUERY:
            return self.query_agent.process_query(response_object)
        return self.feedback_agent.process_feedback(response_object)