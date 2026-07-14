from langchain_core.tools import tool

from ai.services.medline import search_medline
from ai.services import appointments
from ai.agents.tools.rag.retriever import search_clinic_docs


@tool
def get_medline_tool(query: str):
    """Look up health/disease information from MedlinePlus."""
    return search_medline(query)


@tool
def list_patient_appointments(patient_id: str):
    """List a patient's booked appointments, including their appointment ids."""
    return appointments.list_appointments(patient_id=patient_id)


@tool
def search_appointment(doctor_id: str, date: str):
    """Find open appointment slots for a doctor on a YYYY-MM-DD date."""
    return appointments.find_slots(doctor_id, date)


@tool
def create_appointment(patient_id: str, doctor_id: str, start_ts: str, reason: str):
    """Book an appointment for a patient with a doctor at an ISO start time."""
    return appointments.book(patient_id, doctor_id, start_ts, reason)


@tool
def cancel_appointment(appointment_id: str):
    """Cancel an existing appointment by id."""
    return appointments.cancel(appointment_id)


@tool
def clinic_faq(query: str):
    """Search the clinic documentation to answer questions about parking, insurance, hours, location etc via RAG pipeline"""
    return search_clinic_docs(query)


tools = [
    get_medline_tool,
    list_patient_appointments,
    search_appointment,
    create_appointment,
    cancel_appointment,
    clinic_faq
]
