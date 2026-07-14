import os

from dotenv import load_dotenv

# Re-exported from the shared service so `from apiService import handle_query`
# (used by the UI) continues to work without depending on UI internals.
from ai.services.medline import handle_query, search_medline  # noqa: F401
from ai.agents.router import build_router

load_dotenv()

ai_router = build_router()


def _build_trace(messages: list) -> list[dict]:
    """Extract the agent's planning/memory steps from the run's message list.

    Returns ordered steps: each tool the agent decided to call (with its args)
    and each tool result it observed, for display in the UI.
    """
    trace = []
    for m in messages:
        for call in getattr(m, "tool_calls", None) or []:
            trace.append({"kind": "tool_call", "name": call["name"], "args": call["args"]})
        if type(m).__name__ == "ToolMessage":
            trace.append(
                {"kind": "tool_result", "name": getattr(m, "name", ""), "content": str(m.content)}
            )
    return trace


def run_agent(messages: list[dict], patient: dict | None = None) -> dict:
    """Run the LangGraph agent and return {"reply", "trace"}.

    `messages` is the running history: [{"role": "user"|"assistant", "content": str}].
    `patient` is the currently selected patient, given to the agent as context.
    `trace` is the planning/tool-call breakdown for display.
    """
    from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

    converted: list = []
    if patient:
        converted.append(
            SystemMessage(
                content=(
                    f"The current patient is {patient['name']} "
                    f"with patient_id {patient['id']}. Use this id for appointment actions."
                )
            )
        )
    converted += [
        (HumanMessage if m["role"] == "user" else AIMessage)(content=m["content"])
        for m in messages
    ]

    try:
        result = ai_router.invoke({"messages": converted})
        return {"reply": result["messages"][-1].content, "trace": _build_trace(result["messages"])}
    except Exception as exc:  # network / auth / quota
        return {"reply": f"Sorry, I couldn't respond right now ({exc}).", "trace": []}


def chat_reply(messages: list[dict], patient: dict | None = None) -> str:
    """Convenience wrapper returning just the agent's reply text."""
    return run_agent(messages, patient)["reply"]


#Appointment methods

from backend.schedule import Scheduler
from backend import repository


def find_appointment_slots(doctor_id: str, date: str):
    return Scheduler().find_slots(doctor_id, date)


def search_appointments(patient_id: str | None = None, doctor_id: str | None = None):
    return repository.list_appointments(patient_id, doctor_id)


def book_appointment(patient_id: str, doctor_id: str, start_ts: str, reason: str | None = None):
    return Scheduler().book(patient_id, doctor_id, start_ts, reason)


def cancel_appointment(appointment_id: str):
    return Scheduler().cancel(appointment_id)



def search_patient(patient: str):
    return repository.search_patient(patient)
