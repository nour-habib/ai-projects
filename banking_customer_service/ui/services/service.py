"""UI-facing service layer.

Thin boundary between the Streamlit UI and the agent orchestrator. The UI calls
`process_query()` and never imports the agents directly. The orchestrator is
imported lazily inside the function so that an in-progress / non-compiling agent
module can't crash the whole UI on load.
"""


def process_query(raw_input: str) -> str:
    """Send a raw chatbot message to the orchestrator and return its reply.

    Falls back to a friendly message while the agent layer is still being built.
    """
    text = (raw_input or "").strip()
    if not text:
        return "Please type a message."

    try:
        from ai.agents.orchestrator import Orchestrator
        from ai.models.models import CustomerInput

        orchestrator = Orchestrator()
        # customer_id is a placeholder until the UI passes the selected customer.
        customer_input = CustomerInput(customer_id=0, query=text)
        reply = orchestrator.process_user_input(customer_input)
        return reply if reply else "Sorry, I couldn't generate a response."
    except Exception as exc:  # agent layer not ready yet
        return f"⚠️ Agent routing isn't available yet ({type(exc).__name__})."
