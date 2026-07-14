import logging
import os
from dotenv import load_dotenv
from openai import OpenAI
from ai.agents.classifier_agent import ResponseObject
from ai.models.models import Intent
from ai.tools.tickets import get_ticket
from ai.tools.query_parser import QueryParser
from ai.rag.rag import RAGApi

load_dotenv()


class QueryAgent():
    def __init__(self):
        self.model = os.getenv("QUERY_MODEL", "gpt-4o")
        self.client = OpenAI()
        self.RAGApi = RAGApi()
        self.parser = QueryParser()

    def process_query(self, response_object: ResponseObject) -> str:
        if response_object.intent == Intent.TICKET_STATUS:
            ticket_number = self.parser.extract_ticket_number(response_object.original_query)
            if ticket_number is None:
                return "Could you share your ticket number so I can look it up?"
            ticket = get_ticket(ticket_number=ticket_number)
            if ticket is None:
                return f"I couldn't find a ticket with number #{ticket_number}."
            return f"Your ticket #{ticket.ticket_number} is currently marked as: {ticket.status}."

        # GENERAL_QUESTION -> RAG
        docs = self.RAGApi.retrieval(response_object.original_query, 3)
        if not docs:
            return "I don't have information on that."
        return self._answer(response_object.original_query, docs)

    def _answer(self, query: str, docs: list[str]) -> str:
        context = "\n\n".join(docs)
        response = self.client.responses.create(
            model=self.model,
            instructions=(
                "Answer the customer's question using ONLY the context below. "
                "Be concise. If the context doesn't cover it, say you don't have that info.\n\n"
                f"CONTEXT:\n{context}"
            ),
            input=query,
        )
        return response.output_text
